import requests
import ee
import geemap

# Initialize Earth Engine
service_account = 'solafune@encoded-road-413508.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, './encoded-road-413508-aff6e767bbef.json')
ee.Initialize(credentials)

def mask_s2_clouds(image):
    """Masks clouds in a Sentinel-2 image using the QA band.

    Args:
        image (ee.Image): A Sentinel-2 image.

    Returns:
        ee.Image: A cloud-masked Sentinel-2 image.
    """
    qa = image.select('QA60')

    # Bits 10 and 11 are clouds and cirrus, respectively.
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    # Both flags should be set to zero, indicating clear conditions.
    mask = (
        qa.bitwiseAnd(cloud_bit_mask)
        .eq(0)
        .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    )

    return image.updateMask(mask).divide(10000)

dataset = (
    ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterDate('2020-01-01', '2023-01-01')
    # Pre-filter to get less cloudy granules.
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .map(mask_s2_clouds)
)

visualization = {
    'min': 0.0,
    'max': 0.3,
    'bands': ['B4', 'B3', 'B2'],
}

m = geemap.Map()
m.setCenter(83.277, 17.7009,17);
m.add_layer(dataset.mean(), visualization, 'RGB')
m

# Define the region of interest (ROI)
roi = ee.Geometry.Polygon(
    [[[83.25, 17.65], [83.25, 17.75], [83.3, 17.75], [83.3, 17.65], [83.25, 17.65]]]
)

# Get the mean image from the dataset
image = dataset.mean()

# Define export parameters
export_params = {
    'scale': 20,
    'region': roi
}

# Export the image to a local file
output_path = './sentinel2_image.tif'
geemap.ee_export_image(image, filename=output_path, **export_params)

print("Image exported to:", output_path)
