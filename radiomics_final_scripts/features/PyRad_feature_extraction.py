# import all required modules
import os

from radiomics import featureextractor 
import SimpleITK as sitk

import numpy as np
import nibabel as nib

import csv
import pandas as pd

import glob

from joblib import Parallel, delayed


# Create function to instantiate teh extractor
def inizialize_extractor(path_to_parameters):
    return featureextractor.RadiomicsFeatureExtractor(path_to_parameters)



# Function to print the features that will be calculated
def print_enabled_features(extractor):
    radiomic_features = list(extractor.enabledFeatures.keys())
    d = {'Enabled features': radiomic_features}
    print(pd.DataFrame(d))



# Fucntion to print the settings defined to the extractor
def print_extractor_settings(extractor):
    settings, values = list(extractor.settings.keys()), list(extractor.settings.values())
    d = {'Settings': settings, 'Values': values}
    print(pd.DataFrame(d))



# Function to create a list of patients ids
def list_patients(path_to_patients):
    #return os.listdir(path_to_patients)
    return glob.glob(path_to_patients + "/*STD*[!mask].nii.gz")



# Function to get the original image and the mask
def get_image_mask(patient, path_to_patients):
    path_original = path_to_patients + '/' + patient
    path_mask = path_to_patients + '/' + patient[:-7] + '_mask.nii.gz'
    if os.path.exists(path_mask):
      return path_original, path_mask
    else:
      print('Patient ',patient,'missing image or mask')
      return False


# Function to calculate the radiomic features of a patient
def calculate_radiomic_features(extractor, path_to_original_image, path_to_mask):
    return extractor.execute(path_to_original_image, path_to_mask)



# Function to save radiomic extraction results to a .tsv
def save_results(result, path_to_output_dir, patient):
    path_to_output_file = path_to_output_dir + '/' + patient + '.tsv'
    
    # Storing the radiomic features in the .tsv file
    with open(path_to_output_file, "w") as outfile:
        # Create the .tsv file
        csvwriter = csv.writer(outfile, delimiter='\t')
        
        # Iteration over all the values and keys of the extraction results
        for key, value in result.items():
            obj_to_write = []
            obj_to_write.append(str(key))
            obj_to_write.append(str(value))
            csvwriter.writerow(obj_to_write)
    sentence = str('Successful radiomic extraction for patient:\t' + patient)
    print(sentence)



# Function to merge all .tsv into a unique .tsv file for all patients
def merge_tsv_files(general_file, input_file, patient_id):
    df_general = pd.read_csv(general_file,header=None, sep='\t')
    df_input = pd.read_csv(input_file, header=None, sep='\t')

    df_general[patient_id] = df_input[1]
    
    df_general.to_csv(general_file, header=None, index=False, sep='\t')



# Function to generate a unique file with the radiomic features of all the patients
def generate_final_file(results, path_to_output_dir):
    path_to_final_file = path_to_output_dir + '/failed_patients.tsv'
    res = pd.DataFrame(results)
    res.to_csv(path_to_final_file , header=None, index=False, sep='\t')

# Function to print the summary of the process
def print_summary(id_list, path_to_output_dir):
    print('Radiomic features extraction have been finished')
    
    if len(id_list) == 0:
        print('All patients could be processed')
        
    else:
        print('All patients but ', len(id_list), ' were processed. The following ids correspond to the patients that may have some issues in the NIFTI input files')
        id_str = '\n'.join(id_list)
        path_to_issues_report = path_to_output_dir + '/issues_report.txt'
        with open(path_to_issues_report, "w") as issues:
            issues.write("IDs of the patients that could not be processed:\n")
            issues.write(id_str)



# Final function
def Radiomic_features(path_to_patients, path_to_output, 
                                path_to_parameters):

    # Instatntiate the extractor
    extractor = inizialize_extractor(path_to_parameters)
    print('Instatntiate the extractor: Done\n')
    
    # Print enabled parameters
    print_enabled_features(extractor)
    print('Print enabled parameters: Done\n')
    
    # Print settings and its corresponding values
    print_extractor_settings(extractor)
    print('Print settings and its corresponding values: Done\n')
    
    # Creation of a patients id list
    patients_id_list = list_patients(path_to_patients)
    print('Creation of a patients id list: Done\n')
    
    # Iteration over all patients to calculate their radiomic features
    #for patient in patients_id_list:
    #   patient = os.path.basename(patient)
    #   try:
    #       # Get path to image and mask file
    #       image, mask = get_image_mask(patient, path_to_patients)
    #       print('image:', image, '\nmask:', mask)
    #   
    #       # Calculate radiomic features
    #       result = calculate_radiomic_features(extractor, image, mask)
    #       print('\nRadiomic features claculated for patient:',patient)
    #       # Save radiomic features of the patient to a .tsv file
    #        save_results(result, path_to_output, patient)
    #        
    #        # Append patient id to the processed patients list
    #        patients_processed.append(patient)
    #        
    #    except:
    #        patients_with_error.append(patient)
    #        print('\nError occurred for patient:', patient)
          
    def parallelized_get_features(patient):
        patient = os.path.basename(patient)
        try:
            # Get path to image and mask file
            image, mask = get_image_mask(patient, path_to_patients)
            print('image:', image, '\nmask:', mask)
        
            # Calculate radiomic features
            result = calculate_radiomic_features(extractor, image, mask)
            print('\nRadiomic features claculated for patient:',patient)
            # Save radiomic features of the patient to a .tsv file
            save_results(result, path_to_output, patient)
            
        except:
            print('\nError occurred for patient:', patient)
            return patient
            

    results = Parallel(n_jobs=5)(delayed(parallelized_get_features)(i) for i in patients_id_list)
    results = [i for i in results if i]
    # Create the final .tsv with the radiomic features of all patients
    generate_final_file(results, path_to_output)    
    
    # print_summary(patients_with_error, path_to_output)
