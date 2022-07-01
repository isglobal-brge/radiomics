# State directories
rad_features_directory = "/DATA/ECLIPSE_results_Params_full/"
individuals_file = "/DATA/images_to_compute_total.csv"
dest_folder = "/DATA/aux/"

# Get individuals
import pandas
import shutil
import glob
import os
df = pandas.read_csv(individuals_file, names = ["X"])

# Copy to dest folder
for index, row in df.iterrows():
  res = glob.glob(rad_features_directory + "*" + str(row["X"]) + "*L1*")
  if res!=[]:
    shutil.copyfile(res[0], dest_folder + os.path.basename(res[0]))
