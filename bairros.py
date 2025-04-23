import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium
import os

# Configuração do app
st.set_page_config(
    page_title="Localizador de Bairros - Curitiba",
    layout="wide"
)
st.title("🌍 Localizador de Bairros - Curitiba")

# Caminhos relativos
SHAPEFILE_PATH = "DIVISA_DE_BAIRROS.shp"
COLUNA_NOME = "NOME"

# Carrega os dados
@st.cache_data
def load_data():
    try:
        gdf = gpd.read_file(SHAPEFILE_PATH)
        return gdf.to_crs(epsg=4326)
    except Exception as e:
        st.error(f"Erro ao carregar shapefile: {str(e)}")
        st.stop()

bairros = load_data()

# Verifica coluna de nome
if COLUNA_NOME not in bairros.columns:
    st.error(f"Coluna '{COLUNA_NOME}' não encontrada. Colunas disponíveis: {', '.join(bairros.columns)}")
    st.stop()

# Armazena o estado do mapa na sessão
if 'map' not in st.session_state:
    st.session_state.map = None

# Interface
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Digite as coordenadas")
    lon = st.number_input("Longitude:", value=-49.2772, format="%.6f", key='lon')
    lat = st.number_input("Latitude:", value=-25.4284, format="%.6f", key='lat')
    
    if st.button("Identificar Bairro"):
        ponto = Point(st.session_state.lon, st.session_state.lat)
        bairro = bairros[bairros.geometry.contains(ponto)]
        
        if not bairro.empty:
            nome_bairro = bairro.iloc[0][COLUNA_NOME]
            st.success(f"✅ O ponto pertence ao bairro: {nome_bairro}")
            
            # Cria o mapa
            m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=14)
            
            folium.GeoJson(
                bairros,
                style_function=lambda x: {'fillColor': '#dddddd', 'color': '#888888', 'weight': 1, 'fillOpacity': 0.3},
                name="Todos os bairros"
            ).add_to(m)
            
            folium.GeoJson(
                bairro,
                style_function=lambda x: {'fillColor': '#ff0000', 'color': '#ff0000', 'weight': 2, 'fillOpacity': 0.7},
                name="Bairro encontrado"
            ).add_to(m)
            
            folium.Marker(
                [st.session_state.lat, st.session_state.lon],
                popup=f"<b>{nome_bairro}</b><br>Lat: {st.session_state.lat:.6f}<br>Lon: {st.session_state.lon:.6f}",
                icon=folium.Icon(color='blue', icon='map-marker')
            ).add_to(m)
            
            folium.LayerControl().add_to(m)
            
            # Armazena o mapa na sessão
            st.session_state.map = m
            
        else:
            st.warning("Ponto fora dos bairros de Curitiba")
            m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=12)
            folium.Marker([st.session_state.lat, st.session_state.lon]).add_to(m)
            st.session_state.map = m

# Exibe o mapa (se existir)
if st.session_state.map is not None:
    with col2:
        st.header("Visualização do Mapa")
        st_folium(st.session_state.map, width=700, height=500, returned_objects=[])

# Sidebar
with st.sidebar:
    st.header("Sobre")
    st.write(f"Shapefile carregado: {os.path.basename(SHAPEFILE_PATH)}")
    st.write(f"Total de bairros: {len(bairros)}")
    st.markdown("### Exemplos de coordenadas:")
    st.code("""
    Centro: -49.2772, -25.4284
    Batel: -49.2856, -25.4428
    Santa Felicidade: -49.3069, -25.3939
    """)
