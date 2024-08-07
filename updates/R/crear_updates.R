library(tidyverse)

d <-
  read_delim(
    "updates/pedidos_csv/7 ZONAS_PARA CORREGIR BASE DE DATOS_JULIO 2024.txt",
    delim = "\t",
    escape_double = FALSE,
    trim_ws = TRUE
  ) %>%
  select(-starts_with("..."))

makeUpdate <- function(time_start, id_zona, percentil, valor) {
  paste0("UPDATE 7_zonas SET valor = ", valor,
         " WHERE time_start = '", time_start,
         "' AND id_zona = ", id_zona,
         " AND percentil = ", percentil,
         " AND id_parametro = 2000;")
}

dfinal <- d %>%
  pivot_longer(cols = c(p10, p50, p90), names_to = "percentil", values_to = "valor") %>%
  mutate(percentil = sub("p", "", percentil),
         SQL = makeUpdate(time_start, id_zona, percentil, valor))

dfinal %>%
  pull(SQL) %>%
  cat(sep = "\n", file = paste0("updates/SQL/UPDATEs_7zonas_", gsub("-", "", Sys.Date()), ".sql"))






