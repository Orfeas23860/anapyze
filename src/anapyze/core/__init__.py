"""
Anapyze core processing utilities.

This module bundles all functions from:
  - processor.py
  - utils.py
"""

from .processor import (
    run_matlab_command,
    intensity_normalize_pet_histogram,
    intensity_normalize_pet_ref_region,
    histogram_matching,
    logpow_histogram_matching,
    coregister_spm,
    old_normalize_spm,
    new_normalize_spm,
    old_deformations,
    new_deformations,
    smooth_images_spm,
    cat12_segmentation_crossec,
    cat12_segmentation_longit,
    recon_all_freesurfer,
    recon_all_freesurfer_whole_cohort,
    synthstrip_skull_striping_freesurfer,
)


from .utils import (
    check_input_image_shape,
    change_image_dtype,
    resample_image_by_matrix_size,
    resample_image_by_voxel_sizes,
    remove_nan_negs,
    add_poisson_noise,
    create_mean_std_imgs,
    create_atlas_csv_from_normals_imgs,
    transform_img_to_atlas_zscores,
    estimate_fwhm_mizutani,
    spm_map_2_cohens_d,
    get_fdr_thresholds_from_spmt,
    get_tiv_from_cat12_xml_report,
    get_weighted_average_iqrs_from_cat12_xml_report,
)

__all__ = [
    # from processor.py
    "run_matlab_command",
    "intensity_normalize_pet_histogram",
    "intensity_normalize_pet_ref_region",
    "histogram_matching",
    "logpow_histogram_matching",
    "coregister_spm",
    "old_normalize_spm",
    "new_normalize_spm",
    "old_deformations",
    "new_deformations",
    "smooth_images_spm",
    "cat12_segmentation_crossec",
    "cat12_segmentation_longit",
    "recon_all_freesurfer",
    "recon_all_freesurfer_whole_cohort",
    "synthstrip_skull_striping_freesurfer",

    # from utils.py
    "check_input_image_shape",
    "change_image_dtype",
    "resample_image_by_matrix_size",
    "resample_image_by_voxel_sizes",
    "remove_nan_negs",
    "add_poisson_noise",
    "create_mean_std_imgs",
    "create_atlas_csv_from_normals_imgs",
    "transform_img_to_atlas_zscores",
    "estimate_fwhm_mizutani",
    "spm_map_2_cohens_d",
    "get_fdr_thresholds_from_spmt",
    "get_tiv_from_cat12_xml_report",
    "get_weighted_average_iqrs_from_cat12_xml_report",
]
