import os
import ee
import geemap

# Get the current working directory
wd = os.getcwd()
cred_path = os.path.join(wd, 'utils','json','solafune-424011-11884393242c.json')

# Initialize Earth Engine
service_account = 'abiya-946@solafune-424011.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, cred_path)
ee.Initialize(credentials)

def mask_s2_clouds(image):
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
    .filterDate('2017-03-28', '2024-05-20')
    # Pre-filter to get less cloudy granules.
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .map(mask_s2_clouds)
)

def create_polygon_from_center(center_coord, corner_offset):

  longitude, latitude = center_coord

  # Calculate corner coordinates
  north = longitude + corner_offset
  south = longitude - corner_offset
  east = latitude + corner_offset
  west = latitude - corner_offset

  # Create polygon coordinates
  polygon_coords = [
    (west, north),
    (west, south),
    (east, south),
    (east, north),
    (west, north)
  ]
  return polygon_coords

def download(lat, long, uid):
    # Define the region of interest (ROI)
    roi = ee.Geometry.Polygon(
        [create_polygon_from_center((long, lat), (0.0138/3))]
    )

    # Get the mean image from the dataset
    image = dataset.mean()

    # Define export parameters
    export_params = {
        'scale': 5,
        'region': roi
    }

    # Export the image to a local file
    output_path = os.path.join(wd, 'utils','tif_from_sentinel',f'sentinel2_image_{uid}.tif')
    geemap.ee_export_image(image, filename=output_path, **export_params)

    print("Image exported to:", output_path)
