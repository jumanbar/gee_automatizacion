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
# ?luminsivity.1nm
luminsivity.1nm$spectra[,1:4]
lef <- luminsivity.1nm$spectra[4,]

# Bandas Rojo Verde y Azul (en sentinel-2: https://sentiwiki.copernicus.eu/web/s2-mission)
B2 <- lef['490'] # Azul
B3 <- lef['560'] # Verde
B4 <- lef['665'] # Rojo
c(B2, B3, B4)


# Features test ---------
fecha_muestra = "2023-04-05" # Agua / Nubes / Sombras
fecha_muestra = "2023-04-20" # Agua / Floraciones
m <- jsonlite::read_json("~/gee_automatizacion/features_test.json", simplifyVector = TRUE) %>%
  as_tibble() %>%
  mutate(p = row_number())

ml <- m %>%
  pivot_longer(cols=-p, names_to = 'Band', values_to = 'Rrs') %>%
  mutate(Band = toupper(Band))

ml %>%
  ggplot() +
  aes(p, Rrs) +
  geom_point(shape = 21, alpha = 0.8, fill = "darkgrey") +
  facet_wrap(vars(Band)) +
  xlab("Percentil (%)")
  # facet_wrap(vars(Band), scales = "free_y")

ggsave(paste0("acum_indices_agua_", fecha_muestra, ".png"), scale = 0.9, width = 20, height = 15, units = "cm")

m <- jsonlite::read_json("~/gee_automatizacion/muestra_agua_ndwi.json"), simplifyVector = TRUE) %>%
  as_tibble() %>%
  mutate(p = row_number())

ml <- m %>%
  pivot_longer(cols=-p, names_to = 'Band', values_to = 'Rrs') %>%
  mutate(Band = case_when(
    Band == "nd" ~ "NDWI_median",
    Band == "nd_date" ~ "NDWI"
    ))

ml %>%
  ggplot() +
  aes(p, Rrs, fill = Band, color = Band) +
  geom_point(shape = 21, alpha = 0.8) +
  # facet_wrap(vars(Band)) +
  xlab("Percentil (%)") +
  scale_x_continuous(breaks = c(0, 20, 40, 60, 80, 100))
