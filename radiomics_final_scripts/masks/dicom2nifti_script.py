import dicom2nifti
import os
import glob
import tarfile
import shutil
import pandas as pd

# State directories
dicoms_directory = "/DATA/ECLIPSE"
niftis_directory = "/DATA/ECLIPSE_niftis_full/"
eclipse_file = "/DATA/eclipse.txt"
control_string = "Non-smoker Controls"
control_string_omit = "Smoker Controls"

# Read Eclipse txt
eclipse = pd.read_csv(eclipse_file, sep="\t")

# Get individual names
individuals = [d for d in os.listdir(dicoms_directory) if os.path.isdir(dicoms_directory + "/" + d)]

# Iterate by individual
for count, ind in enumerate(individuals):
  print("Processing individual " + ind + ": " + str(count + 1) + " of " + str(len(individuals)), flush=True)
  # List available scans (only the STD's tar.gz's) also, only the L1
  scans = glob.glob(dicoms_directory + "/" + ind + "/*STD*[!mask].tar.gz")
  if len(scans) == 0:
    print("Individual " + ind + " does not have STD images")
    continue
  # Detect if individual is case or control
  # We use the variable 'control_string' to read from the eclipse.txt file 
  # which are the controls, everything else is considered a case
  #indiv_type = eclipse[eclipse['id'] == int(ind)]
  #if len(indiv_type) == 0:
  #  print("Individual " + ind + " not found on the Eclipse.txt")
  #  continue
  #type = indiv_type.iloc[0]['TRTGRP']
  #if type == control_string:
  #  is_control = True
  #elif type == control_string_omit:
  #  print("Individual " + ind + " omitted")
  #  continue
  #else:
  #  is_control = False
  is_control = True
  # Control handle
  if is_control:
    # Decompress scan
    for scan in scans:
      try:
        tar = tarfile.open(scan, "r:gz") 
        tar.extractall(dicoms_directory + '/' + ind)
        tar.close()
        # Convert scan and place in aux directory
        dicom2nifti.convert_directory(scan[:-7], niftis_directory + 'aux')
        # Rename file from aux directory
        os.rename(niftis_directory + 'aux/' + os.listdir(niftis_directory + 'aux')[0], niftis_directory + 'aux/' + os.path.basename(scan)[:-7] + '.nii.gz')
        # Move file from aux directory and move to case directory
        shutil.move(niftis_directory + 'aux/' + os.listdir(niftis_directory + 'aux')[0], niftis_directory)
      except:
        print("An exception occurred while processing file: " + scan)
        shutil.rmtree(niftis_directory + "aux")
        os.makedirs(niftis_directory + "aux")
  