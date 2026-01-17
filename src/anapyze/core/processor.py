import nibabel as nib
import numpy as np
import subprocess
import os
import logging
from os.path import join, exists
from concurrent.futures import ThreadPoolExecutor
from typing import Union, Tuple, List, Dict, Optional

from anapyze.io import spm
from anapyze.io import cat12
from anapyze.config import config

logger = logging.getLogger(__name__)


def run_matlab_command(mfile: str, matlab_cmd: Optional[str] = None) -> None:
    """
    Executes a MATLAB script (.m file) using the configured MATLAB command.

    Args:
        mfile: Path to the .m file to execute.
        matlab_cmd: Optional override for the MATLAB command. If None, uses config.matlab_cmd.

    Raises:
        RuntimeError: If the MATLAB command fails.
    """
    if matlab_cmd is None:
        matlab_cmd = config.matlab_cmd

    mfile_path, mfile_name = os.path.split(mfile)
    
    # Remove extension if present for the batch command
    script_name = os.path.splitext(mfile_name)[0]

    command = f"{matlab_cmd} -nosplash -sd {mfile_path} -batch {script_name}"
    
    logger.info(f"Running MATLAB command: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            check=True
        )
        logger.info(f"Successfully executed {mfile_name}")
        if result.stdout:
            logger.debug(f"MATLAB Output: {result.stdout}")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"MATLAB execution failed: {e.stderr}")
        raise RuntimeError(f"MATLAB execution failed: {e.stderr}") from e

def intensity_normalize_pet_histogram(input_image, template, mask):
    """Normalizes an image using the mode of an intensity histogram.
    More info at: https://pubmed.ncbi.nlm.nih.gov/32771619/

    :param input_image: the path to the input image
    :param template: the path to the template image
    :param mask: the path to the mask image
    :param output: the path to the output image
    :return: the normalization value used to scale the input image
    """

    fdg_data = input_image.get_fdata()
    template_data = template.get_fdata()
    mask_data = mask.get_fdata()

    if len(mask.shape) == 4:
        mask_data = mask_data[:, :, :, 0]

    indx = np.where(mask_data == 1)
    mean_template = np.mean(template_data[indx])
    mean_fdg = np.mean(fdg_data[indx])

    fdg_data = fdg_data * (mean_template / mean_fdg)

    division = template_data[indx] / fdg_data[indx]
    values, bins = np.histogram(division, 200, range=(0.5, 2))
    amax = np.amax(values)
    indx = np.where(values == amax)
    norm_value = float(bins[indx][0])
    norm_data = fdg_data * norm_value

    norm_img = nib.Nifti1Image(norm_data, input_image.affine, input_image.header)

    return norm_value, norm_img

def intensity_normalize_pet_ref_region(input_image, ref_region_img, ref_region_val=1):
    """Normalizes an image using a reference region.
    :param input_image: the path to the input image
    :param ref_region_img: the path to the reference region image
    :param ref_region_val:
    :return: the normalization value used to scale the input image
    """
    ref_data = ref_region_img.get_fdata()

    if len(ref_data) == 4:
        ref_data = ref_data[:, :, :, 0]

    ref_vox = np.where(ref_data == ref_region_val)
    img_data = input_image.get_fdata()

    if len(img_data.shape) == 4:
        img_data = img_data[:, :, :, 0]

    ref_value = np.mean(img_data[ref_vox])
    normalized_data = img_data / ref_value

    normalized_img = nib.Nifti1Image(normalized_data, input_image.affine, input_image.header)

    return normalized_img, ref_value

def histogram_matching(reference_img, input_img):
    """Matches the histogram of an input image to a reference image.

    :param reference_nii: the path to the reference image
    :param input_nii: the path to the input image
    :param output_nii: the path to the output image
    :return: None
    """

    nt_data = reference_img.get_fdata()
    pt_data = input_img.get_fdata()

    # Stores the image data shape that will be used later
    old_shape = pt_data.shape

    # Converts the data arrays to single dimension and normalizes by the maximum
    nt_data_array = nt_data.ravel()
    pt_data_array = pt_data.ravel()

    # get the set of unique pixel values and their corresponding indices and counts
    s_values, bin_idx, s_counts = np.unique(
        pt_data_array, return_inverse=True, return_counts=True
    )
    t_values, t_counts = np.unique(nt_data_array, return_counts=True)

    # take the cumsum of the counts and normalize by the number of pixels to
    # get the empirical cumulative distribution functions for the source and
    # template images (maps pixel value --> quantile)
    s_quantiles = np.cumsum(s_counts).astype(np.float64)
    s_quantiles /= s_quantiles[-1]
    t_quantiles = np.cumsum(t_counts).astype(np.float64)
    t_quantiles /= t_quantiles[-1]

    # interpolate linearly to find the pixel values in the template image
    # that correspond most closely to the quantiles in the source image
    interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)

    # Reshapes the corresponding values to the indexes and reshapes the array to input
    final_image_data = interp_t_values[bin_idx].reshape(old_shape)

    final_image = nib.Nifti1Image(final_image_data, input_img.affine, input_img.header)

    return final_image

def logpow_histogram_matching(reference_img, input_img, alpha: int = 1, beta: int = 3):
    """Matches the histogram of an input image to a reference image using a log-power transformation.
    More info: https://doi.org/10.1117/1.JEI.23.6.063017

    :param reference_nii: the path to the reference image
    :param input_nii: the path to the input image
    :param output_nii: the path to the output image
    :param alpha: the additive constant for the log transformation, defaults to 1
    :param beta: the power exponent for the log transformation, defaults to 3
    """
    nt_data = reference_img.get_fdata()
    pt_data = input_img.get_fdata()

    # Stores the image data shape that will be used later
    old_shape = pt_data.shape

    # Converts the data arrays to single dimension and normalizes by the maximum
    nt_data_array = nt_data.ravel()
    pt_data_array = pt_data.ravel()

    # get the set of unique pixel values and their corresponding indices and counts
    s_values, bin_idx, s_counts = np.unique(pt_data_array, return_inverse=True, return_counts=True)
    t_values, t_counts = np.unique(nt_data_array, return_counts=True)

    s_counts = np.power(np.log10(s_counts + alpha), beta)
    t_counts = np.power(np.log10(t_counts + alpha), beta)

    # take the cumsum of the counts and normalize by the number of pixels to
    # get the empirical cumulative distribution functions for the source and
    # template images (maps pixel value --> quantile)
    s_quantiles = np.cumsum(s_counts).astype(np.float64)
    s_quantiles /= s_quantiles[-1]
    t_quantiles = np.cumsum(t_counts).astype(np.float64)
    t_quantiles /= t_quantiles[-1]

    # interpolate linearly to find the pixel values in the template image
    # that correspond most closely to the quantiles in the source image
    interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)

    # Reshapes the corresponding values to the indexes and reshapes the array to input
    final_image_data = interp_t_values[bin_idx].reshape(old_shape)
    # final_image_data[indx] = 0

    final_image = nib.Nifti1Image(final_image_data, input_img.affine, input_img.header)

    return final_image

def coregister_spm(
    reference_nii: str, 
    input_nii: str, 
    mfile_name: str, 
    spm_path: Optional[str] = None
) -> None:
    """Performs coregistration between two images using SPM."""
    
    if spm_path is None:
        spm_path = config.spm_path

    if spm_path is None:
         raise ValueError("SPM path is not configured.")

    spm.generate_mfile_coregister(spm_path, mfile_name,
                                  reference_nii, input_nii)

    run_matlab_command(mfile_name)

def old_normalize_spm(
    images_to_norm: Union[str, List[str]], 
    template_image: str, 
    mfile_name: str, 
    spm_path: Optional[str] = None
) -> None:

    if spm_path is None:
        spm_path = config.spm_path
        
    if spm_path is None:
         raise ValueError("SPM path is not configured.")

    spm.generate_mfile_old_normalize(spm_path, mfile_name, images_to_norm, template_image)

    run_matlab_command(mfile_name)

def new_normalize_spm(
    images_to_norm: Union[str, List[str]], 
    mfile_name: str, 
    template_image: Optional[str] = None, 
    spm_path: Optional[str] = None
) -> None:

    if spm_path is None:
        spm_path = config.spm_path
        
    if spm_path is None:
         raise ValueError("SPM path is not configured.")

    if template_image is None:
        template_image = join(spm_path, 'tpm', 'TPM.nii')

    spm.generate_mfile_new_normalize(spm_path, mfile_name, template_image, images_to_norm)

    run_matlab_command(mfile_name)

def old_deformations(
    images_to_deform: List[str], 
    base_image: str, 
    def_matrix: str, 
    interpolation: int, 
    mfile_name: str, 
    spm_path: Optional[str] = None
) -> None:

    if spm_path is None:
        spm_path = config.spm_path
        
    if spm_path is None:
         raise ValueError("SPM path is not configured.")

    spm.generate_mfile_old_deformations(spm_path, mfile_name, def_matrix, base_image, images_to_deform, interpolation)
    run_matlab_command(mfile_name)

def new_deformations(
    images_to_deform: List[str],
    def_matrix: str,
    interpolation: int,
    mfile_name: str, 
    spm_path: Optional[str] = None
) -> None:

    if spm_path is None:
        spm_path = config.spm_path
        
    if spm_path is None:
         raise ValueError("SPM path is not configured.")

    spm.generate_mfile_new_deformations(spm_path, mfile_name, def_matrix, images_to_deform, interpolation)
    run_matlab_command(mfile_name)

def smooth_images_spm(
    images_to_smooth: List[str], 
    smoothing: List[float], 
    mfile_name: str, 
    spm_path: Optional[str] = None
) -> None:

    if spm_path is None:
        spm_path = config.spm_path
        
    if spm_path is None:
         raise ValueError("SPM path is not configured.")

    spm.generate_mfile_smooth_imgs(spm_path, mfile_name, images_to_smooth, smoothing)
    run_matlab_command(mfile_name)

def cat12_segmentation_crossec(
    images_to_segment: List[str], 
    mfile_name: str, 
    template_tpm: Optional[str] = None, 
    template_volumes: Optional[str] = None,
    output_vox_size: float = 1.0, 
    bounding_box: str = "cat12", 
    surface_processing: int = 0,
    spm_path: Optional[str] = None
) -> None:

    if spm_path is None:
        spm_path = config.spm_path
        
    if spm_path is None:
         raise ValueError("SPM path is not configured.")

    if not template_tpm:
        template_tpm = join(spm_path, 'tpm', 'TPM.nii')

    if not template_volumes:
        template_volumes = join(spm_path, 'toolbox', 'cat12', 'templates_MNI152NLin2009cAsym', 'Template_0_GS.nii')

    cat12.generate_mfile_cat12_segmentation_crossec(spm_path, mfile_name,images_to_segment,
                                                    template_tpm,template_volumes,
                                                    output_vox_size = output_vox_size, bounding_box = bounding_box,
                                                    surface_processing = surface_processing)

    run_matlab_command(mfile_name)

def cat12_segmentation_longit(
    images_to_segment: List[str], 
    mfile_name: str, 
    template_tpm: Optional[str] = None, 
    template_volumes: Optional[str] = None,
    output_vox_size: float = 1.5, 
    bounding_box: str = "cat12", 
    surface_processing: int = 0,
    spm_path: Optional[str] = None
) -> None:

    if spm_path is None:
        spm_path = config.spm_path
        
    if spm_path is None:
         raise ValueError("SPM path is not configured.")

    if not template_tpm:
        template_tpm = join(spm_path, 'tpm', 'TPM.nii')

    if not template_volumes:
        template_volumes = join(spm_path, 'toolbox', 'cat12', 'templates_MNI152NLin2009cAsym', 'Template_0_GS.nii')

    cat12.generate_mfile_cat12_segmentation_longit(spm_path, mfile_name,images_to_segment,
                                                    template_tpm,template_volumes,
                                                    output_vox_size = output_vox_size, bounding_box = bounding_box,
                                                    surface_processing = surface_processing)

    run_matlab_command(mfile_name)

def recon_all_freesurfer(t1_nii: str, t2_nii: Optional[str] = None) -> None:

    freesurfer_home = config.freesurfer_home
    if not freesurfer_home and "FREESURFER_HOME" not in os.environ:
         raise RuntimeError("FREESURFER_HOME environment variable not set and not in config.")

    #directory containing the t1_nii file
    pat_dir = os.path.split(t1_nii)[0]

    if exists(t1_nii):
        cmd = f"recon-all -sd {pat_dir} -i {t1_nii} -s FS_out -all"
        logger.info(f"Running FreeSurfer command: {cmd}")
        os.system(cmd)
    
    if t2_nii and exists(t1_nii) and exists(t2_nii):
        # TODO : hippocampal subfields
        pass

def recon_all_freesurfer_whole_cohort(cohort_dir: str, pats: Dict[str, Tuple[str, str]], n_parallel: int = 2) -> None:

    freesurfer_home = config.freesurfer_home
    if not freesurfer_home and "FREESURFER_HOME" not in os.environ:
         raise RuntimeError("FREESURFER_HOME environment variable not set and not in config.")

    def process_patient(item: tuple):

        pat, (t1_name, t2_name) = item
        pat_dir = join(cohort_dir, pat)
        t1_nii = join(cohort_dir, pat, t1_name)
        t2_nii = join(cohort_dir, pat, t2_name)

        if exists(t1_nii):
            cmd = f"recon-all -sd {pat_dir} -i {t1_nii} -s FS_out -all"
            logger.info(f"Running FreeSurfer command for {pat}: {cmd}")
            os.system(cmd)
            
        if t2_nii and exists(t1_nii) and exists(t2_nii):
            # TODO : hippocampal subfields
            pass

    with ThreadPoolExecutor(max_workers = n_parallel) as executor:
        executor.map(process_patient, pats.items())
        return None

    # TODO: Similar functions for SAMSEG and Synthseg

def synthstrip_skull_striping_freesurfer(img_to_strip: str, out_: Optional[str] = None, includes_csf: bool = True) -> None:

    freesurfer_home = config.freesurfer_home
    if not freesurfer_home and "FREESURFER_HOME" not in os.environ:
         raise RuntimeError("FREESURFER_HOME environment variable not set and not in config.")

    if not out_:
        out_path, out_name = os.path.split(img_to_strip)
        out_ = join(out_path, 'skull_strip_' + out_name)

    csf_flag = ''
    if not includes_csf:
        csf_flag = '--no-csf'

    if exists(img_to_strip):
        cmd = f"mri_synthstrip -i {img_to_strip} -o {out_} {csf_flag}"
        logger.info(f"Running SynthStrip command: {cmd}")
        os.system(cmd)

    else:
        raise FileNotFoundError(f"Input image does not exist: {img_to_strip}")