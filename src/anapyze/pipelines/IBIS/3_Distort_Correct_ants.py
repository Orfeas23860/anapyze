import warnings

warnings.filterwarnings("ignore")

import os

import nibabel as nib
from os.path import join, exists
import numpy as np
import time
from datetime import datetime
import nilearn.image as proc

"""
This script corrects distortions in the DTI data using 'dipy', 'nilearn', and 'nibabel' libraries along with ANTs software. 
This needs the inputs from both previous cells (including the cat12 results) so wait those to finish.

AFTER THIS SCRIPT you are ready to run the Process_Cohort.m script in the fw_pasternak directory (repository).
"""

dir_patients = r'/mnt/d/IBIS_DATA/Reorder_New'


def extract_date_from_dir(dir_):
    fecha_str = dir_.split('_')[-1]  # Extrae la fecha del nombre
    return datetime.strptime(fecha_str, '%Y%m%d')


list_dirs = os.listdir(dir_patients)

for i in list_dirs:

    dir_subj = join(dir_patients, i)

    print('\nProcessing %s: Subject %s/%s' % (i, list_dirs.index(i), len(list_dirs)))

    start_time = time.time()

    list_subj = os.listdir(dir_subj)

    dti_list = []
    t1_list = []

    for j in list_subj:
        if j.startswith('dti_'):
            dti_list.append(j)
        elif j.startswith('cat12_'):
            t1_list.append(j)

    cat12_dates = {d: extract_date_from_dir(d) for d in t1_list}
    dti_dates = {d: extract_date_from_dir(d) for d in dti_list}

    for dti, dti_date in dti_dates.items():

        # Calcula la diferencia en días con cada cat12 y encuentra el mínimo
        closest_mri = min(cat12_dates, key = lambda x: abs((cat12_dates[x] - dti_date).days))

        print('Pairing %s and %s' % (dti, closest_mri))

        dir_t1 = join(dir_subj, closest_mri, 'mri')
        dir_dti = join(dir_subj, dti)

        t1_source = join(dir_t1, 'p0t1.nii')
        dti_source = join(dir_dti, 'dti_eddy_denoised.nii.gz')

        if exists(t1_source) and exists(dti_source):

            t1_img = nib.load(t1_source)
            t1_data = t1_img.get_fdata()
            t1_data = t1_data.astype(float)
            t1_img.set_data_dtype(float)

            indx = np.where(t1_data > 0)
            t1_data[indx] = 1 / (t1_data[indx])

            inverted_t1 = nib.Nifti1Image(t1_data, t1_img.affine, t1_img.header)
            inverted_t1 = proc.smooth_img(inverted_t1, 2)
            inverted_name = join(dir_t1, 't1_inverted.nii.gz')
            nib.save(inverted_t1, inverted_name)

            ants_log = 'ANTs_log.txt'

            img_4d = nib.load(dti_source)
            # Get the 4D data array
            data_4d = img_4d.get_fdata()
            # Extract the first frame (3D) from the 4D data
            data_3d = data_4d[:, :, :, 0]

            # Create a new 3D NIfTI image with the same header as the original 4D image
            img_3d = nib.Nifti1Image(data_3d, img_4d.affine, img_4d.header)
            b0 = join(dir_dti, 'b0.nii.gz')
            nib.save(img_3d, b0)

            log = join(dir_dti, 'ants.log')

            print("Corregistering T1 with b0....")

            command = 'antsRegistrationSyN.sh -d 3 -f %s -m %s -o %s/t1 -t r -n 6 > %s' % (
            b0, inverted_name, dir_t1, log)
            os.system(command)

            print("Deforming b0....")

            t1_warped = join(dir_t1, 't1Warped.nii.gz')

            command = 'antsRegistrationSyN.sh -d 3 -f %s -m %s -o %s/dti -t s -n 12 >> %s' % (
            t1_warped, b0, dir_dti, log)
            os.system(command)

            dti_warped = join(dir_dti, 'dtiWarped.nii.gz')
            dti_warp = join(dir_dti, 'dti1Warp.nii.gz')

            warped_files = []

            print("Applying the transformation to the whole dataset....")

            for k in range(data_4d.shape[3]):
                data_3d = data_4d[:, :, :, k]
                img_3d = nib.Nifti1Image(data_3d, img_4d.affine, img_4d.header)
                bk = join(dir_dti, 'temp_b%s.nii.gz' % k)
                nib.save(img_3d, bk)
                warped_bk = join(dir_dti, 'warped_b%s.nii.gz' % k)

                command = 'antsApplyTransforms -d 3 -i %s -r %s -o %s -t %s >> %s' % (
                bk, dti_warped, warped_bk, dti_warp, log)
                os.system(command)

                warped_files.append(warped_bk)

            data_3d_list = [nib.load(file).get_fdata() for file in warped_files]

            data_4d = np.stack(data_3d_list, axis = 3)

            affine = nib.load(warped_files[0]).affine
            header = nib.load(warped_files[0]).header
            header.set_data_shape(data_4d.shape)

            img_4d = nib.Nifti1Image(data_4d, affine, header)

            ants_out_file = join(dir_dti, 'dti_ants.nii.gz')

            nib.save(img_4d, ants_out_file)

            to_remove = join(dir_dti, 'temp_*')
            os.system('rm %s' % to_remove)
            to_remove = join(dir_dti, 'warped_*')
            os.system('rm %s' % to_remove)

            # Now we will mask data

            out_mask = join(dir_dti, 'dti_mask.nii.gz')
            out_masked = join(dir_dti, 'dti_masked.nii.gz')

            if exists(ants_out_file):  # and not exists(out_masked):

                out = join(dir_dti, 'dti')
                os.system('bet %s %s -m -f 0.2 -n' % (ants_out_file, out))

                if exists(out_mask):

                    img_in = nib.load(ants_out_file)
                    mask_in = nib.load(out_mask)

                    img_data = img_in.get_fdata()
                    mask_data = mask_in.get_fdata()

                    mask_data = np.expand_dims(mask_data, axis = 3)
                    masked_data = img_data * mask_data

                    img = nib.Nifti1Image(masked_data, img_in.affine, img_in.header)
                    nib.save(img, out_masked)

                print("I finished Processing %s: It took me %s minutes " % (dti, (time.time() - start_time) / 60))

            to_remove = join(dir_dti, 'dti1*')
            os.system('rm %s' % to_remove)
            to_remove = join(dir_dti, 'dti0GenericAffine.mat')
            os.system('rm %s' % to_remove)
            to_remove = join(dir_dti, 'dtiInverseWarped.nii.gz')
            os.system('rm %s' % to_remove)
            to_remove = join(dir_dti, 'dtiWarped.nii.gz')
            os.system('rm %s' % to_remove)
            to_remove = join(dir_dti, 'dti_eddy_denoised.nii.gz')
            os.system('rm %s' % to_remove)
            to_remove = join(dir_dti, 'dti_eddy.nii.gz')
            os.system('rm %s' % to_remove)
            to_remove = join(dir_dti, 'dti.nii')
            os.system('rm %s' % to_remove)
            to_remove = join(dir_dti, 'b0.nii.gz')
            os.system('rm %s' % to_remove)

        else:
            print("DTI or MRI images missing")