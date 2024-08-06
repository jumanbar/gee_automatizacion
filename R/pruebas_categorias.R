
d <- data.frame(
  clase = c("sombra", "agua", "floracion", "nube"),
  B2 = c(754, 935, 986, 3800),
  B3 = c(486, 792, 1074, 3742),
  B4 = c(309, 636, 519, 4037),
  B8 = c(170, 244, 4452, 4415)
  )

dl <- pivot_longer(d, cols = -clase, names_to = "Band", values_to = "Rrs")

ggplot(dl) +
  aes(clase, Rrs, color = Band) +
  geom_point(size = 5) +
  scale_color_manual(values = c("blue", "green", "red", "orange"))

d %>% mutate(
  NDVI = (B8 - B4) / (B8 + B4),
  NDBG = (B2 - B3) / (B2 + B3),
  NDBR = (B2 - B4) / (B2 + B4),
  NDWI = (B3 - B8) / (B3 + B8)
  # NDVI_inv = abs(1 / NDVI)
  ) %>%
  select(-starts_with("B")) %>%
  pivot_longer(cols = -clase, names_to = "Band", values_to = "Rrs") %>%
  ggplot() +
  aes(clase, Rrs, color = Band) +
  geom_point(size = 5)
<
