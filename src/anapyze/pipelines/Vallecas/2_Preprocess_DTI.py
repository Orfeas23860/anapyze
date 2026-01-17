import warnings

warnings.filterwarnings("ignore")

import os
import shutil
import nibabel as nib
from os.path import join, exists, isdir, dirname
from concurrent.futures import ThreadPoolExecutor
import time


"""
This script performs preprocessing steps on Diffusion Tensor Imaging (DTI) data for each subject in a given directory. 

The steps involve:

- Eddy current and movement correction via FSL.
- Denoising through DIPY's patch2self method.
- Removal of Gibbs ringing artifacts.

The result is *dti_eddy_denoised.nii.gz* that is placed under the *dti_bXXX_date* directory
"""

dir_raws = r'/mnt/nasneuro_share/data/raws/PVallecas/niftis'
dir_derivatives = r'/mnt/nasneuro_share/data/derivatives/DTI'

from dipy.core.gradients import gradient_table
from dipy.io.gradients import read_bvals_bvecs
from dipy.denoise.patch2self import patch2self
from dipy.denoise.gibbs import gibbs_removal

list_dirs = os.listdir(dir_raws)

for subj_ in list_dirs:

    dir_subj = join(dir_raws, subj_)

    print('\nProcessing %s: Subject %s/%s' % (subj_, list_dirs.index(subj_), len(list_dirs)))

    if isdir(dir_subj):

        subj_derivates = join(dir_derivatives, subj_)
        if not exists(subj_derivates):
            os.makedirs(subj_derivates)

        visits = os.listdir(dir_subj)

        for visit_ in visits:

            dti_dir = join(dir_subj, visit_,'DTI')

            dti_file = join(dti_dir,'%s_DTI_%s.nii.gz' % (subj_,visit_))
            bval = join(dti_dir,'%s_DTI_%s.bval' % (subj_,visit_))
            bvec = join(dti_dir,'%s_DTI_%s.bvec' % (subj_,visit_))

            if exists(dti_file) and exists(bvec) and exists(bval):

                visit_deriv_dir = join(subj_derivates, visit_)
                if not exists(visit_deriv_dir):
                    os.makedirs(visit_deriv_dir)

                dti_deriv_ = join(visit_deriv_dir, '%s_DTI_%s.nii.gz' % (subj_,visit_))
                if not exists(dti_deriv_):
                    shutil.copy(dti_file, dti_deriv_)

                bval_deriv_ = join(visit_deriv_dir, '%s_DTI_%s.bval' % (subj_,visit_))
                if not exists(bval_deriv_):
                    shutil.copy(bval, bval_deriv_)

                bvec_deriv_ = join(visit_deriv_dir, '%s_DTI_%s.bvec' % (subj_,visit_))
                if not exists(bvec_deriv_):
                    shutil.copy(bvec, bvec_deriv_)

                this_case = [dti_deriv_,bval_deriv_, bvec_deriv_]


                # If already processed it is not added to the pending list
                check_result = join(visit_deriv_dir,'subj_data_denoised.nii.gz')

                #if not exists(check_result):
                if visit_=='V01':

                    start = time.time()

                    bvals, bvecs = read_bvals_bvecs(bval_deriv_, bvec_deriv_)
                    gtab = gradient_table(bvals, bvecs)

                    bet_out = join(visit_deriv_dir,'subj_brain')

                    command = f'bet {dti_deriv_} {bet_out} -o -m -s -f 0.1'
                    os.system(command)

                    adq_file = join(visit_deriv_dir,'acqp.txt')

                    with open (adq_file, 'w') as f:
                        f.write('0 1 0 0.05')

                    with open (bval_deriv_, 'r') as bval_text:
                        text = bval_text.read()
                    words = text.split()
                    n_directions = len(words)

                    index_file = join(visit_deriv_dir,'index.txt')

                    with open (index_file, 'w') as f_index:
                        for j in range(n_directions):
                            f_index.write('1 ')

                    mask = join(visit_deriv_dir, 'subj_brain_mask.nii.gz')

                    eddy_out = join(visit_deriv_dir, 'subj_data')

                    command = (f'eddy --imain={dti_deriv_} --mask={mask} --acqp={adq_file} --index={index_file} ' 
                               f'--bvecs={bvec_deriv_} --bvals={bval_deriv_} --repol --out={eddy_out}')
                    os.system(command)

                    eddy_out_ext = join(visit_deriv_dir, 'subj_data.nii.gz')
                    dti_out = join(visit_deriv_dir, 'subj_data_denoised.nii.gz')

                    dti_img = nib.load(eddy_out_ext)

                    dti_data = dti_img.get_fdata()
                    hdr = dti_img.header
                    affine = dti_img.affine

                    print("Denoising....")
                    denoised_arr = patch2self(
                            dti_data, bvals, model = 'ols', shift_intensity = True,
                            clip_negative_vals = False, b0_threshold = 50,
                            )

                    print("Removing Gibbs artifacts....")
                    gibbs_corr = gibbs_removal(denoised_arr, slice_axis = 2, num_processes = 4)

                    img = nib.Nifti1Image(gibbs_corr, affine, hdr)
                    nib.save(img, dti_out)

                    print(
                        "I finished processing Visit %s:\n It took me %s minutes" % (dti_deriv_,(time.time() - start) / 60)
                        )