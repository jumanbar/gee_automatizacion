library(tidyverse)

# fecha_muestra = "2023-04-05" # Agua / Nubes / Sombras
# fecha_muestra = "2023-04-20" # Agua / Floraciones
fecha_muestra = '2023-04-08' # Agua / Nubes / Sombras / Floraciones
m <- read_csv(paste0("sampleClusters_", fecha_muestra, ".csv"), col_types = cols(.geo = col_skip()))

ml <- m[-1] %>%
  pivot_longer(col=-cluster, names_to = "Banda", values_to = "Rrs") %>%
  # mutate(Banda = toupper(Banda), Clase = case_when(cluster == 0 ~ "Agua", cluster == 1 ~ "Nubes", TRUE ~ "Sombras"))
  # mutate(Banda = toupper(Banda), Clase = case_when(cluster == 0 ~ "Nubes-Floracion", cluster == 1 ~ "Sombras", TRUE ~ "Agua")) # 2023-04-08
  mutate(Banda = toupper(Banda), Clase = case_when(cluster == 0 ~ "Nubes-Floracion", cluster == 1 ~ "Sombras", cluster == 2 ~ "Agua1", TRUE ~ "Agua2")) # 2023-04-08


ml %>%
  ggplot() +
  aes(Clase, Rrs, fill=Banda) +
  geom_boxplot() +
  xlab(NULL) +
  scale_fill_manual(values = c("#33cccc", "#d966ff", "#80bfff"))


ggsave(paste0("indices_x_clase_", fecha_muestra, ".png"), scale = 0.9, width = 20, height = 15, units = "cm")
