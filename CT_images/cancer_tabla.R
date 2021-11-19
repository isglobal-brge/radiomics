library(rvest)
library(tibble)

url.cancer <- "https://www.cancerimagingarchive.net/collections/"

tmp <- read_html(url.cancer)

tmp <- html_nodes(tmp, "table")


length(tmp)

sapply(tmp, class)

sapply(tmp, function(x) dim(html_table(x, fill = TRUE)))

cancer <- html_table(tmp[[1]])


url.img <- tmp %>% html_nodes("tr") %>%
  html_nodes("a") %>%
  html_attr("href")


img.cancer <- cancer %>% add_column(URL = url.img, .before = "Supporting Data")

write.table(x = img.cancer, file = "C:/Iker/ISGlobal/tabla_cancer.txt", sep = ",",
            row.names = FALSE, col.names = TRUE)

tabla <- read.delim(file.choose("C:/Iker/ISGlobal/tabla_cancer"))

