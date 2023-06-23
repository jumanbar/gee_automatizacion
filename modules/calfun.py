import ee

###################################################################
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
not_ndwi = ee.Image(0)

# Para sombras
BUFFER = 50
CLD_PRB_THRESH = 50
NIR_DRK_THRESH = 0.15
CLD_PRJ_DIST = 1


###################################################################

def chlorophyll(img):

    NDCI_coll = (
        img.select('B5')\
            .add(img.select('B3'))\
            .subtract(img.select('B4'))
        ).divide(
        img.select('B3')\
            .add(img.select('B4').add(img.select('B5')))
        )
    
    chlor_a_coll = ee.Image(10)\
        .pow(ee.Image(-13.25)\
            .add(ee.Image(87.04).multiply(NDCI_coll))\
            .add(ee.Image(-163.31).multiply(NDCI_coll.pow(ee.Image(2))))\
            .add(ee.Image(103.29).multiply(NDCI_coll.pow(ee.Image(3)))))
    
    out = chlor_a_coll.\
        updateMask(chlor_a_coll.lt(6000))\
        .set('system:time_start', img.get('system:time_start'))

    return out

def cdom(img):

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

def turbidez(img):

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
    clouds = ee.Image(img.get('cloud_mask')).select('probability')
    isNotCloud = clouds.lt(MAX_CLOUD_PROBABILITY)
    return img.updateMask(isNotCloud)

# The masks for the 10m bands sometimes do not exclude bad data at
# scene edges, so we apply masks from the 20m and 60m bands as well.
# Example asset that needs this operation:
# COPERNICUS/S2_CLOUD_PROBABILITY/20190301T000239_20190301T000238_T55GDP
def maskEdges(s2img):
    out = s2img.updateMask(
        s2img.select('B8A')\
            .mask()\
            .updateMask(s2img.select('B9').mask())
        )

    return out

def getPercentiles(feat_col, parameter):

    reduce_scale = 300
    if id_zona > 5:
        reduce_scale = 500

    def mapFunc(feat):
        stats = feat.reduceRegion(
            reducer = ee.Reducer.percentile(p),
            geometry = geom,
            scale = reduce_scale
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

def s2Correction(img):

    pi = ee.Image(3.141592)  # Imagen con todos los pixeles = pi

    # msi bands 
    bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']

    # rescale
    rescale = img.select(bands).divide(10000).multiply(mask_ndwi)

    # tile footprint
    footprint = rescale.geometry()

    # dem
    DEM = ee.Image('USGS/SRTMGL1_003').clip(footprint)

    # ozone
    DU = ee.ImageCollection('TOMS/MERGED')\
        .filterDate(ini_date, end_date)\
        .filterBounds(footprint).mean()

    #Julian Day
    imgDate = ee.Date(img.get('system:time_start'))
    FOY = ee.Date.fromYMD(imgDate.get('year'), 1, 1)
    JD = imgDate.difference(FOY, 'day').int().add(1)

    # earth-sun distance
    myCos = ((ee.Image(0.0172).multiply(ee.Image(JD).subtract(ee.Image(2)))).cos()).pow(2)
    cosd = myCos.multiply(pi.divide(ee.Image(180))).cos()
    d = ee.Image(1).subtract(ee.Image(0.01673)).multiply(cosd).clip(footprint)

    # sun azimuth
    SunAz = ee.Image.constant(img.get('MEAN_SOLAR_AZIMUTH_ANGLE')).clip(footprint)

    # sun zenith
    SunZe = ee.Image.constant(img.get('MEAN_SOLAR_ZENITH_ANGLE')).clip(footprint)
    cosdSunZe = SunZe.multiply(pi.divide(ee.Image(180))).cos() # in degrees
    sindSunZe = SunZe.multiply(pi.divide(ee.Image(180))).sin() # in degrees



    # sat zenith
    SatZe = ee.Image.constant(img.get('MEAN_INCIDENCE_ZENITH_ANGLE_B5')).clip(footprint)
    cosdSatZe = (SatZe).multiply(pi.divide(ee.Image(180))).cos()
    sindSatZe = (SatZe).multiply(pi.divide(ee.Image(180))).sin()

    # sat azimuth
    SatAz = ee.Image.constant(img.get('MEAN_INCIDENCE_AZIMUTH_ANGLE_B5')).clip(footprint)

    # relative azimuth
    RelAz = SatAz.subtract(SunAz)
    cosdRelAz = RelAz.multiply(pi.divide(ee.Image(180))).cos()

    # Pressure
    P = (ee.Image(101325).multiply(ee.Image(1).subtract(ee.Image(0.0000225577).multiply(DEM)).pow(5.25588)).multiply(0.01)).multiply(mask_ndwi)
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
    Ltoa = imgArr.multiply(ESUN).multiply(cosdSunZe).divide(pi.multiply(d.pow(2)))

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
    Lt = Ltoa.multiply(((Toz)).multiply((ee.Image(1).divide(cosdSunZe)).add(ee.Image(1).divide(cosdSatZe))).exp())

    # Rayleigh optical thickness
    Tr = (P.divide(Po))\
        .multiply(ee.Image(0.008569).multiply(bandCenter.pow(-4)))\
        .multiply((ee.Image(1).add(ee.Image(0.0113).multiply(bandCenter.pow(-2))).add(ee.Image(0.00013).multiply(bandCenter.pow(-4)))))

    # Specular reflection (s- and p- polarization states)
    theta_V = ee.Image(0.0000000001)
    sin_theta_j = sindSunZe.divide(ee.Image(1.333))

    theta_j = sin_theta_j.asin().multiply(ee.Image(180).divide(pi))

    theta_SZ = SunZe

    R_theta_SZ_s = (((theta_SZ.multiply(pi.divide(ee.Image(180)))).subtract(theta_j.multiply(pi.divide(ee.Image(180))))).sin().pow(2))\
        .divide((((theta_SZ.multiply(pi.divide(ee.Image(180)))).add(theta_j.multiply(pi.divide(ee.Image(180))))).sin().pow(2)))

    R_theta_V_s = ee.Image(0.0000000001)

    R_theta_SZ_p = (((theta_SZ.multiply(pi.divide(180))).subtract(theta_j.multiply(pi.divide(180)))).tan().pow(2))\
        .divide((((theta_SZ.multiply(pi.divide(180))).add(theta_j.multiply(pi.divide(180)))).tan().pow(2)))

    R_theta_V_p = ee.Image(0.0000000001)

    R_theta_SZ = ee.Image(0.5).multiply(R_theta_SZ_s.add(R_theta_SZ_p))

    R_theta_V = ee.Image(0.5).multiply(R_theta_V_s.add(R_theta_V_p))

    # Sun-sensor geometry
    theta_neg = ((cosdSunZe.multiply(ee.Image(-1))).multiply(cosdSatZe))\
        .subtract((sindSunZe).multiply(sindSatZe).multiply(cosdRelAz))

    theta_neg_inv = theta_neg.acos().multiply(ee.Image(180).divide(pi))

    theta_pos = (cosdSunZe.multiply(cosdSatZe))\
        .subtract(sindSunZe.multiply(sindSatZe).multiply(cosdRelAz))

    theta_pos_inv = theta_pos.acos().multiply(ee.Image(180).divide(pi))

    cosd_tni = theta_neg_inv.multiply(pi.divide(180)).cos() # in degrees

    cosd_tpi = theta_pos_inv.multiply(pi.divide(180)).cos() # in degrees

    Pr_neg = ee.Image(0.75).multiply((ee.Image(1).add(cosd_tni.pow(2))))

    Pr_pos = ee.Image(0.75).multiply((ee.Image(1).add(cosd_tpi.pow(2))))

    # Rayleigh scattering phase function
    Pr = Pr_neg.add((R_theta_SZ.add(R_theta_V)).multiply(Pr_pos))

    # rayleigh radiance contribution
    denom = ee.Image(4).multiply(pi).multiply(cosdSatZe)
    Lr = (ESUN.multiply(Tr)).multiply(Pr.divide(denom))

    # rayleigh corrected radiance
    Lrc = Lt.subtract(Lr)
    LrcImg = Lrc.arrayProject([0]).arrayFlatten([bands])

    ## Aerosol correction ##

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

    # Calculate aerosol type
    eps = ((((Lam_11).divide(ESUNImg.select('B12'))).log()).subtract(((Lam_10).divide(ESUNImg.select('B11'))).log()))\
        .divide(ee.Image(2190).subtract(ee.Image(1610)))

    # Calculate multiple scattering of aerosols for each band
    Lam = (Lam_11).multiply(((ESUN).divide(ESUNImg.select('B12')))).multiply((eps.multiply(ee.Image(-1))).multiply((bands_nm.divide(ee.Image(2190)))).exp())

    # diffuse transmittance
    trans = Tr.multiply(ee.Image(-1)).divide(ee.Image(2)).multiply(ee.Image(1).divide(cosdSatZe)).exp()

    # Compute water-leaving radiance
    Lw = Lrc.subtract(Lam).divide(trans)

    # water-leaving reflectance
    pw = (Lw.multiply(pi).multiply(d.pow(2)).divide(ESUN.multiply(cosdSunZe)))

    # remote sensing reflectance
    Rrs_coll = (pw.divide(pi).arrayProject([0]).arrayFlatten([bands]).slice(0, 9))

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





###################################################################
###################################################################
###################################################################
###################################################################
# PARA GESTIONAR SOMBRAS DE NUBES
# Fuente:
# https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless

def bandClouds(img):
    # Basada en maskClouds (ver Actuales)
    clouds = ee.Image(img.get('cloud_mask')).select('probability')
    isCloud = clouds.gte(MAX_CLOUD_PROBABILITY).rename('clouds')
    return img.addBands(ee.Image(isCloud))

def add_cloud_bands(img):
    # Get s2cloudless image (cloud_mask), subset the probability band.
    cld_prb = ee.Image(img.get('cloud_mask')).select('probability')

    # Condition s2cloudless (cloud_mask) by the probability threshold value.
    is_cloud = cld_prb.gt(CLD_PRB_THRESH).rename('clouds')

    # Add the cloud probability layer and cloud mask as image bands.
    return img.addBands(ee.Image([cld_prb, is_cloud]))

def add_shadow_bands(img):
    # Identify water pixels from the SCL band.
    not_water = img.select('SCL').neq(6)

    # Identify dark NIR pixels that are not water (potential cloud shadow pixels).
    SR_BAND_SCALE = 1e4
    dark_pixels = img.select('B8').lt(NIR_DRK_THRESH * SR_BAND_SCALE).multiply(not_water).rename('dark_pixels')
    # dark_pixels = img.select('B8').lt(NIR_DRK_THRESH * SR_BAND_SCALE).multiply(not_ndwi).rename('dark_pixels')

    # Determine the direction to project cloud shadow from clouds (assumes UTM projection).
    shadow_azimuth = ee.Number(90).subtract(ee.Number(img.get('MEAN_SOLAR_AZIMUTH_ANGLE')));

    # Project shadows from clouds for the distance specified by the CLD_PRJ_DIST input.
    cld_proj = (img.select('clouds').directionalDistanceTransform(shadow_azimuth, CLD_PRJ_DIST * 10)
        .reproject(**{'crs': img.select(0).projection(), 'scale': 100})
        .select('distance')
        .mask()
        .rename('cloud_transform'))

    # Identify the intersection of dark pixels with cloud shadow projection.
    shadows = cld_proj.multiply(dark_pixels).rename('shadows')

    # Add dark pixels, cloud projection, and identified shadows as image bands.
    return img.addBands(ee.Image([dark_pixels, cld_proj, shadows]))

def add_cld_shdw_mask(img):
    # Add cloud component bands.
    # img_cloud = bandClouds(img)
    img_cloud = add_cloud_bands(img)

    # Add cloud shadow component bands.
    img_cloud_shadow = add_shadow_bands(img_cloud)

    # Combine cloud and shadow mask, set cloud and shadow as value 1, else 0.
    is_cld_shdw = img_cloud_shadow.select('clouds').add(img_cloud_shadow.select('shadows')).gt(0)

    # Remove small cloud-shadow patches and dilate remaining pixels by BUFFER input.
    # 20 m scale is for speed, and assumes clouds don't require 10 m precision.
    is_cld_shdw = (is_cld_shdw.focalMin(2).focalMax(BUFFER * 2/20)
        .reproject(**{'crs': img.select([0]).projection(), 'scale': 20})
        .rename('cloudmask'))

    # Add the final cloud-shadow mask to the image.
    # return img_cloud_shadow.addBands(is_cld_shdw)
    return img_cloud_shadow.updateMask(is_cld_shdw)

###################################################################