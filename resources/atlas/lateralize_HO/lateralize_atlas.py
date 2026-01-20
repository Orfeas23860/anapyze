import pandas as pd
import nibabel as nib
import numpy as np
import os

def lateralize_nifti(input_path, output_path, split_x=55, left_offset=100, right_offset=200):
    """
    Lateralizes a NIfTI atlas by adding offsets to labels based on hemisphere.
    Assumes standard orientation where higher X index corresponds to Left.
    """
    print(f"Loading NIfTI: {input_path}")
    img = nib.load(input_path)
    data = img.get_fdata().astype(np.int32)
    affine = img.affine
    
    # Check orientation just to be safe in logs, though logic is hardcoded to index
    print(f"Shape: {data.shape}")
    print(f"Affine orientation: {nib.aff2axcodes(affine)}")
    
    # Split logic: x > split_x is Left
    # We only modify non-background voxels (value > 0)
    # Right hemisphere (x <= split_x): Add right_offset
    # Left hemisphere (x > split_x): Add left_offset
    
    new_data = data.copy()
    
    # Create masks
    valid_mask = data > 0
    left_mask = (np.arange(data.shape[0])[:, None, None] > split_x) & valid_mask
    right_mask = (np.arange(data.shape[0])[:, None, None] <= split_x) & valid_mask
    
    # Apply offsets
    new_data[left_mask] += left_offset
    new_data[right_mask] += right_offset
    
    print(f"Saving lateralized NIfTI to: {output_path}")
    new_img = nib.Nifti1Image(new_data, affine, header=img.header)
    nib.save(new_img, output_path)
    print("NIfTI lateralization complete.")

def lateralize_csv(input_path, output_path, left_offset=100, right_offset=200):
    """
    Lateralizes a CSV atlas definition file.
    """
    print(f"Loading CSV: {input_path}")
    # Read CSV, handling potentially missing headers or specific formats if needed
    # Based on file view, it has a header: ROI_NAME,ROI_NUM,LOBE,LOBE_NUM
    df = pd.read_csv(input_path)
    
    new_rows = []
    
    for _, row in df.iterrows():
        # Get original values
        roi_name = row['ROI_NAME']
        roi_num = int(row['ROI_NUM'])
        lobe = row['LOBE']
        lobe_num = int(row['LOBE_NUM'])
        
        # Skip empty lines if any (though pandas usually handles this)
        if pd.isna(roi_name):
            continue
            
        # Create Right entry (ID + right_offset)
        right_row = {
            'ROI_NAME': f'Right_{roi_name}',
            'ROI_NUM': roi_num + right_offset,
            'LOBE': lobe,
            'LOBE_NUM': lobe_num
        }
        new_rows.append(right_row)
        
        # Create Left entry (ID + left_offset)
        left_row = {
            'ROI_NAME': f'Left_{roi_name}',
            'ROI_NUM': roi_num + left_offset,
            'LOBE': lobe,
            'LOBE_NUM': lobe_num
        }
        new_rows.append(left_row)
        
    new_df = pd.DataFrame(new_rows)
    
    print(f"Saving lateralized CSV to: {output_path}")
    new_df.to_csv(output_path, index=False)
    print("CSV lateralization complete.")

if __name__ == "__main__":
    base_dir = '/Users/jsilva/Work/1_Projects/anapyze/resources/atlas/lateralize_HO'
    
    # File paths
    nii_in = os.path.join(base_dir, 'Harvard_Oxford_cat12_1.5mm_LZ.nii.gz')
    nii_out = os.path.join(base_dir, 'Harvard_Oxford_cat12_1.5mm_LZ_lateralized.nii.gz')
    
    csv_in = os.path.join(base_dir, 'Harvard_Oxford.csv')
    csv_out = os.path.join(base_dir, 'Harvard_Oxford_lateralized.csv')
    
    try:
        lateralize_nifti(nii_in, nii_out)
        lateralize_csv(csv_in, csv_out)
        print("Success!")
    except Exception as e:
        print(f"An error occurred: {e}")
