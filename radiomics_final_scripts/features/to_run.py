# Read segmentation functions and import required libraries
exec(open("/DATA/radiomics_final_scripts/Carlos/PyRad_feature_extraction.py").read())



Radiomic_features('/DATA/ECLIPSE_niftis_full', "/DATA/ECLIPSE_results_Params_full2/", '/DATA/radiomics_final_scripts/Carla/Parameter_files/Params.yaml')
