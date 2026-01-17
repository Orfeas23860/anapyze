import warnings
import os
import nibabel as nib
from os.path import join, exists, isdir
import numpy as np
import time
from scipy.ndimage import binary_closing, gaussian_filter,binary_fill_holes
import nilearn.image as proc

warnings.filterwarnings("ignore")

"""
This script corrects distortions in the DTI data using 'dipy', 'nilearn', and 'nibabel' libraries along with ANTs software. 
This needs the inputs from both previous cells (including the cat12 results) so wait those to finish.

AFTER THIS SCRIPT you are ready to run the Process_Cohort.m script in the fw_pasternak directory (repository).
"""

dir_patients = r'/mnt/nasneuro_share/data/derivatives/DTI'
dir_t1s = r'/mnt/nasneuro_share/data/derivatives/CAT12_baseline'


list_dirs = os.listdir(dir_patients)

for subj_ in list_dirs:

    dir_subj = join(dir_patients, subj_)

    if isdir(dir_subj):

        list_visits = os.listdir(dir_subj)

        for visit_ in list_visits:

            visit_dir = join(dir_subj, visit_)

            if isdir(visit_dir):

                print('\nProcessing Subject %s Visit %s: Subject %s/%s' % (subj_,visit_, list_dirs.index(subj_), len(list_dirs)))

                start_time = time.time()

                dti_source = join(visit_dir,'subj_data_denoised.nii.gz')
                bval = join(visit_dir,'%s_DTI_%s.bval' % (subj_,visit_))
                bvec = join(visit_dir,'subj_data.eddy_rotated_bvecs')

                dir_cat = join(dir_t1s, subj_,visit_,'T1','mri')
                t1_source = join(dir_cat,'p0%s_T1_%s.nii' % (subj_,visit_))
                gm_source = join(dir_cat,'p1%s_T1_%s.nii' % (subj_,visit_))

                if exists(t1_source) and exists(dti_source):

                    out_mask = join(visit_dir, 'dti_mask.nii.gz')
                    #out_masked = join(visit_dir, 'dti_masked.nii.gz')
                    out_masked = join(visit_dir,'%s_%s_dti_masked.nii.gz' % (subj_,visit_))

                    if not exists(out_mask) or not exists(out_masked):

                        t1_img = nib.load(t1_source)
                        t1_data = t1_img.get_fdata()
                        t1_data = t1_data.astype(float)
                        t1_img.set_data_dtype(float)

                        gm_img = nib.load(gm_source)
                        gm_data = gm_img.get_fdata()

                        print("Creating mask and tuned inverted t1...")

                        # Step 1: Fill gaps using binary closing
                        # Adjust the structure size as needed
                        filled_mask = binary_closing(gm_data, structure=np.ones((15, 15, 15))).astype(np.float32)
                        filled_mask = binary_fill_holes(filled_mask).astype(np.float32)

                        # Step 2: Soften the mask using Gaussian smoothing
                        # Adjust sigma to control the level of smoothing
                        smoothed_mask = gaussian_filter(filled_mask, sigma=3)

                        # Optional: Step 3 - Threshold to re-binarize (if needed)
                        threshold = 0.4
                        binary_smoothed_mask = (smoothed_mask > threshold).astype(np.float32)

                        # Save the result as a new NIfTI file
                        p0mask_name = join(dir_cat,'p0_mask.nii')
                        p0mask_nii = nib.Nifti1Image(binary_smoothed_mask, affine=gm_img.affine)
                        nib.save(p0mask_nii, p0mask_name)

                        t1_data = t1_data*binary_smoothed_mask

                        indx = np.where(t1_data > 0)
                        t1_data[indx] = 1 / (t1_data[indx])

                        indx = np.where(t1_data > 2)
                        t1_data[indx] = 0

                        inverted_t1 = nib.Nifti1Image(t1_data, t1_img.affine, t1_img.header)
                        inverted_t1 = proc.smooth_img(inverted_t1, 2)
                        inverted_name = join(dir_cat, 't1_inverted.nii.gz')
                        nib.save(inverted_t1, inverted_name)

                        ants_log = 'ANTs_log.txt'

                        img_4d = nib.load(dti_source)
                        # Get the 4D data array
                        data_4d = img_4d.get_fdata()
                        # Extract the first frame (3D) from the 4D data
                        data_3d = data_4d[:, :, :, 0]

                        # Create a new 3D NIfTI image with the same header as the original 4D image
                        img_3d = nib.Nifti1Image(data_3d, img_4d.affine, img_4d.header)
                        b0 = join(visit_dir, 'b0.nii.gz')
                        nib.save(img_3d, b0)

                        log = join(visit_dir, 'ants.log')

                        print("Corregistering T1 with b0....")

                        command = 'antsRegistrationSyN.sh -d 3 -f %s -m %s -o %s/t1 -t r -n 6 > %s' % (
                        b0, inverted_name, dir_cat, log)
                        os.system(command)

                        print("Fixing Vertical missmatch")

                        img_b0 = nib.load(b0)
                        b0_data = img_b0.get_fdata()

                        t1_warped = join(dir_cat, 't1Warped.nii.gz')
                        img_t1w = nib.load(t1_warped)
                        t1w_data = img_t1w.get_fdata()


                        for slice_ in range(b0_data.shape[2]):

                            slice_data_max = np.amax(b0_data[:,:,slice_])
                            if slice_data_max == 0:
                                t1w_data[:,:,slice_] = 0

                        out_t1w = nib.Nifti1Image(t1w_data, img_t1w.affine, img_t1w.header)
                        nib.save(out_t1w, t1_warped)

                        print("Deforming b0....")

                        command = 'antsRegistrationSyN.sh -d 3 -f %s -m %s -o %s/dti -t so -n 12 >> %s' % (
                        t1_warped, b0, visit_dir, log)
                        os.system(command)

                        dti_warped = join(visit_dir, 'dtiWarped.nii.gz')
                        dti_warp = join(visit_dir, 'dti1Warp.nii.gz')

                        bias_corrected_b0 = join(visit_dir, 'bias_corrected_b0.nii.gz')
                        bias_correction_field = join(visit_dir, 'bias_correction.nii.gz')

                        print("Calculating Bias Correction....")

                        command = 'N4BiasFieldCorrection -d 3 -v 1 -s 4 -b [ 100, 3 ] -c [ 1000, 0.0 ] -i %s -o [ %s, %s ] >> %s' % (
                            dti_warped, bias_corrected_b0, bias_correction_field, log)

                        os.system(command)

                        bias_corr_data = nib.load(bias_correction_field).get_fdata()

                        warped_files = []

                        print("Applying the transformation to the whole dataset....")

                        for k in range(data_4d.shape[3]):

                            data_3d = data_4d[:, :, :, k]
                            img_3d = nib.Nifti1Image(data_3d, img_4d.affine, img_4d.header)
                            bk = join(visit_dir, 'temp_b%s.nii.gz' % k)
                            nib.save(img_3d, bk)
                            warped_bk = join(visit_dir, 'warped_b%s.nii.gz' % k)

                            command = 'antsApplyTransforms -d 3 -i %s -r %s -o %s -t %s >> %s' % (
                                bk, dti_warped, warped_bk, dti_warp, log)
                            os.system(command)

                            if k == 0:

                                command = 'antsRegistrationSyN.sh -d 3 -f %s -m %s -o %s/bk -t r -n 6 > %s' % (
                                    bias_corrected_b0, warped_bk, visit_dir, log)
                                os.system(command)

                            bk_transform = join(visit_dir, 'bk0GenericAffine.mat')
                            command = 'antsApplyTransforms -d 3 -i %s -r %s -o %s -t %s >> %s' % (
                                warped_bk, bias_corrected_b0, warped_bk, bk_transform, log)
                            os.system(command)

                            warped_files.append(warped_bk)

                        data_3d_list = [nib.load(file).get_fdata() for file in warped_files]
                        data_3d_list_bc = [nib.load(file).get_fdata()/bias_corr_data for file in warped_files]

                        data_4d = np.stack(data_3d_list, axis = 3)
                        data_4d_bc = np.stack(data_3d_list_bc, axis = 3)

                        data_4d = data_4d.astype(np.float32)
                        data_4d_bc = data_4d_bc.astype(np.float32)

                        affine = nib.load(warped_files[0]).affine
                        header = nib.load(warped_files[0]).header
                        header.set_data_shape(data_4d.shape)

                        img_4d = nib.Nifti1Image(data_4d, affine, header)
                        ants_out_file = join(visit_dir, 'dti_ants.nii.gz')
                        nib.save(img_4d, ants_out_file)

                        img_4d_bc = nib.Nifti1Image(data_4d_bc, affine, header)
                        ants_out_file_bc = join(visit_dir, 'dti_ants_bias_corr.nii.gz')
                        nib.save(img_4d_bc, ants_out_file_bc)

                        # Now we will mask data

                        if exists(ants_out_file_bc) and not exists(out_masked):

                            out = join(visit_dir, 'dti')
                            os.system('bet %s %s -m -f 0.2 -n' % (ants_out_file_bc, out))

                            if exists(out_mask):

                                img_in = nib.load(ants_out_file_bc)
                                mask_in = nib.load(out_mask)

                                img_data = img_in.get_fdata()
                                mask_data = mask_in.get_fdata()

                                mask_data = np.expand_dims(mask_data, axis = 3)
                                masked_data = img_data * mask_data

                                img = nib.Nifti1Image(masked_data, img_in.affine, img_in.header)
                                nib.save(img, out_masked)

                        print("I finished Processing %s: It took me %s minutes " % (dti_source, (time.time() - start_time) / 60))

                        print(ants_out_file_bc)
                        print(out_masked)

                        to_remove = join(visit_dir, 'dti1*')
                        os.system('rm %s' % to_remove)
                        to_remove = join(visit_dir, '*warped_b*')
                        os.system('rm %s' % to_remove)
                        to_remove = join(visit_dir, '*temp_b*')
                        os.system('rm %s' % to_remove)
                        to_remove = join(visit_dir, '*bk*')
                        os.system('rm %s' % to_remove)
                        
                        to_remove_list = ['dti0GenericAffine.mat','dtiInverseWarped.nii.gz','dtiWarped.nii.gz','b0.nii.gz']
                        for remove_file in to_remove_list:
                            file_path = join(visit_dir, remove_file)
                            if exists(file_path):
                                os.remove(file_path)
