import SimpleITK as sitk
import os
import numpy as np
from lungmask import mask
import nrrd

# Function to convert a series of DICOM files into nrrd format.
# Commands of Plastimatch are from: http://plastimatch.org/plastimatch.html#plastimatch-convert
def from_dicom_series_to_nrrd(DICOM_path, patient_id):
    dicom_dir = DICOM_path
    out_name = dicom_dir + patient_id
    os.system("plastimatch convert \
    --input %s \
    --output-img %s.nrrd" % (dicom_dir, out_name))

def generate_mask(path):
    img = sitk.ReadImage(path)
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

def  get_and_save_masks(path_nrrd_file):
    # On the one hand store ndarray with pixel values and on the other hand store header of nrrd format with geometry information
    image_data, header = nrrd.read(path_nrrd_file)
    # Get masked lungs and mask filters
    mask_filter, masked_lung = generate_mask(path_nrrd_file)
    # Check assigned dtype of the generated ndarray for the mask
    type_data = mask_filter[1][1].dtype
    print("The type of data of my mask is: %s" % type_data)
    
    # Change data to a different data type in a new object if needed
    # Data type int8 stores each value as a byte ranging from 0 to 255 and is used for data without negative values
    if type_data != "int8":
        print("Changing data type to int8")
        mask_corrected = mask_filter.astype(np.int8, copy=True)
        # Writing the mask in nrrd format
        # Index order equal to "C" to place the z axis in the right place (numpy switches z axis to first position)
        nrrd.write(path_nrrd_file[:-5] + ".mask.nrrd" , mask_corrected, header, index_order='C')
    else:
         # Writing the mask in nrrd format
        nrrd.write(path_nrrd_file[:-5] + ".mask.nrrd", mask_filter, header, index_order='C')
    
    # Writing the image segmented in nrrd format
    nrrd.write(path_nrrd_file[:-5] + ".segmentation.nrrd", masked_lung, index_order='C')
    print("Segmentation finished!")
