import warnings

warnings.filterwarnings("ignore")

import os
import shutil
import nibabel as nib
from os.path import join, exists
import time

"""
This script performs preprocessing steps on Diffusion Tensor Imaging (DTI) data for each subject in a given directory. 

The steps involve:

- Eddy current and movement correction via FSL.
- Denoising through DIPY's patch2self method.
- Removal of Gibbs ringing artifacts.

The result is *dti_eddy_denoised.nii.gz* that is placed under the *dti_bXXX_date* directory
"""


dir_patients = r'/mnt/d/IBIS_DATA/Reorder_New'

from dipy.core.gradients import gradient_table
from dipy.io.gradients import read_bvals_bvecs
from dipy.denoise.patch2self import patch2self
from dipy.denoise.gibbs import gibbs_removal

list_dirs = os.listdir(dir_patients)



for i in list_dirs:

    print('\nProcessing %s: Subject %s/%s' % (i, list_dirs.index(i), len(list_dirs)))

    start_time = time.time()

    dir_subj = join(dir_patients, i)

    files_ = os.listdir(dir_subj)

    for file_ in files_:

        if file_[0:2] == 'IN' and 'DTI' in file_ and file_[-3:] == 'nii':

            dti_image = join(dir_subj, file_)
            date = file_[-12:-4]
            bval = dti_image[0:-3] + 'bval'
            bvec = dti_image[0:-3] + 'bvec'

            if 'DTI001' in file_:
                b_zero = 800
            else:
                b_zero = 1000

            if exists(dti_image) and exists(bvec) and exists(bval):

                dti_dir = join(dir_subj, 'dti_b%s_%s' % (str(b_zero), date))

                # Check data 3D
                data_ = nib.load(dti_image).get_fdata()
                if len(data_.shape) != 4:
                    print(
                        "Data shape:", data_.shape,
                        ". Something is wrong with the shape of the data. Ignoring this image..."
                        )
                    pass

                else:
                    print("Processing %s_b%s_%s" % (i, str(b_zero), date))
                    print("Data shape:", data_.shape)
                    dti_out = join(dti_dir, 'dti_eddy_denoised.nii.gz')

                    if not exists(dti_dir):
                        os.makedirs(dti_dir)

                    dti_in = join(dti_dir, 'dti.nii')
                    shutil.copy(dti_image, dti_in)

                    bval_in = join(dti_dir, 'dti.bval')
                    shutil.copy(bval, bval_in)

                    bvec_in = join(dti_dir, 'dti.bvec')
                    shutil.copy(bvec, bvec_in)

                    bvals, bvecs = read_bvals_bvecs(bval_in, bvec_in)
                    gtab = gradient_table(bvals, bvecs)

                    dti_compressed = join(dti_dir, 'dti_eddy.nii.gz')

                    # Image Corrections
                    print("Correcting DTI for eddy currents....")
                    log_file = join(dti_dir, 'eddy_correct.log')
                    os.system('eddy_correct %s %s 0 spline >> %s' % (dti_in, dti_compressed, log_file))

                    dti_img = nib.load(dti_compressed)
                    dti_data = dti_img.get_fdata()
                    hdr = dti_img.header
                    affine = dti_img.affine

                    print("Denoising....")
                    denoised_arr = patch2self(
                        dti_data, bvals, model = 'ols', shift_intensity = True,
                        clip_negative_vals = False, b0_threshold = 50
                        )

                    print("Removing Gibbs artifacts....")
                    gibbs_corr = gibbs_removal(denoised_arr, slice_axis = 2, num_processes = -1)

                    img = nib.Nifti1Image(gibbs_corr, affine, hdr)
                    nib.save(img, dti_out)

                    b_file = join(dti_dir, str(b_zero))
                    with open(b_file, 'w') as b0_file:
                        pass

                    print(
                        "I finished processing %s_b%s_%s: It took me %s minutes" % (
                        i, str(b_zero), date, (time.time() - start_time) / 60)
                        )