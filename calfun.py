import ee
from inifun import rangoFechas

###################################################################
# Variables misc =====
# Definir estas cosas para que el VS code no ponga
# alertas todo el tiempo
id_zona = 1
zona = 'PALMAR'
geom = ee.FeatureCollection('users/brunogda/zonas_palmar_represa_dis')\
    .first()\
    .geometry()

p = [10, 50, 90]
cloud_perc = 25
cloud_perc2 = 25
MAX_CLOUD_PROBABILITY = 10

ini_date = '2023-03-01'
end_date = '2023-03-31'
mask_ndwi = ee.Image(0)

###################################################################


def chlorophyll(img: ee.image.Image) -> ee.image.Image:
    """
    Calcula la concentración de clorofila-a en una imagen utilizando el Índice de
    diferencia normalizada de clorofila (NDCI).

    img -- Objeto de imagen de Earth Engine. Representa una imagen con
    múltiples bandas, como una imagen de satélite.
    """
    NDCI_coll = (
        img.select('B5')
        .add(img.select('B3'))
        .subtract(img.select('B4'))
    ).divide(
        img.select('B3')
        .add(img.select('B4')
             .add(img.select('B5')))
    )

    chlor_a_coll = ee.Image(10)\
        .pow(ee.Image(-13.25)
             .add(ee.Image(87.04).multiply(NDCI_coll))
             .add(ee.Image(-163.31).multiply(NDCI_coll.pow(ee.Image(2))))
             .add(ee.Image(103.29).multiply(NDCI_coll.pow(ee.Image(3)))))

    out = chlor_a_coll.\
        updateMask(chlor_a_coll.lt(6000))\
        .set('system:time_start', img.get('system:time_start'))

    return out


def cdom(img: ee.image.Image) -> ee.image.Image:
    """
    Calcula el índice CDOM (Materia Orgánica Disuelta Coloreada) para una imagen de entrada.

    img -- Imagen de Earth Engine (representación de un raster)
    """
    blueRed_coll2 = img.select('B2')\
        .add(img.select('B4'))\
        .divide(ee.Image(2.0))

    sd_coll = ee.Image(-220.3).multiply(blueRed_coll2)

    sd_coll1 = sd_coll.exp()

    cdom_coll = ee.Image(25.221)\
        .multiply(sd_coll1)

    out = cdom_coll\
        .updateMask(cdom_coll.lt(30))\
        .set('system:time_start', img.get('system:time_start'))

    return out


def turbidez(img: ee.image.Image) -> ee.image.Image:
    """
    Calcula la Turbidez usando el Normalized Difference Chlorophyll Index (NDCI)

    img -- The parameter "img" is an Earth Engine image object. It is expected to have bands B5 and
    B6, which are used in the calculation of Turbidity.
    """
    NDCI_coll = img.select('B5')\
        .add(img.select('B6'))\
        .divide(ee.Image(2.0))

    turbidez_coll = ee.Image(-16.872)\
        .add(ee.Image(4442.1).multiply(NDCI_coll))

    out = turbidez_coll.\
        updateMask(turbidez_coll.lt(300))\
        .set('system:time_start', img.get('system:time_start'))

    return out


def maskClouds(img):
    """
    La función "maskClouds" toma una imagen como entrada y realiza algunas operaciones para enmascarar
    las nubes en la imagen.

    The masks for the 10m bands sometimes do not exclude bad data at
    scene edges, so we apply masks from the 20m and 60m bands as well.
    Example asset that needs this operation:
    COPERNICUS/S2_CLOUD_PROBABILITY/20190301T000239_20190301T000238_T55GDP

    :param img: El parámetro `img` es un objeto de imagen o matriz que representa una imagen de nube
    """
    clouds = ee.Image(img.get('cloud_mask')).select('probability')
    isNotCloud = clouds.lt(MAX_CLOUD_PROBABILITY)
    return img.updateMask(isNotCloud)


# The masks for the 10m bands sometimes do not exclude bad data at
# scene edges, so we apply masks from the 20m and 60m bands as well.
# Example asset that needs this operation:
# COPERNICUS/S2_CLOUD_PROBABILITY/20190301T000239_20190301T000238_T55GDP

def maskEdges(s2img):
    """
    La función enmascara los bordes de una imagen.

    :param s2img: Se espera que el parámetro de entrada `s2img` sea una imagen
    """
    out = s2img.updateMask(
        s2img.select('B8A')
        .mask()
        .updateMask(s2img.select('B9').mask())
    )

    return out


def getPercentiles(feat_col, parameter, sietez=True):
    """
    La función `getPercentiles` calcula los percentiles de una columna de características determinada en
    función de un parámetro específico.

    :param feat_col: El parámetro feat_col es la columna o característica de su conjunto de datos para
    la que desea calcular los percentiles. Podría ser una columna numérica como concentración de clorofila,
    CDOM, o cualquier otra variable continua
    :param parameter: El ID del parámetro de interés (ej: 2000 para clorofila)
    """
    if (sietez):
        reduce_scale = 300
        if id_zona > 5:
            reduce_scale = 500
    else:
        reduce_scale = None

    def mapFunc(feat):
        stats = feat.reduceRegion(
            reducer=ee.Reducer.percentile(p),
            geometry=geom,
            scale=reduce_scale
        )

        f = ee.Feature(None).set({
            'zona': zona,
            'id_zona': id_zona,
            'date': ee.Date(feat.get('system:time_start')).format(None),
            'parameter': parameter,
            'p10': stats.get('constant_p10'),
            'p50': stats.get('constant_p50'),
            'p90': stats.get('constant_p90'),
        })

        return f

    return feat_col.map(mapFunc)


def s2Correction(img: ee.image.Image) -> ee.image.Image:

    pi = ee.Image(3.141592)  # Imagen con todos los pixeles = pi

    # msi bands =====
    bands = ['B1', 'B2', 'B3', 'B4', 'B5',
             'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']

    # rescale
    rescale = img.select(bands).divide(10000).multiply(mask_ndwi)

    # tile footprint
    footprint = rescale.geometry()

    # dem
    DEM = ee.Image('USGS/SRTMGL1_003').clip(footprint)

    # ozone
    ini_date2 = rangoFechas(30, end_date)[0]
    DU = ee.ImageCollection('TOMS/MERGED')\
        .filterDate(ini_date2, end_date)\
        .filterBounds(footprint).mean()

    # Julian Day
    imgDate = ee.Date(img.get('system:time_start'))
    FOY = ee.Date.fromYMD(imgDate.get('year'), 1, 1)
    JD = imgDate.difference(FOY, 'day').int().add(1)

    # earth-sun distance =====
    myCos = ((ee.Image(0.0172).multiply(
        ee.Image(JD).subtract(ee.Image(2)))).cos()).pow(2)
    cosd = myCos.multiply(pi.divide(ee.Image(180))).cos()
    d = ee.Image(1).subtract(ee.Image(0.01673)).multiply(cosd).clip(footprint)

    # sun azimuth
    SunAz = ee.Image.constant(
        img.get('MEAN_SOLAR_AZIMUTH_ANGLE')).clip(footprint)

    # sun zenith =====
    SunZe = ee.Image.constant(
        img.get('MEAN_SOLAR_ZENITH_ANGLE')).clip(footprint)
    cosdSunZe = SunZe.multiply(pi.divide(ee.Image(180))).cos()  # in degrees
    sindSunZe = SunZe.multiply(pi.divide(ee.Image(180))).sin()  # in degrees

    # sat zenith =====
    SatZe = ee.Image.constant(
        img.get('MEAN_INCIDENCE_ZENITH_ANGLE_B5')).clip(footprint)
    cosdSatZe = (SatZe).multiply(pi.divide(ee.Image(180))).cos()
    sindSatZe = (SatZe).multiply(pi.divide(ee.Image(180))).sin()

    # sat azimuth
    SatAz = ee.Image.constant(
        img.get('MEAN_INCIDENCE_AZIMUTH_ANGLE_B5')).clip(footprint)

    # relative azimuth =====
    RelAz = SatAz.subtract(SunAz)
    cosdRelAz = RelAz.multiply(pi.divide(ee.Image(180))).cos()

    # Pressure
    P = (ee.Image(101325).multiply(ee.Image(1).subtract(ee.Image(
        0.0000225577).multiply(DEM)).pow(5.25588)).multiply(0.01)).multiply(mask_ndwi)
    Po = ee.Image(1013.25)

    # esun
    ESUN = ee.Image(ee.Array([
        ee.Image(img.get('SOLAR_IRRADIANCE_B1')),
        ee.Image(img.get('SOLAR_IRRADIANCE_B2')),
        ee.Image(img.get('SOLAR_IRRADIANCE_B3')),
        ee.Image(img.get('SOLAR_IRRADIANCE_B4')),
        ee.Image(img.get('SOLAR_IRRADIANCE_B5')),
        ee.Image(img.get('SOLAR_IRRADIANCE_B6')),
        ee.Image(img.get('SOLAR_IRRADIANCE_B7')),
        ee.Image(img.get('SOLAR_IRRADIANCE_B8')),
        ee.Image(img.get('SOLAR_IRRADIANCE_B8A')),
        ee.Image(img.get('SOLAR_IRRADIANCE_B11')),
        ee.Image(img.get('SOLAR_IRRADIANCE_B12'))
    ])).toArray().toArray(1)

    ESUN = ESUN.multiply(ee.Image(1))

    ESUNImg = ESUN.arrayProject([0]).arrayFlatten([bands])

    # create empty array for the images
    imgArr = rescale.select(bands).toArray().toArray(1)

    # pTOA to Ltoa
    Ltoa = imgArr.multiply(ESUN).multiply(cosdSunZe)\
        .divide(pi.multiply(d.pow(2)))

    # band centers
    bandCenter = ee.Image(443).divide(1000)\
        .addBands(ee.Image(490).divide(1000))\
        .addBands(ee.Image(560).divide(1000))\
        .addBands(ee.Image(665).divide(1000))\
        .addBands(ee.Image(705).divide(1000))\
        .addBands(ee.Image(740).divide(1000))\
        .addBands(ee.Image(783).divide(1000))\
        .addBands(ee.Image(842).divide(1000))\
        .addBands(ee.Image(865).divide(1000))\
        .addBands(ee.Image(1610).divide(1000))\
        .addBands(ee.Image(2190).divide(1000))\
        .toArray().toArray(1)

    # ozone coefficients
    koz = ee.Image(0.0039)\
        .addBands(ee.Image(0.0213))\
        .addBands(ee.Image(0.1052))\
        .addBands(ee.Image(0.0505))\
        .addBands(ee.Image(0.0205))\
        .addBands(ee.Image(0.0112))\
        .addBands(ee.Image(0.0075))\
        .addBands(ee.Image(0.0021))\
        .addBands(ee.Image(0.0019))\
        .addBands(ee.Image(0))\
        .addBands(ee.Image(0))\
        .toArray().toArray(1)

    # Calculate ozone optical thickness
    Toz = koz.multiply(DU).divide(ee.Image(1000))

    # Calculate TOA radiance in the absense of ozone
    Lt = Ltoa.multiply(((Toz)).multiply(
        (ee.Image(1).divide(cosdSunZe)).add(ee.Image(1).divide(cosdSatZe))).exp())

    # Rayleigh optical thickness
    Tr = (P.divide(Po))\
        .multiply(ee.Image(0.008569).multiply(bandCenter.pow(-4)))\
        .multiply((ee.Image(1).add(ee.Image(0.0113).multiply(bandCenter.pow(-2))).add(ee.Image(0.00013).multiply(bandCenter.pow(-4)))))

    # Specular reflection (s- and p- polarization states)
    theta_V = ee.Image(0.0000000001)
    sin_theta_j = sindSunZe.divide(ee.Image(1.333))

    theta_j = sin_theta_j.asin().multiply(ee.Image(180).divide(pi))

    theta_SZ = SunZe

    # THETA =====
    R_theta_SZ_s = (((theta_SZ.multiply(pi.divide(ee.Image(180)))).subtract(theta_j.multiply(pi.divide(ee.Image(180))))).sin().pow(2))\
        .divide((((theta_SZ.multiply(pi.divide(ee.Image(180)))).add(theta_j.multiply(pi.divide(ee.Image(180))))).sin().pow(2)))

    R_theta_V_s = ee.Image(0.0000000001)

    R_theta_SZ_p = (((theta_SZ.multiply(pi.divide(180))).subtract(theta_j.multiply(pi.divide(180)))).tan().pow(2))\
        .divide((((theta_SZ.multiply(pi.divide(180))).add(theta_j.multiply(pi.divide(180)))).tan().pow(2)))

    R_theta_V_p = ee.Image(0.0000000001)

    R_theta_SZ = ee.Image(0.5).multiply(R_theta_SZ_s.add(R_theta_SZ_p))

    R_theta_V = ee.Image(0.5).multiply(R_theta_V_s.add(R_theta_V_p))

    # Sun-sensor geometry ======
    theta_neg = ((cosdSunZe.multiply(ee.Image(-1))).multiply(cosdSatZe))\
        .subtract((sindSunZe).multiply(sindSatZe).multiply(cosdRelAz))

    theta_neg_inv = theta_neg.acos().multiply(ee.Image(180).divide(pi))

    theta_pos = (cosdSunZe.multiply(cosdSatZe))\
        .subtract(sindSunZe.multiply(sindSatZe).multiply(cosdRelAz))

    theta_pos_inv = theta_pos.acos().multiply(ee.Image(180).divide(pi))

    cosd_tni = theta_neg_inv.multiply(pi.divide(180)).cos()  # in degrees

    cosd_tpi = theta_pos_inv.multiply(pi.divide(180)).cos()  # in degrees

    Pr_neg = ee.Image(0.75).multiply((ee.Image(1).add(cosd_tni.pow(2))))

    Pr_pos = ee.Image(0.75).multiply((ee.Image(1).add(cosd_tpi.pow(2))))

    # Rayleigh scattering phase function =====
    Pr = Pr_neg.add((R_theta_SZ.add(R_theta_V)).multiply(Pr_pos))

    # rayleigh radiance contribution
    denom = ee.Image(4).multiply(pi).multiply(cosdSatZe)
    Lr = (ESUN.multiply(Tr)).multiply(Pr.divide(denom))

    # rayleigh corrected radiance
    Lrc = Lt.subtract(Lr)
    LrcImg = Lrc.arrayProject([0]).arrayFlatten([bands])

    # Aerosol correction =====

    # Bands in nm
    bands_nm = ee.Image(443)\
        .addBands(ee.Image(490))\
        .addBands(ee.Image(560))\
        .addBands(ee.Image(665))\
        .addBands(ee.Image(705))\
        .addBands(ee.Image(740))\
        .addBands(ee.Image(783))\
        .addBands(ee.Image(842))\
        .addBands(ee.Image(865))\
        .addBands(ee.Image(0))\
        .addBands(ee.Image(0))\
        .toArray().toArray(1)

    # Lam in SWIR bands
    Lam_10 = LrcImg.select('B11')
    Lam_11 = LrcImg.select('B12')

    # Calculate aerosol type ======
    eps = ((((Lam_11).divide(ESUNImg.select('B12'))).log()).subtract(((Lam_10).divide(ESUNImg.select('B11'))).log()))\
        .divide(ee.Image(2190).subtract(ee.Image(1610)))

    # Calculate multiple scattering of aerosols for each band ======
    Lam = (Lam_11).multiply(((ESUN).divide(ESUNImg.select('B12')))).multiply(
        (eps.multiply(ee.Image(-1))).multiply((bands_nm.divide(ee.Image(2190)))).exp())

    # diffuse transmittance
    trans = Tr.multiply(ee.Image(-1)).divide(ee.Image(2)
                                             ).multiply(ee.Image(1).divide(cosdSatZe)).exp()

    # Compute water-leaving radiance
    Lw = Lrc.subtract(Lam).divide(trans)

    # water-leaving reflectance
    pw = (Lw.multiply(pi).multiply(d.pow(2)).divide(ESUN.multiply(cosdSunZe)))

    # remote sensing reflectance
    Rrs_coll = (pw.divide(pi).arrayProject(
        [0]).arrayFlatten([bands]).slice(0, 9))

    out = (Rrs_coll.set('system:time_start', img.get('system:time_start')))

    # # atmospheric parameters
    # H2O = img.getInfo()['properties']['PRODUCTS']['1']['PROCESSING_LEVEL_CORRECTED']['IMAGE_ATTRIBUTES']['WATER_VAPOR_RETRIEVAL']['mean']
    # O3 = DU.getInfo()['properties']['total_ozone']['value']

    # # run 6S
    # result = run6S(rescale, DEM, H2O, O3, d, 'Sentinel-2', 'Continental', False)

    # # extract water leaving reflectance
    # Rrs = ee.Image(result).select('Rrs')

    # # add original band names to the output
    # output = Rrs.rename(bands)

    # return output
    return out
