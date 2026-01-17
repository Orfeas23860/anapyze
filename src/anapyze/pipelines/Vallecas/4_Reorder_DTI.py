import gzip
import os
import shutil
from datetime import datetime
import subprocess
from os.path import exists, join

dir_patients = '/mnt/nasneuro_share/data/derivatives/DTI'
dir_mris = '/mnt/nasneuro_share/data/derivatives/CAT12_baseline'

dirs_ = os.listdir(dir_patients)

#cat12_command = '/Users/jsilva/software/CAT12.9/run_spm12.sh /Users/jsilva/software/CAT12.9/R2023b'

spm_path = "/mnt/WORK/software/spm12"
matlab_cmd = "/usr/local/MATLAB/R2024a_cris/bin/matlab"


for i in dirs_:

    dir_subj = join(dir_patients, i,'V01')

    print('\nProcessing %s: Subject %s/%s' % (i, dirs_.index(i), len(dirs_)))


    dir_t1 = join(dir_mris, i, 'V01', 'T1', 'mri')
    dir_mauricio = join(dir_subj, 'Maurizio')


    results_mauricio = ['free_water_map_01.nii.gz', 'MD_map_01.nii.gz', 'FA_map_01.nii.gz', 'MO_map_01.nii.gz',
                            'FA_FW_map_01.nii.gz', 'MD_FW_map_01.nii.gz', 'MO_FW_map_01.nii.gz']

        

    # Processing results from Maurizio

    print('\nPostprocessing Maurizio outputs for subject %s' % (dirs_.index(i)))

    

    img_to_deform = []

    for r_image in results_mauricio:

            out_ants = 't1_%s' % r_image[0:-3]

            in_files = join(dir_mauricio, out_ants)

            if exists(join(dir_mauricio, out_ants)):
                img_to_deform.append(in_files)


    if img_to_deform:

            def_matrix = join(dir_t1, 'y_%s_T1_V01.nii' % i)

            mfile_name = join(dir_mauricio, 'deformations.m')

            print(mfile_name)


            design_type_comp = "matlabbatch{1}.spm.util.defs.comp{1}."
            design_type_out = "matlabbatch{1}.spm.util.defs.out{1}."

            new_spm = open(mfile_name, "w")

            new_spm.write("addpath('%s')\n" % spm_path)


            new_spm.write(
                    design_type_comp + "def = {'" + def_matrix + "'};\n" +
                    design_type_out + "pull.fnames = {" + "\n"
                    )

            for image in img_to_deform:
                new_spm.write("'" + image + "'\n")
            new_spm.write("};\n")

            new_spm.write(
                    design_type_out + "pull.savedir.savesrc = 1;\n" +
                    design_type_out + "pull.interp =" + str(4) + ";\n" +
                    design_type_out + "pull.mask = 0;\n" +
                    design_type_out + "pull.fwhm = [0 0 0];\n" +
                    design_type_out + "pull.prefix ='" + 'w' + "';\n"
                    )
            
            new_spm.write("spm('defaults','fmri');\n")
            new_spm.write("spm_jobman('initcfg');\n")
            new_spm.write("spm_jobman('run',matlabbatch);\n")

            new_spm.close()

            #os.system('%s batch %s' % (cat12_command, mfile_name))
            command = f"{matlab_cmd} -nosplash -sd {dir_mauricio} -batch deformations"
            print(command)
            #result = subprocess.run(command, shell = True, capture_output = True, text = True)
            os.system(command)

