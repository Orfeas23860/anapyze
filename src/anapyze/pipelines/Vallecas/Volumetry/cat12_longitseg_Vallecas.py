import warnings
import os, sys
from os.path import join, exists, isdir
from anapyze.core import processor

warnings.filterwarnings("ignore")


# CONFIG
# ---------------------------------------------------------------------------------------------------------------
dir_subjects = r'/mnt/nasneuro_share/data/raws/PVallecas/niftis'
mfile_name = '/mnt/nasneuro_share/analysis/jsilva/cat12_longit.m'

# Change your templates here if necessary \toolbox\cat12\templates_MNI152NLin2009cAsym
spm_path = r'/mnt/WORK/software/spm12'
tpm = join(spm_path,'tpm','TPM.nii')
template_volumes = join(spm_path,'toolbox','cat12','templates_MNI152NLin2009cAsym','Template_0_GS.nii')
#---------------------------------------------------------------------------------------------------------------

list_subjects = os.listdir(dir_subjects)
list_subjects.sort()

# This will create a cat_12seg_longit.m
images = []

for subj in list_subjects:
    print('Checking subject %s' % subj)

    subject = []
    check_cat_processing = []

    dir_subj = join(dir_subjects, subj)

    if isdir(dir_subj):

        list_visits = os.listdir(dir_subj)
        list_visits.sort()

        if len(list_visits)>1:

            for visit in list_visits:

                t1_file = join(dir_subj,visit,'T1','%s_T1_%s.nii' % (subj,visit))

                if exists(t1_file):
                    pass
                else:
                    t1_file = join(dir_subj,visit,'T1','%s_T1_%s.nii.gz' % (subj,visit))

                if exists(t1_file):
                    final_gm = join(dir_subj,visit,'T1','mri','mwmwp1r%s_T1_%s.nii' % (subj,visit))
                    check_cat_processing.append(final_gm)
                    subject.append(t1_file)

            # If any new visit not segmented, the patients will be reprocessed.
            # Probably there is a more efficient way to do this, still figuring out

            if all(exists(j) for j in check_cat_processing):
                pass

            else:
                images.append(subject)
                print("New images found for subject!!")

processor.cat12_segmentation_longit(images, mfile_name, template_tpm = tpm, template_volumes = template_volumes,
                              output_vox_size = 1.5, bounding_box = "cat12", surface_processing = 0,
                              spm_path=spm_path)