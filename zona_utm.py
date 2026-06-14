#import geopandas as gpd
#import math

#def calcular_utm(gdf):
#    gdf = gdf.dissolve(by=None)
#    centroid = gdf.centroid.iloc[0]
#    zona = (math.floor((centroid.x+180)/6))+1
#    if centroid.y > 0:
#        epsg = zona + 32600
#    else:
#        epsg = zona + 32700
#    return epsg

#if __name__ == '__main__':
#    calcular_utm(gpd.read_file('/dados/car.geojson'))

import math

def calcular_utm(gdf):
    gdf = gdf.to_crs(epsg=4326)

    bounds = gdf.total_bounds
    lon = (bounds[0] + bounds[2]) / 2
    lat = (bounds[1] + bounds[3]) / 2

    zona = math.floor((lon + 180) / 6) + 1

    if lat >= 0:
        epsg = zona + 32600
    else:
        epsg = zona + 32700

    return epsg
