# Get masks from NIFTIs and save them as NIFTIs

# Read segmentation functions and import required libraries
exec(open("/DATA/DataSHIELD_development_test_data/radiomics/scripts/imports_functions.py").read())

# Path of individuals
path_niftis = "/DATA/ECLIPSE_niftis_full/"

# Get individual names
individuals = glob.glob(path_niftis + "/*STD*[!mask].nii.gz")

# Iterate by individual
for count, ind in enumerate(individuals):
  print("Processing individual " + ind + ": " + str(count + 1) + " of " + str(len(individuals)), flush=True)
  try:
    im = sitk.ReadImage(ind)
    segmentation, masked_img = generate_mask(im)
    segmentation = sitk.GetImageFromArray(segmentation)
    segmentation.CopyInformation(im)
    sitk.WriteImage(segmentation, ind[:-7] + '_mask.nii.gz')
  except:
    print("An exception occurred while processing file: " + ind)

