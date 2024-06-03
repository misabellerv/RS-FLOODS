import ee
import folium
import collections
import geemap
import geopandas
import geemap.colormaps as cm
from google.colab import drive
import time

ee.Authenticate()
ee.Initialize(project='rs-floods')

Map = geemap.Map(basemap="HYBRID")

point = ee.Geometry.Point([-53.72, -29.08])

Map.centerObject(point,6)

geometry = ee.Geometry.Rectangle([-52.251113,-31.833254, -51.251357,-30.776636])

roi = ee.Feature(geometry, {}).geometry()

Map.addLayer(ee.Image().paint(roi, 0, 3), {
             'palette': 'summer'}, 'ROI TEST')

collectionVH = (ee.ImageCollection('COPERNICUS/S1_GRD')
              .filter(ee.Filter.eq('instrumentMode', 'IW'))
              .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
              .filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))
              .filterBounds(roi)
              .select('VH').map(lambda image: image.clip(roi))
              )

beforeVH = collectionVH.filterDate('2023-01-01', '2023-12-30').mosaic()
afterVH = collectionVH.filterDate('2024-05-05', '2024-05-14').mosaic()

Map.centerObject(roi, 7)
Map.addLayer(beforeVH, {"min":-25,"max":0}, 'Before flood VH', 0)
Map.addLayer(afterVH, {"min":-25,"max":0}, 'After flood VH', 0)

SMOOTHING_RADIUS = 50

beforeVH_filtered = beforeVH.focal_mean(SMOOTHING_RADIUS, 'circle', 'meters')
afterVH_filtered = afterVH.focal_mean(SMOOTHING_RADIUS, 'circle', 'meters')


differenceVH = afterVH_filtered.divide(beforeVH_filtered)
Map.addLayer(differenceVH, {"min": 0, "max":2}, 'difference VH filtered', 0)

DIFF_UPPER_THRESHOLD = 1.5
differenceVH_thresholded = differenceVH.gt(DIFF_UPPER_THRESHOLD)
Map.addLayer(differenceVH_thresholded.updateMask(differenceVH_thresholded),{"palette":"0000FF"},'flooded areas - blue',1)

Map