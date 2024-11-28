# DÍAS A BORRAR DE ZONAS 1 A 3
#
# 21 DE SETIEMBRE
# 21 DE OCTUBRE
# 31 DE OCTUBRE
#
#
# DÍAS BORRAR ZONAS DE 4 A 7
#
# 21 DE SETIEMBRE
# 11 DE OCTUBRE
# 31 DE OCTUBRE
#
fechas1 <- paste(2024, stringr::str_pad(c(9, 10, 10), 2, "left", "0"), c(21, 21, 31), sep = "-")
fechas2 <- paste(2024, stringr::str_pad(c(9, 10, 10), 2, "left", "0"), c(21, 11, 31), sep = "-")

library(tidyverse)
d <- tibble(
  time_start = c(rep(fechas1, each = 3), rep(fechas2, each = 4)),
  id_zona = c(rep(1:3, 3), rep(4:7, 3))
)
View(d)

delete <- d %>%
  mutate(
    SQL = paste0("DELETE FROM `7_zonas` WHERE time_start = '", time_start, "' AND id_zona = ", id_zona, ";")
  )

FECHA <- gsub("-", "", Sys.Date())
cat(delete$SQL, sep = "\n", file = paste0("updates/SQL/DELETEs_7zonas_", FECHA, ".sql"))
