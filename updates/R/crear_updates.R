library(tidyverse)

FECHA <- gsub("-", "", Sys.Date())
# FECHA <- "20240712"
# FECHA <- "20240829"
id_parametro <- 2000
makeUpdate <- function(time_start, id_zona, percentil, id_parametro, valor) {
  paste0("UPDATE `7_zonas` SET `valor` = ", valor,
         " WHERE `time_start` = '", time_start,
         "' AND `id_zona` = ", id_zona,
         " AND `percentil` = ", percentil,
         " AND `id_parametro` = ", id_parametro,";")
}


d <-
  read_delim(
    # "updates/pedidos_csv/7 ZONAS_PARA CORREGIR BASE DE DATOS_JULIO 2024.txt",
    # "updates/pedidos_csv/7 ZONAS_PARA CORREGIR REPETIDOS BASE DE DATOS_SETIEMBRE OCTUBRE 2024_CLOROFILA_ACTUALIZADO 27-11-24.txt",
    "updates/pedidos_csv/7 ZONAS_PARA CORREGIR REPETIDOS BASE DE DATOS_SETIEMBRE OCTUBRE 2024_CLOROFILA_ACTUALIZADO 20-01-2025.txt",
    delim = "\t",
    locale = locale(decimal_mark = ","),
    escape_double = FALSE,
    trim_ws = TRUE
  ) %>%
  select(-starts_with("..."))

dfinal <- d %>%
  pivot_longer(cols = c(p10, p50, p90), names_to = "percentil", values_to = "valor") %>%
  mutate(percentil = sub("p", "", percentil),
         SQL = makeUpdate(time_start, id_zona, percentil, id_parametro, valor))

dfinal %>%
  pull(SQL) %>%
  cat(sep = "\n", file = paste0("updates/SQL/UPDATEs_7zonas_", gsub("-", "", Sys.Date()), ".sql"))






