# Declare directory containing the individuals
dir_path = '/DATA/ECLIPSE/'

# Read segmentation functions and import required libraries
exec(open("/DATA/DataSHIELD_development_test_data/radiomics/scripts/imports_functions.py").read())

# Get individual names
individuals = [d for d in os.listdir(dir_path) if os.path.isdir(dir_path + '/' + d)]

# Iterate by individual
for count, ind in enumerate(individuals):
  print("Processing individual " + ind + ": " + str(count + 1) + " of " + str(len(individuals)), flush=True)
  # List available scans (only the STD's tar.gz's)
  scans = glob.glob(dir_path + "/" + ind + "/*STD*[!mask]*L2*.tar.gz")
  # Iterate over scans
  for scan in scans:
    try:
      # Decompress tarball
      tar = tarfile.open(scan, "r:gz")
      tar.extractall(dir_path + "/" + ind)
      tar.close()
      # Create mask with the decompressed dicoms
      get_and_save_masks(scan[:-7])
      # Compress mask
      with tar.open(scan[:-7] + "_mask.tar.gz","w:gz") as tarf:
        for file in os.listdir(scan[:-7] + "_mask"):
          tarf.add(scan[:-7] + "_mask/" + file, 
          arcname=os.path.basename(scan[:-7] + "_mask/" + file))
      # Remove decompressed tarball and mask
      shutil.rmtree(scan[:-7] + "_mask")
      shutil.rmtree(scan[:-7])
    except:
      print("An exception occurred while processing file: " + os.path.basename(scan))
