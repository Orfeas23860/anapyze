import json
import os
from os.path import exists, isdir, join

dir_patients = '/Volumes/txusser_data/IBIS_DATA/Reorder_New'

list_dirs = os.listdir(dir_patients)

for i in list_dirs:

    dir_subj = join(dir_patients, i)

    if isdir(dir_subj):

        files_ = os.listdir(dir_subj)

        for file_ in files_:

            if file_[0:2] == 'IN' and file_[-3:] == 'nii' and 'FDG' in file_:

                pet_in = join(dir_subj, file_)
                date = file_[-12:-4]

                pet_dir = join(dir_subj, 'fdg_%s' % date)

                if not exists(pet_dir):
                    os.makedirs(pet_dir)

                json_file = join(pet_in[0:-3] + 'json')
                with open(json_file, 'r') as file:
                    data = json.load(file)

                # Extract and print the ManufacturersModelName
                manufacturers_model_name = data['ManufacturersModelName']
                print(manufacturers_model_name)
                scanner_file = join(pet_dir, str(manufacturers_model_name))
                with open(scanner_file, 'w') as b0_file:
                    pass