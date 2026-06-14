import os

os.environ["PROJ_LIB"] = r"C:\Users\joaoc\anaconda3\envs\mba_car\Library\share\proj"

import streamlit as st

#Faz com que o dashboard utilize toda a largura disponível da tela,ampliando a área de visualização de mapas, tabelas e gráficos.
st.set_page_config(
    page_title="MBA Inteligência em dados ambientais",
    layout="wide")

import geopandas as gpd
import pandas as pd
import plotly.express as px
from pyproj import datadir
import folium 
from streamlit_folium import folium_static,st_folium
# from car_downloader import baixar_car
from zona_utm import calcular_utm

# Bibliotecas: 
# streamlit (fornecida pelo google) -> Framework de desenvolvimento de dashbords interativos 
# plotly -> Biblioteca de plotagem de gráfico
# folium -> Biblioteca de confecção de mapas 
# treamlit_folium -> Bibliotecas de integração do streamlit com o folium

datadir.set_data_dir(
    r"C:\Users\joaoc\anaconda3\envs\mba_dashboards\Library\share\proj"
)

# Funções de disposição de elementos na tela
st.title('MBA Inteligência em dados ambientais') 
st.write('') # adcidonar espaço entre o título e as colunas no dashboards
st.write('')
st.sidebar.title('Menu')

# Upload de um arquivo
arquivo_subido = st.sidebar.file_uploader(label='Selecione um arquivo')

compacto = st.sidebar.checkbox(label='Ativar modo compacto')

# Checagem para saber se o arquivo foi sibido, se o arquivo não foi subido o progra vai cair la embaixo no "ELSE" não fazendo a leitura que foi definido em if

EMBARGO = 'dados/embargos/adm_embargo_a.shp'
DESMATAMENTO = 'dados/prodes/prodes-001.parquet'
TIS = 'dados/tis_poligonais/tis.parquet'

if arquivo_subido:
    poligono_analise = gpd.read_file(arquivo_subido)
    epsg = calcular_utm(poligono_analise)
  
if arquivo_subido and not compacto:

    # Elemento de seleção da visualização
    elemento=st.sidebar.radio('Selecione o elemento a ser visualizado',options=['Mapa','Gráfico','Resumo','Cabeçalho'])

    # Leitura do arquivo na forma de um geodataframe
    gdf = poligono_analise

    @st.cache_resource
    def abrir_embargo():
        gdf_embargo = gpd.read_file(EMBARGO)
        return gdf_embargo
    
    @st.cache_resource
    def abrir_desmatamento():
        gdf_desmat = gpd.read_parquet(DESMATAMENTO)
        return gdf_desmat
    
    @st.cache_resource
    def abrir_tis():
        gdf_ti = gpd.read_parquet(TIS)
        return gdf_ti
    
    gdf_embargo = abrir_embargo()
    gdf_desmat = abrir_desmatamento()
    gdf_ti = abrir_tis()

    #st.dataframe(gdf_embargo.head())

    gdf_embargo = gdf_embargo.drop(columns=['nom_pessoa','cpf_cnpj_i','cpf_cnpj_s','end_pessoa','des_bairro','num_cep','num_fone','data_tad','dat_altera','data_cadas','data_geom','dt_carga'])
    
    entrada_embargo = gpd.sjoin(gdf_embargo,gdf,how='inner',predicate='intersects')
    entrada_desmat = gpd.sjoin(gdf_desmat,gdf,how='inner',predicate='intersects')
    entrada_ti = gpd.sjoin(gdf_ti,gdf,how='inner',predicate='intersects')
    

    # Conversão do geodataframe em um dataframe
    df_embargo = pd.DataFrame(entrada_embargo).drop(columns=['geometry'])
    df_desmat = pd.DataFrame(entrada_desmat).drop(columns=['geometry'])
    df_ti = pd.DataFrame(entrada_ti).drop(columns=['geometry'])
    

    #st.write(gdf) -- transformado em comentário para remover do dashbords a tabela indesejada, se quiser colocar em visualização no dashbords basta remover o #
    
    # Criar funções para separar os elementos
    def resumo():
        # Divisão em colunas para melhor visualização
        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(df_embargo,height=320)
            st.dataframe(df_desmat,height=320)
            st.dataframe(df_ti,height=320)
        with col2:
            st.dataframe(df_embargo.describe(),height=320)
            st.dataframe(df_desmat.describe(),height=320)
            st.dataframe(df_ti.describe(),height=320)

    def cabecalho():
        st.subheader('Dados de embargo')
        st.dataframe(df_embargo)
        st.subheader('Dados de desmatamento')
        st.dataframe(df_desmat)
        st.subheader('Dados de Terras Indígenas')
        st.dataframe(df_ti)
    
    def grafico():
        col1_gra,col2_gra,col3_gra,col4_gra= st.columns(4)
        # Seleção do tipo de gráfico e uma opção padrão(utilizando o "index")
        tema_grafico = col1_gra.selectbox('Selecione o tema do gráfico',options=['Embargo','Desmatamento','Terras Indígenas'])
        
        if tema_grafico == 'Embargo':
            df_analisado = df_embargo
        elif tema_grafico == 'Desmatamento':
            df_analisado = df_desmat
        elif tema_grafico == 'Terras Indígenas':
            df_analisado = df_ti
    

        tipo_grafico = col2_gra.selectbox('Selecione o tipo de gráfico',options=['box','bar','line','scatter','violin','histogram'],index=5)
        # Plotagem da função utilizando o plotly express
        plot_func = getattr(px, tipo_grafico)
        # Criação de opções dos eixos x e y com opção padrão
        x_val = col3_gra.selectbox('Selecione o eixo x',options=df_analisado.columns,index=4)

        y_val = col4_gra.selectbox('Selecione o eixo y',options=df_analisado.columns,index=3)
        # Cria a plotagem do gráfico
        plot = plot_func(df_analisado,x=x_val,y=y_val)
        # Faz a plotagem
        st.plotly_chart(plot, use_container_width=True)

    def mapa():
        # Criar um mapa e seleciona algumas opções
        m = folium.Map(location=[-14,-54], zoom_start=4, control_scale=True, tiles=None)

        ###inicio do codigo para inserir o google satelite
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Satélite",
            overlay=False,
            control=True
        ).add_to(m)

        folium.TileLayer(
            "OpenStreetMap"
        ).add_to(m)
        ###fim do codigo para inserir o google satelite

        # Deleta Colunas do geodataframe: gdf1 = entrada_embargo.drop(columns=['dat_criaca','data_atual'], errors='ignore') 
        
        def style_function_entrada(x): return{
            'fillColor':'blue',
            'color':'black',
            'weight':0,
            'fillOpacity':0.3
        }
        
        def style_function_embargo(x): return{
            'fillColor':'orange',
            'color':'black',
            'weight':1,
            'fillOpacity':0.6
        }

        def style_function_desmat(x): return{
            'fillColor':'red',
            'color':'black',
            'weight':1,
            'fillOpacity':0.6
        }

        def style_function_ti(x): return{
            'fillColor':'purple',
            'color':'black',
            'weight':1,
            'fillOpacity':0.6
        }

        # seleciona apenas a coluna de interesse
        # Plotagem do geodataframe no mapa
        gdf_limpo = gpd.GeoDataFrame(gdf,columns=['geometry'])
        folium.GeoJson(gdf_limpo,style_function=style_function_entrada).add_to(m)

        entrada_embargo_limpo = gpd.GeoDataFrame(entrada_embargo,columns=['geometry'])
        folium.GeoJson(entrada_embargo_limpo,style_function=style_function_embargo).add_to(m)

        entrada_desmat_limpo = gpd.GeoDataFrame(entrada_desmat,columns=['geometry'])
        folium.GeoJson(entrada_desmat_limpo,style_function=style_function_desmat).add_to(m)

        entrada_ti_limpo = gpd.GeoDataFrame(entrada_ti,columns=['geometry'])
        folium.GeoJson(entrada_ti_limpo,style_function=style_function_ti).add_to(m)
        
        
        # Calcula o limite da geometria
        bounds = gdf.total_bounds
        # Ajusta o mapa para os limites da geometria
        m.fit_bounds([[bounds[1],bounds[0]],[bounds[3],bounds[2]]])
        # Adiciona os controles de camadas no mapa
        folium.LayerControl().add_to(m)
        # Faz a plotagem do mapa no dashboard
        st_folium(m,width="100%")

    # Condicional para mostrar os elementos na tela
    if elemento == 'Cabeçalho':
        cabecalho()
    elif elemento == 'Resumo':
        resumo()
    elif elemento == 'Gráfico':
        grafico()
    elif elemento == 'Mapa':
        mapa()


elif arquivo_subido and compacto:

    gdf = poligono_analise

    @st.cache_resource
    def abrir_embargo():
        gdf_embargo = gpd.read_file(EMBARGO)
        return gdf_embargo
    
    @st.cache_resource
    def abrir_desmatamento():
        gdf_desmat = gpd.read_parquet(DESMATAMENTO)
        return gdf_desmat
    
    @st.cache_resource
    def abrir_tis():
        gdf_ti = gpd.read_parquet(TIS)
        return gdf_ti
    
    gdf_embargo = abrir_embargo()
    gdf_desmat = abrir_desmatamento()
    gdf_ti = abrir_tis()

    #st.dataframe(gdf_embargo.head())

    gdf_embargo = gdf_embargo.drop(columns=['nom_pessoa','cpf_cnpj_i','cpf_cnpj_s','end_pessoa','des_bairro','num_cep','num_fone','data_tad','dat_altera','data_cadas','data_geom','dt_carga'])
    
    entrada_embargo = gpd.sjoin(gdf_embargo,gdf,how='inner',predicate='intersects')
    entrada_embargo = gpd.overlay(entrada_embargo,gdf,how='intersection')

    entrada_desmat = gpd.sjoin(gdf_desmat,gdf,how='inner',predicate='intersects')
    entrada_desmat = gpd.overlay(entrada_desmat,gdf,how='intersection')

    entrada_ti = gpd.sjoin(gdf_ti,gdf,how='inner',predicate='intersects')
    entrada_ti = gpd.overlay(entrada_ti,gdf,how='intersection')

    # Conversão do geodataframe em um dataframe
    df_embargo = pd.DataFrame(entrada_embargo).drop(columns=['geometry'])
    df_desmat = pd.DataFrame(entrada_desmat).drop(columns=['geometry'])
    df_ti = pd.DataFrame(entrada_ti).drop(columns=['geometry'])

    area_desmat = entrada_desmat.dissolve(by=None)
    area_desmat = area_desmat.to_crs(epsg=epsg)
    area_desmat['area'] = area_desmat.area / 10000

    area_embargo = entrada_embargo.dissolve(by=None)
    area_embargo = area_embargo.to_crs(epsg=epsg)
    area_embargo['area'] = area_embargo.area / 10000
    
    area_ti = entrada_ti.dissolve(by=None)
    area_ti = area_ti.to_crs(epsg=epsg)
    area_ti['area'] = area_ti.area / 10000

    card_columns1,card_columns2,card_columns3=st.columns(3)
    with card_columns1:
        st.write('Área Total desmatada')
        if len(area_desmat) == 0:
            st.subheader('0')
        else:
            st.subheader(str(round(area_desmat.loc[0,'area'],2)))
    with card_columns2:
        st.write('Área Total de embargos')
        if len(area_embargo) == 0:
            st.subheader('0')
        else:
            st.subheader(str(round(area_embargo.loc[0,'area'],2)))
    with card_columns3:
        st.write('Área Total de Terras Indígenas')
        if len(area_ti) == 0:
            st.subheader('0')
        else:
            st.subheader(str(round(area_ti.loc[0,'area'],2)))

    col1_graf,col2_graf,col3_graf,col4_graf = st.columns(4)

    tema_grafico = col1_graf.selectbox('Selecione o tema do gráfico', options=['Embargo','Desmatamento','Terras Indígenas'])

    if tema_grafico == 'Embargo':
            df_analisado = df_embargo
    elif tema_grafico == 'Desmatamento':
            df_analisado = df_desmat
    elif tema_grafico == 'Terras Indígenas':
            df_analisado = df_ti
    

    tipo_grafico = col2_graf.selectbox('Selecione o tipo de gráfico',options=['box','bar','line','scatter','violin','histogram'],index=5)   

    plot_func = getattr(px, tipo_grafico)
    # Criação de opções dos eixos x e y com opção padrão
    x_val = col3_graf.selectbox('Selecione o eixo x',options=df_analisado.columns,index=4)

    y_val = col4_graf.selectbox('Selecione o eixo y',options=df_analisado.columns,index=3)
    # Cria a plotagem do gráfico
    plot = plot_func(df_analisado,x=x_val,y=y_val)
    # Faz a plotagem
    st.plotly_chart(plot, use_container_width=True)

    m = folium.Map(location=[-14,-54], zoom_start=4, control_scale=True, tiles=None)

            ###inicio do codigo para inserir o google satelite
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satélite",
        overlay=False,
        control=True
        ).add_to(m)

    folium.TileLayer(
        "OpenStreetMap"
        ).add_to(m)
            ###fim do codigo para inserir o google satelite

            # Deleta Colunas do geodataframe: gdf1 = entrada_embargo.drop(columns=['dat_criaca','data_atual'], errors='ignore') 
            
    def style_function_entrada(x): return{
        'fillColor':'blue',
        'color':'black',
        'weight':0,
        'fillOpacity':0.3
        }
            
    def style_function_embargo(x): return{
        'fillColor':'orange',
        'color':'black',
        'weight':1,
        'fillOpacity':0.6
        }

    def style_function_desmat(x): return{
        'fillColor':'red',
        'color':'black',
        'weight':1,
        'fillOpacity':0.6
        }

    def style_function_ti(x): return{
        'fillColor':'purple',
        'color':'black',
        'weight':1,
        'fillOpacity':0.6
        }

    # seleciona apenas a coluna de interesse
    # Plotagem do geodataframe no mapa
    gdf_limpo = gpd.GeoDataFrame(gdf,columns=['geometry'])
    folium.GeoJson(gdf_limpo,style_function=style_function_entrada).add_to(m)

    entrada_embargo_limpo = gpd.GeoDataFrame(entrada_embargo,columns=['geometry'])
    folium.GeoJson(entrada_embargo_limpo,style_function=style_function_embargo).add_to(m)

    entrada_desmat_limpo = gpd.GeoDataFrame(entrada_desmat,columns=['geometry'])
    folium.GeoJson(entrada_desmat_limpo,style_function=style_function_desmat).add_to(m)

    entrada_ti_limpo = gpd.GeoDataFrame(entrada_ti,columns=['geometry'])
    folium.GeoJson(entrada_ti_limpo,style_function=style_function_ti).add_to(m)
            
            
    # Calcula o limite da geometria
    bounds = gdf.total_bounds
    # Ajusta o mapa para os limites da geometria
    m.fit_bounds([[bounds[1],bounds[0]],[bounds[3],bounds[2]]])
    # Adiciona os controles de camadas no mapa
    folium.LayerControl().add_to(m)
    # Faz a plotagem do mapa no dashboard
    st_folium(m,width="100%")

else:
    st.info('Faça upload de um arquivo geoespacial.')