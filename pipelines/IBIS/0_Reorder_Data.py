# For using this file, you should clone the SUJETOS directory in the NEUROIMAGING DATABASE SYSTEM.
# After that, you can reorder to filter the modalities you need for you project.

import os
import zipfile
from os.path import exists, join

dir_db = "D:/IBIS_DATA/SUJETOS"
dir_ordered = "D:/IBIS_DATA/Reorder_New"

list_dirs = os.listdir(dir_db)

for i in list_dirs:

    this_dir = join(dir_db, i)
    subjects = os.listdir(this_dir)

    for j in subjects:

        subj_dir = join(this_dir, j)
        dest_dir = join(dir_ordered, j)

        for root, dirs, i_files in os.walk(subj_dir):

            for i_file in i_files:

                if i_file[-3:] == "zip" and "T1" in i_file:

                    if not exists(dest_dir):
                        os.makedirs(dest_dir)
                        print("New Patient!")

                elif i_file[-3:] == "zip" and "DTI" in i_file and "NII" in i_file:

                    if not exists(dest_dir):
                        os.makedirs(dest_dir)
                        print("New Patient!")

                    print(i_file)

                    i_file_path = join(root, i_file)
                    with zipfile.ZipFile(i_file_path, "r") as zip_ref:
                        zip_ref.extractall(dest_dir)

                elif i_file[-3:] == "zip" and "PET" in i_file and "NII" in i_file:

                    if not exists(dest_dir):
                        os.makedirs(dest_dir)
                        print("New Patient!")

                    print(i_file)

                    i_file_path = join(root, i_file)
                    with zipfile.ZipFile(i_file_path, "r") as zip_ref:
                        zip_ref.extractall(dest_dir)

# %%
