import warnings

warnings.filterwarnings("ignore")

import os
import shutil
from os.path import join, exists
from spm import CAT12

"""
Note that this script expects that you have run the 0_Reorder_Data.py first

- Patient Data Directory (dir_patients): This points to the directory where patient data is stored. 
- SPM PATH: Path for your installation of the Statistical Parametric Mapping (SPM) software 
- TPM (Tissue Probability Maps) Image (tpm): This is set to the path where the TPM.nii file resides within the SPM software directory. **Check that this is correct**. 
- CAT12 Gray Scale Template Volume (template_volumes): This is set to the path in the SPM directory where the CAT12 toolbox's template volumes are stored. **Check that this is correct**.

This prepares a processing script that will process the collected T1 image files using SPM’s CAT12 toolbox.
A MATLAB script named ‘cat_12.m’ is created that is recommended to be run separately in MATLAB. 
Alternatively you can run it here stating run=False in the spm_proc.cat12seg_imgs line, but you will not take advantage of the multi-threading capabilities of cat12. It is fine for a few images.
"""

dir_patients = r'D:/IBIS_DATA/Reorder_New'
spm_path = r'C:\Users\jesus\Work\software\spm12'
tpm = join(spm_path, 'tpm', 'TPM.nii')
template_volumes = join(spm_path, r'toolbox\cat12\templates_MNI152NLin2009cAsym', 'Template_0_GS.nii')

list_dirs = os.listdir(dir_patients)

images = []

for i in list_dirs:

    dir_subj = join(dir_patients, i)

    files_ = os.listdir(dir_subj)

    for file_ in files_:

        if file_[0:2] == 'IN':
            if file_[-3:] == 'nii':
                if 'T1' in file_:

                    t1_image = join(dir_subj, file_)
                    date = file_[-12:-4]

                    cat12_dir = join(dir_subj, 'cat12_%s' % date)
                    if not exists(cat12_dir):
                        os.makedirs(cat12_dir)

                    rm_in = join(cat12_dir, 't1.nii')
                    if not exists(rm_in):
                        shutil.copy(t1_image, rm_in)

                    check_cat_processing = [join(cat12_dir, 'report', 'catreport_t1.pdf'),
                                            join(cat12_dir, 'mri', 'mwp1t1.nii'),
                                            join(cat12_dir, 'mri', 'mwp2t1.nii'),
                                            join(cat12_dir, 'mri', 'mwp3t1.nii'),
                                            join(cat12_dir, 'mri', 'p0t1.nii'),
                                            join(cat12_dir, 'mri', 'wmt1.nii')]

                    if all(exists(j) for j in check_cat_processing):
                        pass

                    else:
                        images.append(rm_in)

spm_proc = CAT12(spm_path)
cat_12_proc = spm_proc.cat12seg_imgs(images, tpm, template_volumes, run = False)