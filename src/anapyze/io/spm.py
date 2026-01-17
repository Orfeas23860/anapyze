import os
from os.path import exists, join
from typing import List, Union, Optional
from anapyze.config import config

parent_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = join(parent_dir, 'templates')

default_bounding_box = [-84, -120, -72, 84, 84, 96]  # CAT12 Default

def generate_mfile_coregister(
    spm_path: str, 
    mfile_name: str,
    reference_image: str, 
    source_image: str
) -> None:

    design_type = "matlabbatch{1}.spm.spatial.coreg.estwrite."

    with open(mfile_name, "w") as new_spm:
        new_spm.write(f"addpath('{spm_path}')\n")
        new_spm.write(design_type + "ref = {'" + reference_image + ",1'};\n")
        new_spm.write(design_type + "source = {'" + source_image + ",1'};\n")
        new_spm.write(design_type + "other = {''};\n")
        new_spm.write(design_type + "eoptions.cost_fun = 'nmi';\n")
        new_spm.write(design_type + "eoptions.sep = [4 2];\n")
        new_spm.write(
            design_type + "eoptions.tol = [0.02 0.02 0.02 0.001 0.001 0.001 0.01 0.01 0.01 0.001 0.001 0.001];\n")
        new_spm.write(design_type + "eoptions.fwhm = [7 7]\n;")
        new_spm.write(design_type + "roptions.interp = 4;\n")
        new_spm.write(design_type + "roptions.wrap = [0 0 0];\n")
        new_spm.write(design_type + "roptions.mask = 0;\n")
        new_spm.write(design_type + "roptions.prefix = 'r';\n")

def generate_mfile_old_normalize(
    spm_path: str, 
    mfile_name: str,
    images_to_norm: Union[str, List[str]], 
    template_image: str,
    bb: Optional[List[int]] = None, 
    write_vox_size: str = '[1.5 1.5 1.5]', 
    wrapping: bool = False,
    interpolation: int = 4, 
    prefix: str = 'w'
) -> None:

    if isinstance(images_to_norm, str):
        images_to_norm = [images_to_norm]

    if bb is None:
        bb = default_bounding_box

    with open(mfile_name, "w") as new_spm:
        new_spm.write(f"addpath('{spm_path}')\n")

        design_type = "matlabbatch{1}.spm.tools.oldnorm.estwrite."

        for i in range(len(images_to_norm)):
            new_spm.write(
                design_type + "subj(" + str(i + 1) + ").source = {'" + images_to_norm[i] + ",1'};" + "\n" +
                design_type + "subj(" + str(i + 1) + ").wtsrc = '';" + "\n" +
                design_type + "subj(" + str(i + 1) + ").resample = {'" + images_to_norm[i] + ",1'};" + "\n")

        new_spm.write(
            design_type + "eoptions.template = {'" + template_image + ",1'};" + "\n" +
            design_type + "eoptions.weight = '';" + "\n" +
            design_type + "eoptions.smosrc = 8;" + "\n" +
            design_type + "eoptions.smoref = 0;" + "\n" +
            design_type + "eoptions.regtype = 'mni';" + "\n" +
            design_type + "eoptions.cutoff = 25;" + "\n" +
            design_type + "eoptions.nits = 16;" + "\n" +
            design_type + "eoptions.reg = 1;" + "\n" +
            design_type + "roptions.preserve = 0;" + "\n" +
            design_type + "roptions.bb =[" + str(bb[0]) + " " + str(bb[1]) + " " + str(bb[2]) + "\n" +
            str(bb[3]) + " " + str(bb[4]) + " " + str(bb[5]) + "];" + "\n" +
            design_type + "roptions.vox =" + write_vox_size + ";" + "\n" +
            design_type + "roptions.interp =" + str(interpolation) + ";" + "\n")

        if wrapping:
            new_spm.write(design_type + "roptions.wrap = [1 1 1];" + "\n")
        else:
            new_spm.write(design_type + "roptions.wrap = [0 0 0];" + "\n")

        new_spm.write(design_type + "roptions.prefix ='" + prefix + "';" + "\n")

        new_spm.write("spm('defaults','fmri');" + "\n")
        new_spm.write("spm_jobman('initcfg');" + "\n")
        new_spm.write("spm_jobman('run',matlabbatch);" + "\n")

def generate_mfile_old_deformations(
    spm_path: str, 
    mfile_name: str,
    def_matrix: str, 
    base_image: str,
    images_to_deform: List[str], 
    interpolation: int
) -> None:

    with open(mfile_name, "w") as new_spm:
        new_spm.write(f"addpath('{spm_path}')\n")

        source_img_path, source_img_name = os.path.split(images_to_deform[0])

        design_type_comp = "matlabbatch{1}.spm.util.defs.comp{1}.inv."
        design_type_out = "matlabbatch{1}.spm.util.defs.out{1}."

        new_spm.write(
                design_type_comp + "comp{1}.sn2def.matname = {'" + def_matrix + "'};\n"
                + design_type_comp + "comp{1}.sn2def.vox = [NaN NaN NaN];\n"
                + design_type_comp + "comp{1}.sn2def.bb = [NaN NaN NaN\n" + "NaN NaN NaN];\n"
                + design_type_comp + "space = {'" + base_image + "'};\n"
                + design_type_out + "pull.fnames = {\n"
                )

        for image in images_to_deform:
            new_spm.write("'" + image + "'" + "\n")
        new_spm.write("};" + "\n")

        new_spm.write(
                design_type_out + "pull.savedir.saveusr = {'" + source_img_path + "/'};\n"
                + design_type_out + "pull.interp = " + str(interpolation) + ";\n"
                + design_type_out + "pull.mask = 1;\n"
                + design_type_out + "pull.fwhm = [0 0 0];\n"
                )

def generate_mfile_new_normalize(
    spm_path: str, 
    mfile_name: str, 
    template_image: str, 
    images_to_norm: Union[str, List[str]], 
    images_to_write: Optional[Union[str, List[str]]] = None,
    bb: Optional[List[int]] = None, 
    write_vox_size: str = "[1.5 1.5 1.5]",
    interpolation: int = 4
) -> None:

    if bb is None:
        bb = default_bounding_box

    if isinstance(images_to_norm, str):
        images_to_norm = [images_to_norm]

    if images_to_write is None:
        images_to_write = images_to_norm
    elif isinstance(images_to_write, str):
        images_to_write = [images_to_write]

    with open(mfile_name, "w") as new_spm:
        new_spm.write(f"addpath('{spm_path}')\n")

        design_type = "matlabbatch{1}.spm.spatial.normalise.estwrite."

        new_spm.write(design_type + "subj.vol = {'")

        for image_to_norm in images_to_norm:
            new_spm.write("'" + image_to_norm + ",1'" + "\n")
        new_spm.write("};" + "\n")

        new_spm.write(design_type + "subj.resample = {" + "\n")

        for image in images_to_write:
            new_spm.write("'" + image + ",1'" + "\n")
        new_spm.write("};" + "\n")

        new_spm.write(
            design_type + "eoptions.biasreg = 0.01;\n" +
            design_type + "eoptions.biasfwhm = 60;\n" +
            design_type + "eoptions.tpm = {'" + template_image + "'};\n" +
            design_type + "eoptions.affreg = 'mni';\n" +
            design_type + "eoptions.reg = [0 0.001 0.5 0.05 0.2];\n" +
            design_type + "eoptions.fwhm = 0;\n" +
            design_type + "eoptions.samp = 3;\n" +
            design_type + "woptions.bb = [" +
            str(bb[0]) + " " + str(bb[1]) + " " + str(bb[2]) + "\n" +
            str(bb[3]) + " " + str(bb[4]) + " " + str(bb[5]) + "];" + "\n" +
            design_type + "woptions.vox = " + write_vox_size + ";" + "\n" +
            design_type + "woptions.interp = " + str(interpolation) + ";" + "\n")

def generate_mfile_new_deformations(
    spm_path: str, 
    mfile_name: str,
    def_matrix: str, 
    images_to_deform: Union[str, List[str]],
    interpolation: int, 
    prefix: str = "w"
) -> None:

    if isinstance(images_to_deform, str):
        images_to_deform = [images_to_deform]

    with open(mfile_name, "w") as new_spm:
        new_spm.write(f"addpath('{spm_path}')\n")

        design_type_comp = "matlabbatch{1}.spm.util.defs.comp{1}."
        design_type_out = "matlabbatch{1}.spm.util.defs.out{1}."


        new_spm.write(
                design_type_comp + "def = {'" + def_matrix + "'};\n"
                + design_type_out + "pull.fnames = {" + "\n"
                )

        for image in images_to_deform:
            new_spm.write("'" + image + "'\n")
        new_spm.write("};\n")

        new_spm.write(
                design_type_out + "pull.savedir.savesrc = 1;\n"
                + design_type_out + "pull.interp =" + str(interpolation) + ";\n"
                + design_type_out + "pull.mask = 0;\n"
                + design_type_out + "pull.fwhm = [0 0 0];\n"
                + design_type_out + "pull.prefix ='" + prefix + "';\n"
                )

def generate_mfile_smooth_imgs(
    spm_path: str, 
    mfile_name: str, 
    images_to_smooth: List[str], 
    smoothing: List[float]
) -> None:

    with open(mfile_name, "w") as new_spm:
        new_spm.write(f"addpath('{spm_path}')\n")

        design_type = "matlabbatch{1}.spm.spatial.smooth."
        smoothing_array = (
                "[" + str(smoothing[0]) + " " + str(smoothing[1]) + " " + str(smoothing[2]) + "]"
        )

        new_spm.write(design_type + "data = {\n")

        for i in images_to_smooth:
            new_spm.write("'" + i + ",1'\n")
        new_spm.write("};" + "\n")

        new_spm.write(design_type + "fwhm =" + smoothing_array + ";" + "\n")
        new_spm.write(design_type + "dtype = 0;" + "\n")
        new_spm.write(design_type + "im = 0;" + "\n")
        new_spm.write(design_type + "prefix ='" + "s" + "';" + "\n")

        new_spm.write("spm('defaults','fmri');\n")
        new_spm.write("spm_jobman('initcfg');\n")
        new_spm.write("spm_jobman('run',matlabbatch);\n")

def generate_mfile_model(
    spm_path: str, 
    mfile_name: str,
    save_dir: str, 
    group1: List[str], 
    group2: List[str],
    covar1_name: Optional[str] = None, 
    group1_covar1: Optional[List[float]] = None, 
    group2_covar1: Optional[List[float]] = None,
    covar2_name: Optional[str] = None, 
    group1_covar2: Optional[List[float]] = None, 
    group2_covar2: Optional[List[float]] = None,
    mask: Optional[str] = None
) -> None:


    with open(mfile_name, "w") as new_spm:

        new_spm.write(f"addpath ('{spm_path}');\n\n")

        design_type = "matlabbatch{1}.spm.stats.factorial_design."

        new_spm.write(
                design_type + "dir = {'" + save_dir + "/'};\n"
                + design_type + "des.t2.scans1 = {\n"
                )

        for image in group1:
            new_spm.write("'" + image + ",1'" + "\n")
        new_spm.write("};" + "\n")

        new_spm.write(design_type + "des.t2.scans2 = {" + "\n")

        for image in group2:
            new_spm.write("'" + image + ",1'" + "\n")
        new_spm.write("};" + "\n")

        new_spm.write(
                design_type
                + "des.t2.dept = 0;\n"
                + design_type + "des.t2.variance = 1;\n"
                + design_type + "des.t2.gmsca = 0;\n"
                + design_type + "des.t2.ancova = 0;\n"
                )

        if covar1_name and group1_covar1 and group2_covar1:

            new_spm.write(design_type + "cov(1).c = [")
            for covar1 in group1_covar1:
                new_spm.write(str(covar1) + "\n")
            for covar1 in group2_covar1:
                new_spm.write(str(covar1) + "\n")
            new_spm.write("];\n")
            new_spm.write(
                design_type + "cov(1).cname = '" + covar1_name + "';\n"
                + design_type + "cov(1).iCFI = 1;\n"
                + design_type + "cov(1).iCC = 5;\n")


        if covar2_name and group1_covar2 and group2_covar2:

            new_spm.write(design_type + "cov(2).c = [")
            for covar2 in group1_covar2:
                new_spm.write(str(covar2) + "\n")
            for covar2 in group2_covar2:
                new_spm.write(str(covar2) + "\n")
            new_spm.write("];\n")

            new_spm.write(
                    design_type + "cov(2).cname = '" + covar2_name + "';\n"
                    + design_type + "cov(2).iCFI = 1;\n"
                    + design_type + "cov(2).iCC = 1;\n"
                    )

        new_spm.write(design_type + "multi_cov = struct('files', {}, 'iCFI', {}, 'iCC', {});\n")
        
        if mask:
            new_spm.write(design_type + "masking.tm.tm_none = 1;\n"
                + design_type + "masking.im = 0;\n"
                + design_type + "masking.em = {'" + mask + ",1'};\n")
        else:
             new_spm.write(design_type + "masking.tm.tm_none = 1;\n"
                + design_type + "masking.im = 0;\n"
                + design_type + "masking.em = {''};\n")
                
        new_spm.write(design_type + "globalc.g_omit = 1;\n"
                + design_type + "globalm.gmsca.gmsca_no = 1;\n"
                + design_type + "globalm.glonorm = 1;\n\n"
                )

        new_spm.write("spm('defaults','fmri');\n")
        new_spm.write("spm_jobman('initcfg');\n")
        new_spm.write("spm_jobman('run',matlabbatch);\n")

def generate_mfile_estimate_model(
    spm_path: str, 
    mfile_name: str, 
    spm_mat: str
) -> None:

    with open(mfile_name, "w") as new_spm:

        new_spm.write(f"addpath ('{spm_path}');\n\n")
        
        design_type = "matlabbatch{1}.spm.stats.fmri_est."

        new_spm.write(design_type + "spmmat = {'" + spm_mat + "'};\n")
        new_spm.write(design_type + "write_residuals = 0;\n")
        new_spm.write(design_type + "method.Classical = 1;\n\n")

        new_spm.write("spm('defaults','fmri');\n")
        new_spm.write("spm_jobman('initcfg');\n")
        new_spm.write("spm_jobman('run',matlabbatch);\n")

def generate_mfile_contrast(
    spm_path: str, 
    mfile_name: str, 
    spm_mat: str, 
    contrast_name: str = "contrast", 
    contrast: str = "[1 -1 0]"
) -> None:

    with open(mfile_name, "w") as new_spm:

        new_spm.write(f"addpath ('{spm_path}');\n\n")

        design_type = "matlabbatch{1}.spm.stats.con."

        new_spm.write(design_type + "spmmat = {'" + spm_mat + "'};\n")
        new_spm.write(design_type + "consess{1}.tcon.name = '" + contrast_name + "';\n")
        new_spm.write(design_type + "consess{1}.tcon.weights =" + contrast + ";\n")
        new_spm.write(design_type + "consess{1}.tcon.sessrep = 'none';\n")
        new_spm.write(design_type + "delete = 0;\n\n")

        new_spm.write("spm('defaults','fmri');\n")
        new_spm.write("spm_jobman('initcfg');\n")
        new_spm.write("spm_jobman('run',matlabbatch);\n")


