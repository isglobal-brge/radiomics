
# ---------------------------- #
# Radiomic features with RIA 
# ---------------------------- #


## Load libraries
library(RIA)
library(RNifti)

## ---------- First order statistics ---------- ##

path_folders <- "/Users/andrealetaalfonso/Desktop/TFG/DICOMS/rstudio-export" # path where all the folders are at
patients_list <- list.files(path_folders) # list of the name of the folders of every patient

# Compute first_order to patient i
fun <- function(i){
  
  res <- c() # vector for the results
  
  patient_path <- file.path(path_folders, i, fsep="/") # path to folder of every patient
  images_folder_names <- grep(list.files(path = patient_path), pattern='mask.nii.gz', invert=TRUE, value=TRUE) # name of nii files
  mask_folder_names <- list.files(patient_path, pattern="mask.nii.gz") # name of mask files
  images_path <- file.path(patient_path, images_folder_names, fsep="/") # path to images files
  mask_path <- file.path(patient_path, mask_folder_names, fsep="/") # path to masks files
  
  # Add tryCatch block
  pre_symbol <- NULL
  tryCatch({images = RIA::load_nifti(filename = images_path, mask_filename = mask_path)
  pre_symbol <- "blah"}, # try to load images and masks
  error = function(e) { print(e)})
  # If succeed
  if(!is.null(pre_symbol)){
    images = RIA::load_nifti(filename = images_path, mask_filename = mask_path)
    images = RIA::first_order(images) # compute first order
    radiomic_list <- RIA:::list_to_df(images$stat_fo$orig)
    name_characteristics <- rownames(radiomic_list)
    res <- RIA:::list_to_df(images$stat_fo$orig)
    res
  } else{ # if not succeed, fill values with NA
    res <- rep("NA", 44)
  }
  
}

get_radiomic_features <- function(list_patients){
  results_map <- purrr:::map(list_patients, fun) # Apply fun function to all the patients
  results <- do.call(cbind.data.frame, results_map) # results
  colnames(results) <- list_patients
  rownames(results) <- name_characteristics
  write.table(results, file="first_order.txt", sep="\t")
  results
}

# Obtain radiomic features
radiomic_features <- get_radiomic_features(patients_list)

table1 <- read.delim("first_order.txt") # read table






## ---------- Geometry-based statistics ---------- ##

path_folders <- "/Users/andrealetaalfonso/Desktop/TFG/DICOMS/rstudio-export" # path where all the folders are at
patients_list <- list.files(path_folders) # list of the name of the folders of every patient

# Compute first_order to patient i
fun <- function(i){
  
  res <- c() # vector for the results
  
  patient_path <- file.path(path_folders, i, fsep="/") # path to folder of every patient
  images_folder_names <- grep(list.files(path = patient_path), pattern='mask.nii.gz', invert=TRUE, value=TRUE) # name of nii files
  mask_folder_names <- list.files(patient_path, pattern="mask.nii.gz") # name of mask files
  images_path <- file.path(patient_path, images_folder_names, fsep="/") # path to images files
  mask_path <- file.path(patient_path, mask_folder_names, fsep="/") # path to masks files
  
  # Add tryCatch block
  pre_symbol <- NULL
  tryCatch({images = RIA::load_nifti(filename = images_path, mask_filename = mask_path)
  pre_symbol <- "blah"}, # try to load images and masks
  error = function(e) { print(e)})
  # If succeed
  if(!is.null(pre_symbol)){
    images = RIA::load_nifti(filename = images_path, mask_filename = mask_path)
    images = RIA::geometry(RIA_data_in = images, use_orig = TRUE, calc_sub = FALSE)
    radiomic_list <- RIA:::list_to_df(images$stat_geometry$orig)
    name_characteristics <- rownames(radiomic_list)
    res <- RIA:::list_to_df(images$stat_geometry$orig)
    res
  } else{ # if not succeed, fill values with NA
    res <- rep("NA", 12)
  }
  
}

get_radiomic_features <- function(list_patients){
  results_map <- purrr:::map(list_patients, fun) # Apply fun function to all the patients
  results <- do.call(cbind.data.frame, results_map) # results
  colnames(results) <- list_patients
  rownames(results) <- name_characteristics
  write.table(results, file="geometry.txt", sep="\t")
  results
}

# Obtain radiomic features
radiomic_features <- get_radiomic_features(patients_list)

table2 <- read.delim("geometry.txt") # read table






## Combine results
table1 <- as.data.frame(table1)
table2 <- as.data.frame(table2)
radiomic_features <- rbind(table1, table2)

## Export results
all_results_table <- write.table(radiomic_features, file="radiomic_features.txt", sep="\t")
read_table <- read.delim("radiomic_features.txt")


## ---------- RadAR ---------- ##

library(RadAR)

rdr.ria <- import_radiomic_table("/Users/andrealetaalfonso/Desktop/TFG/A_Project/radiomic_features.txt")
rdr.ria




