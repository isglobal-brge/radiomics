from lungmask import mask
import SimpleITK as sitk
import os
import pydicom
from pydicom.data import get_testdata_files
import numpy as np
import matplotlib.pyplot as plt
import cv2
import time
import glob
import tarfile
import shutil

def get_img_sitk(path):
    return sitk.ReadImage(path)
  
def get_series_sitk(path):
    reader = sitk.ImageSeriesReader()
    reader.MetaDataDictionaryArrayUpdateOn()
    reader.LoadPrivateTagsOn()
    dicom_names = reader.GetGDCMSeriesFileNames(path)
    reader.SetFileNames(dicom_names)
    return reader.Execute(), reader

def generate_mask(img):
    segmentation = mask.apply(img)
    segmentation[segmentation > 0] = 1
    if img.GetSize()[2] > 1:
      masked_img = np.zeros((img.GetSize()[2], img.GetSize()[0], img.GetSize()[1]))
      for i in range(1, segmentation.__len__()):
        masked_img[i,:,:] = np.where(segmentation[i,:,:] == 1, sitk.GetArrayFromImage(img)[i,:,:], 0)
    else:
      masked_img = np.where(segmentation == 1, sitk.GetArrayFromImage(img)[0,:,:], 0)
      masked_img = masked_img[0,:,:]
      segmentation = segmentation[0,:,:]

    return segmentation, masked_img

def create_writer(series_reader, direction):
    writer = sitk.ImageFileWriter()
    writer.KeepOriginalImageUIDOn()
    tags_to_copy = ["0010|0010",  # Patient Name
                    "0010|0020",  # Patient ID
                    "0010|0030",  # Patient Birth Date
                    "0020|000D",  # Study Instance UID, for machine consumption
                    "0020|0010",  # Study ID, for human consumption
                    "0008|0020",  # Study Date
                    "0008|0030",  # Study Time
                    "0008|0050",  # Accession Number
                    "0008|0060"  # Modality
                    ]
    modification_time = time.strftime("%H%M%S")
    modification_date = time.strftime("%Y%m%d")
    series_tag_values = [
                            (k, series_reader.GetMetaData(0, k))
                            for k in tags_to_copy
                            if series_reader.HasMetaDataKey(0, k)] + \
                        [("0008|0031", modification_time),  # Series Time
                         ("0008|0021", modification_date),  # Series Date
                         ("0008|0008", "DERIVED\\SECONDARY"),  # Image Type
                         ("0020|000e", "1.2.826.0.1.3680043.2.1125." +
                          modification_date + ".1" + modification_time),
                         ("0020|0037",
                          '\\'.join(map(str, (direction[0], direction[3],
                                          direction[6],
                                          # Image Orientation (Patient)
                                          direction[1], direction[4],
                                          direction[7])))),
                         ("0008|103e","Processed-SimpleITK")]  # Series Description
    return writer, series_tag_values

def get_and_save_masks(series_path):
    # Get series of dicom images
    series, series_reader = get_series_sitk(series_path)
    
    # Get masked lungs and mask filters
    mask_filter, masked_lung = generate_mask(series)
    
    # Save masks
    writer, series_tag_values = create_writer(series_reader, series.GetDirection())
    
    for id in range(len(mask_filter)):
        image_slice = sitk.GetImageFromArray(mask_filter[id,:,:])
        # Tags shared by the series.
        for tag, value in series_tag_values:
            image_slice.SetMetaData(tag, value)
        # Slice specific tags.
        #   Instance Creation Date
        image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d"))
        #   Instance Creation Time
        image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S"))
        #   Image Position (Patient)
        image_slice.SetMetaData("0020|0032", '\\'.join(
          map(str, series.TransformIndexToPhysicalPoint((0, 0, id)))))
        # Instace Number
        image_slice.SetMetaData("0020|0013", str(id))
        # Check if new directory exists
        if not os.path.exists(series_path + "_mask/"):
          os.makedirs(series_path + "_mask/")
        # Write to the output directory and add the extension dcm, to force writing
        # in DICOM format.
        writer.SetFileName(series_path + "_mask/" + str(id) + ".dcm")
        writer.Execute(image_slice)
