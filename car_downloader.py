# fazer requisição no site da internet

#import requests
#import geopandas as gpd
#from io import BytesIO

#def baixar_car(cod_imovel):
#    state = cod_imovel.lower()[0:2]

#    url = 'https://geoserver.car.gov.br/geoserver/sicar/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=sicar:sicar_imoveis_'+state+'&outputFormat=application/json&cql_filter=cod_imovel='+'\''+cod_imovel+'\''
#    print(url)

#    r = requests.get(url,allow_redirects=True)

#    gdf = gpd.read_file(BytesIO(r.content))

#   print(gdf)

#if __name__ == '__main__':
#    baixar_car('AC-1200435-BF161742078A40169FE13B3DF58CCF87')

#----------------------------------------------------------------------

#import geopandas as gpd
#import subprocess
#from pathlib import Path


#def baixar_car(cod_imovel):
#    uf = cod_imovel[:2].lower()

#    url = (
#        "https://geoserver.car.gov.br/geoserver/sicar/ows"
#        "?service=WFS"
#        "&version=1.0.0"
#        "&request=GetFeature"
#        f"&typeName=sicar:sicar_imoveis_{uf}"
#        "&outputFormat=application/json"
#        f"&cql_filter=cod_imovel='{cod_imovel}'"
#   )

#    arquivo_saida = Path("D:/mba_dash") / f"car_{cod_imovel}.geojson"

#    comando = [
#        "powershell",
#        "-Command",
#        f'Invoke-WebRequest -UseBasicParsing "{url}" -OutFile "{arquivo_saida}"'
#    ]

#    subprocess.run(comando, check=True)

#    gdf = gpd.read_file(arquivo_saida)

#    return gdf

#___________________________________________________________________

import geopandas as gpd
import subprocess
from pathlib import Path
from urllib.parse import urlencode


def baixar_car(cod_imovel):
    uf = cod_imovel[:2].lower()

    base_url = "https://geoserver.car.gov.br/geoserver/sicar/ows"

    params = {
        "service": "WFS",
        "version": "1.0.0",
        "request": "GetFeature",
        "typeName": f"sicar:sicar_imoveis_{uf}",
        "outputFormat": "application/json",
        "cql_filter": f"cod_imovel='{cod_imovel}'",
    }

    url = base_url + "?" + urlencode(params)

    arquivo_saida = Path("D:/mba_dash") / f"car_{cod_imovel}.geojson"

    comando = [
        "powershell",
        "-Command",
        f'Invoke-WebRequest -UseBasicParsing "{url}" -OutFile "{arquivo_saida}"'
    ]

    resultado = subprocess.run(comando, capture_output=True, text=True)

    if resultado.returncode != 0:
        raise RuntimeError(
            f"Erro ao baixar CAR.\nURL: {url}\n\nSTDOUT:\n{resultado.stdout}\n\nSTDERR:\n{resultado.stderr}"
        )

    gdf = gpd.read_file(arquivo_saida)

    return gdf






