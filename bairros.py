import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium
import zipfile
import io
import requests
import os

# Configuração da página
st.set_page_config(
    page_title="Localizador de Bairros - Curitiba",
    page_icon="🌍",
    layout="wide"
)

# Título do aplicativo
st.title("🌍 Localizador de Bairros - Curitiba")

@st.cache_data
def load_shapefile():
    """Carrega o shapefile dos bairros de Curitiba"""
    try:
        # URL do arquivo ZIP no GitHub (FORMATO RAW)
        SHAPEFILE_URL = "https://github.com/ThiagoKerr/DesenvolvimentoAplicacoes/blob/c946f286620ff54402c8fadb00b9a88a14367806/bairros.zip"
        
        # Cria diretório temporário se não existir
        os.makedirs("temp_shapefile", exist_ok=True)
        
        # Faz download do arquivo zip
        r = requests.get(SHAPEFILE_URL)
        if r.status_code != 200:
            st.error(f"Erro ao baixar o shapefile. Status code: {r.status_code}")
            return None
            
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            # Extrai todos os arquivos para o diretório temporário
            z.extractall("temp_shapefile")
            
            # Lista os arquivos extraídos para debug
            st.session_state.extracted_files = z.namelist()
            
            # Procura pelo arquivo .shp (case insensitive)
            shp_file = [f for f in z.namelist() if f.lower().endswith('.shp')]
            
            if not shp_file:
                st.error("Nenhum arquivo .shp encontrado no ZIP")
                return None
                
            # Carrega o shapefile
            shapefile_path = os.path.join("temp_shapefile", shp_file[0])
            bairros = gpd.read_file(shapefile_path)
            bairros = bairros.to_crs(epsg=4326)
            
            # Verifica se a coluna 'NOME' existe (ou ajuste para o nome correto)
            if 'NOME' not in bairros.columns:
                st.error("Coluna 'NOME' não encontrada no shapefile. Colunas disponíveis: " + ", ".join(bairros.columns))
                return None
                
            return bairros
            
    except Exception as e:
        st.error(f"Erro ao carregar o shapefile: {str(e)}")
        return None

# Carrega os dados dos bairros
bairros = load_shapefile()

# Debug: mostra arquivos extraídos (opcional)
if 'extracted_files' in st.session_state:
    st.sidebar.write("Arquivos extraídos:", st.session_state.extracted_files)

if bairros is not None:
    # Restante do seu código (igual ao anterior)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Entrada de Coordenadas")
        # ... (mantenha o resto do código igual)
