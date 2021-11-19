library(RIA)
library(RadAR)
library(RNifti)

# Visualizar imagen

image <- readNifti("C:/Iker/ISGlobal/COVID-19/coronacases_001.nii.gz")
view(image)

# Cargar cada imagen con su máscara

corona1 <- RIA::load_nifti(filename = "C:/Iker/ISGlobal/COVID-19/coronacases_001.nii.gz",
                           mask_filename = "C:/Iker/ISGlobal/COVID-19-MASK/coronacases_001.nii.gz")
corona2 <- RIA::load_nifti(filename = "C:/Iker/ISGlobal/COVID-19/coronacases_002.nii.gz",
                           mask_filename = "C:/Iker/ISGlobal/COVID-19-MASK/coronacases_002.nii.gz")
control1 <- RIA::load_nifti(filename = "C:/Iker/ISGlobal/COVID-19/radiopaedia_10_85902_1.nii.gz",
                            mask_filename = "C:/Iker/ISGlobal/COVID-19-MASK/radiopaedia_10_85902_1.nii.gz")
control2 <- RIA::load_nifti(filename = "C:/Iker/ISGlobal/COVID-19/radiopaedia_10_85902_3.nii.gz",
                            mask_filename = "C:/Iker/ISGlobal/COVID-19-MASK/radiopaedia_10_85902_3.nii.gz")

# Calcular las características de tipo first-order

corona1 <- RIA::first_order(corona1)
corona2 <- RIA::first_order(corona2)
control1 <- RIA::first_order(control1)
control2 <- RIA::first_order(control2)

# Crear una tabla con las características para cada individuo

stats_corona1 <- RIA:::list_to_df(corona1$stat_fo$orig)
stats_corona2 <- RIA:::list_to_df(corona2$stat_fo$orig)
stats_control1 <- RIA:::list_to_df(control1$stat_fo$orig)
stats_control2 <- RIA:::list_to_df(control2$stat_fo$orig)

stats_global <- data.frame(corona1 = stats_corona1,
                           corona2 = stats_corona2,
                           control1 = stats_control1,
                           control2 = stats_control2)

# Cambiar el nombre de las columnas para cada individuo

colnames(stats_global) <- c("corona1", "corona2", "control1", "control2")

head(stats_global)

# Guardar el archivo de la tabla

write.table(stats_global, file = "C:/Iker/ISGlobal/Covid_features.txt", sep = "\t")

# Importar las características

rdr <- import_radiomic_table(file = "C:/Iker/ISGlobal/DataSHIELD_utils/Radiomics_features_extraction/stats_global.tsv")


# Crear una tabla con el identificador de cada paciente y su estado

clinical <- data.frame(PatientID = c("corona1", "corona2", "corona3", "corona4", "corona5",
                                     "corona6", "corona7", "corona8", "corona9", "corona10",
                                     "control1", "control2", "control3", "control5",
                                     "control6", "control7", "control9", "control10"),
                       covid_status = c("covid", "covid", "covid", "covid", "covid",
                                        "covid", "covid", "covid", "covid", "covid",
                                        "no_covid", "no_covid", "no_covid",
                                        "no_covid", "no_covid", "no_covid", "no_covid", "no_covid"))
colData(rdr) <- cbind(colData(rdr), clinical)

#

features.nodup <- assays(rdr)$values[-which(apply(assays(rdr)$values, 1, function(x){length(unique(x)) == 1})),]

rdr_2 <- SummarizedExperiment::SummarizedExperiment(assays = list(values = features.nodup), 
                                                    rowData = data.frame(feature_name = rownames(features.nodup)), colData = colnames(features.nodup), 
                                                    metadata = metadata(rdr))

colData(rdr_2) <- cbind(colData(rdr_2), clinical)

# Ver la correlación de las features

plot_correlation_matrix(rdr = rdr_2, 
                        method_correlation = "spearman", 
                        view_as = "heatmap", 
                        which_data = "normal")

# 

rdr_2 <- scale_feature_values(rdr = rdr_2, method = "minmax")


# AGRUPAMIENTO DE CARACTERÍSTICAS

rdr_2 <- do_hierarchical_clustering(rdr = rdr_2,
                                    which_data = "scaled",
                                    method_dist_col = "correlation.spearman")

plot_heatmap_hcl(rdr = rdr_2, 
                 annotation_tracks = c("covid_status"))




