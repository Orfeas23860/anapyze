import os
import subprocess

def dcm_nii_dcm2niix(input_folder: str, output_folder: str, output_filename: str) -> None:
    """
    Converts a dicom folder into a nifti using dcm2niix.
    dcm2niix should be installed and added to the PATH environment variable
    :param input_folder: Input DICOM folder
    :param output_folder: Path Where the Nifti images will go
    :param output_filename: Basename for the output Nifti's
    """

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Run dcm2niix command to convert DICOM to NIfTI
    command = f"dcm2niix -o {output_folder} -f {output_filename} {input_folder}"
    subprocess.run(command, shell=True)