#  ----------------------
# |     INSTRUCTIONS     |
#  ----------------------
#
# This program allows to correct the individual tsv files from our Pyradiomics analysis into a format readable by RadAR function: import_pyradiomics.
# The output would be the same individual files (not merged) but with the format corrected in order to create the radar object.
# So, our input and the output are directories containing those files.
#
# 1. Modify the 'test_files_path' variable with the input path where your individual tsv files with Pyradiomics' results are located
# 2. Also select the the output path in 'new_path' variable
# 3. The variable 'files_to_change' is printed because sometimes in the list can appear a hidden file like '.DS_Store'. 
# If this is the case, then iterate from index 1 in 'range(1,len(files_to_change))'. Otherwise use index 0.
# 4. Finally, you can use the sample ID you want in the new_line variable that will be appended in the end of the process.
# It should be placed in the 'filename' variable.
#
# Additionally, there is a checkpoint to be sure that when the format is being corrected there are no NaN. 
# Otherwise, a detailed warning massage arises.
#
#
#
#
#  ----------------------
# |       PROGRAM        |
#  ----------------------
import os
import glob
from os import walk
import pandas as pd
import csv
import time

test_files_path = "/Users/carla/Documents/Master Bioinformatics UAB/Prácticas Radiomics/Radiomic features/Results_rfeatures/results/test/"
new_path = "/Users/carla/Documents/Master Bioinformatics UAB/Prácticas Radiomics/Radiomic features/Results_rfeatures/results/"


def change_floats_pyradiomics_table(dataframe, filename):
    # Group columns to a single data type by transposing
    df_changed = dataframe.T
    
    # Get the number of columns
    n_columns = df_changed.shape[1]
    # Create a list with columns having strings and not floats
    avoid_cols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14, 15, 16, 17, 20, 21, 22, 23, 27, 28, 29, 32, 33]
    
    # Iterate over columns of transposed data frame
    for i in range(n_columns):
        if i not in avoid_cols:
            df_changed.iloc[1,i] = pd.to_numeric(df_changed.iloc[1,i], errors='coerce')
            #print(df_changed.iloc[1,i])
        else: 
            continue
    
    # Check if coercion worked properly
    n_nan_values = df_changed.isnull().sum().sum()        

    if n_nan_values == 0:
        print("File %s correctly processed" % (filename))
    else:
        print("Some NaN were found in %s: %d" % (filename, n_nan_values))
    
    return df_changed


files_to_change = []
for (dirpath, dirnames, filenames) in walk(test_files_path):
    # This would be to append all the filanames listed in that directory
    files_to_change.extend(filenames)
    root = dirpath

# Print the list of files to be sure that in the list is not any hidden file like '.DS_Store'. 
# If this is the case, then iterate from index 1. Otherwise use index 0.
print(files_to_change)

# Iterate over files to correct format for Pyradiomics tables in order to be recognised by RadAR
for file in range(1,len(files_to_change)):
    df_original = pd.read_csv(root + files_to_change[file], header=None, sep='\t')
    # Replace "-" for "."
    df_original.iloc[:, 0] = df_original.iloc[:, 0].str.replace('-','.')
    # Start transforming floats to floats
    df_changed = change_floats_pyradiomics_table(df_original, files_to_change[file])
    # Add additional lines for Pyradiomics format
    df_changed = df_changed.T
    id_patient = files_to_change[file][:-31]
    filename = files_to_change[file]
    new_line = pd.DataFrame(data={0: ["PAZ","PAR","ROI_name","Image","Mask"], 1:[id_patient, "Na", "Na", "Na", filename]})
    df_changed = pd.concat([new_line, df_changed])
    # Transpose one more time
    df_changed = df_changed.T
    df_changed.to_csv(new_path + files_to_change[file][:-4] + ".csv", header=None, index=False, sep=',', float_format=None, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

print("Done")
