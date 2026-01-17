import gzip
import os
import shutil
from datetime import datetime
from os.path import exists, join

dir_patients = r'/Volumes/txusser_data/IBIS_DATA/Reorder_New/'

list_dirs = os.listdir(dir_patients)

cat12_command = '/Users/jsilva/software/CAT12.9/run_spm12.sh /Users/jsilva/software/CAT12.9/R2023b'


def extract_date_from_dir(dir_):
    fecha_str = dir_.split('_')[-1]  # Extrae la fecha del nombre
    return datetime.strptime(fecha_str, '%Y%m%d')


for i in list_dirs:

    dir_subj = join(dir_patients, i)

    print('\nProcessing %s: Subject %s/%s' % (i, list_dirs.index(i), len(list_dirs)))

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

        dir_t1 = join(dir_subj, closest_mri, 'mri')
        dir_pasternak = join(dir_subj, dti, 'Pasternak')
        dir_mauricio = join(dir_subj, dti, 'Maurizio')

        results_pasternak = ['fw_FW.nii.gz', 'fw_NoNeg_MD.nii.gz', 'fw_NoNeg_FA.nii.gz', 'fw_NoNeg_MO.nii.gz',
                             'fw_FWE.nii.gz', 'fw_FWE_MD.nii.gz', 'fw_FWE_FA.nii.gz', 'fw_FWE_MO.nii.gz']

        results_mauricio = ['free_water_map_01.nii.gz', 'MD_map_01.nii.gz', 'FA_map_01.nii.gz', 'MO_map_01.nii.gz',
                            'FA_FW_map_01.nii.gz', 'MD_FW_map_01.nii.gz', 'MO_FW_map_01.nii.gz']

        # Processing results from Pasternak

        print('\nPostprocessing Pasternak outputs for subject %s: %s' % (list_dirs.index(i), dti,))

        for r_image in results_pasternak:

            result = join(dir_pasternak, r_image)
            warp = join(dir_t1, 't10GenericAffine.mat')
            t1_inverted = join(dir_t1, 't1_inverted.nii.gz')
            out_ants = join(dir_pasternak, 't1_%s' % r_image)

            final = join(dir_pasternak, 'wt1_' + r_image[0:-3])

            if exists(result) and not exists(final):

                command = 'antsApplyTransforms -d 3 -i %s -r %s -o %s -t [%s,1]' % (result, t1_inverted, out_ants, warp)
                os.system(command)

                with gzip.open(out_ants, 'rb') as f_in:
                    with open(out_ants[0:-3], 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                os.remove(out_ants)

        img_to_deform = []

        for r_image in results_pasternak:

            out_ants = 't1_%s' % r_image[0:-3]

            in_files = join(dir_pasternak, out_ants)

            if exists(join(dir_pasternak, out_ants)):
                img_to_deform.append(in_files)

        if img_to_deform:

            def_matrix = join(dir_t1, 'y_t1.nii')

            mfile_name = join(dir_pasternak, 'deformations.m')

            design_type_comp = "matlabbatch{1}.spm.util.defs.comp{1}."
            design_type_out = "matlabbatch{1}.spm.util.defs.out{1}."

            new_spm = open(mfile_name, "w")

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

            new_spm.close()

            os.system('%s batch %s' % (cat12_command, mfile_name))

        for img_ in img_to_deform:
            os.remove(img_)

        # Processing results from Maurizio

        print('\nPostprocessing Maurizio outputs for subject %s: %s' % (list_dirs.index(i), dti,))

        for r_image in results_mauricio:

            result = join(dir_mauricio, r_image)
            warp = join(dir_t1, 't10GenericAffine.mat')
            t1_inverted = join(dir_t1, 't1_inverted.nii.gz')
            out_ants = join(dir_mauricio, 't1_%s' % r_image)

            final = join(dir_mauricio, 'wt1_' + r_image[0:-3])

            if exists(result) and not exists(final):

                command = 'antsApplyTransforms -d 3 -i %s -r %s -o %s -t [%s,1]' % (result, t1_inverted, out_ants, warp)
                os.system(command)

                with gzip.open(out_ants, 'rb') as f_in:
                    with open(out_ants[0:-3], 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                os.remove(out_ants)

        img_to_deform = []

        for r_image in results_mauricio:

            out_ants = 't1_%s' % r_image[0:-3]

            in_files = join(dir_mauricio, out_ants)

            if exists(join(dir_mauricio, out_ants)):
                img_to_deform.append(in_files)

        if img_to_deform:

            def_matrix = join(dir_t1, 'y_t1.nii')

            mfile_name = join(dir_mauricio, 'deformations.m')

            design_type_comp = "matlabbatch{1}.spm.util.defs.comp{1}."
            design_type_out = "matlabbatch{1}.spm.util.defs.out{1}."

            new_spm = open(mfile_name, "w")

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

            new_spm.close()

            os.system('%s batch %s' % (cat12_command, mfile_name))

        for img_ in img_to_deform:
            if exists(img_):
                os.remove(img_)