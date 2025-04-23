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

# Caminhos relativos (Streamlit Cloud monta o repo completo)
SHAPEFILE_PATH = "DIVISA_DE_BAIRROS.shp"
COLUNA_NOME = "NOME"  # Confirme o nome da coluna

# Carrega os dados
@st.cache_data
def load_data():
    try:
        # Verifica se os arquivos existem
        required_files = [
            SHAPEFILE_PATH,
            SHAPEFILE_PATH.replace('.shp', '.shx'),
            SHAPEFILE_PATH.replace('.shp', '.dbf'),
            SHAPEFILE_PATH.replace('.shp', '.prj')
        ]
        
        missing_files = [f for f in required_files if not os.path.exists(f)]
        if missing_files:
            st.error(f"Arquivos do shapefile faltando: {', '.join(missing_files)}")
            st.stop()
        
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

# Interface
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Digite as coordenadas")
    lon = st.number_input("Longitude:", value=-49.2772, format="%.6f")
    lat = st.number_input("Latitude:", value=-25.4284, format="%.6f")
    
    if st.button("Identificar Bairro"):
        ponto = Point(lon, lat)
        bairro = bairros[bairros.geometry.contains(ponto)]
        
        if not bairro.empty:
            nome_bairro = bairro.iloc[0][COLUNA_NOME]
            st.success(f"✅ O ponto pertence ao bairro: {nome_bairro}")
            
            # Mapa interativo
            m = folium.Map(location=[lat, lon], zoom_start=14)
            
            # Camada de todos os bairros
            folium.GeoJson(
                bairros,
                style_function=lambda x: {
                    'fillColor': '#dddddd',
                    'color': '#888888',
                    'weight': 1,
                    'fillOpacity': 0.3
                },
                name="Todos os bairros"
            ).add_to(m)
            
            # Bairro selecionado
            folium.GeoJson(
                bairro,
                style_function=lambda x: {
                    'fillColor': '#ff0000',
                    'color': '#ff0000',
                    'weight': 2,
                    'fillOpacity': 0.7
                },
                name="Bairro encontrado"
            ).add_to(m)
            
            # Marcador
            folium.Marker(
                [lat, lon],
                popup=f"<b>{nome_bairro}</b><br>Lat: {lat:.6f}<br>Lon: {lon:.6f}",
                icon=folium.Icon(color='blue', icon='map-marker')
            ).add_to(m)
            
            # Controle de camadas
            folium.LayerControl().add_to(m)
            
            with col2:
                st_folium(m, width=700, height=500)
        else:
            st.warning("Ponto fora dos bairros de Curitiba")
            with col2:
                m = folium.Map(location=[lat, lon], zoom_start=12)
                folium.Marker([lat, lon]).add_to(m)
                st_folium(m, width=700, height=500)

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
