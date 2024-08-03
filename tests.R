library(tidyverse)

m <- jsonlite::read_json("~/gee_automatizacion/muestra.json", simplifyVector = TRUE) %>%
  as_tibble() %>%
  mutate(p = row_number())


m %>%
  ggplot() +
  aes(p, nd_date) +
  geom_col()


m %>%
  ggplot() +
  aes(p, B8) +
  geom_step()

ml <- m %>%
  pivot_longer(cols=-p, names_to = 'Band', values_to = 'Rrs')

ml %>%
  ggplot() +
  aes(p, Rrs) +
  geom_point() +
  facet_wrap(vars(Band), scales = "free_y")


ml %>%
  ggplot() +
  aes(p, Rrs) +
  geom_point() +
  scale_y_log10() +
  facet_wrap(vars(Band), scales = "free_y")

# Luminous Efficiency Function --------
# https://en.wikipedia.org/wiki/Luminous_efficiency_function
library(colorSpec)
?luminsivity.1nm$spectra[,1:4]
lef <- luminsivity.1nm$spectra[4,]

# Bandas Rojo Verde y Azul (en sentinel-2: https://sentiwiki.copernicus.eu/web/s2-mission; lambda = )
B2 <- lef['490'] # Azul
B3 <- lef['560'] # Verde
B4 <- lef['665'] # Rojo
c(B2, B3, B4)



