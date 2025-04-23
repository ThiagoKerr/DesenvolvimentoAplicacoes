import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium
import zipfile
import io
import requests

# Configuração da página
st.set_page_config(
    page_title="Localizador de Bairros - Curitiba",
    page_icon="🌍",
    layout="wide"
)

# Título do aplicativo
st.title("🌍 Localizador de Bairros - Curitiba")

# Função para carregar o shapefile
@st.cache_data
def load_shapefile():
    """Carrega o shapefile dos bairros de Curitiba"""
    try:

        SHAPEFILE_URL = "https://github.com/ThiagoKerr/DesenvolvimentoAplicacoes/blob/main/bairros.zip"
        
        # Faz download do arquivo zip
        r = requests.get(SHAPEFILE_URL)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall("shapefile")
        
        # Carrega o shapefile
        bairros = gpd.read_file("shapefile/DIVISA_DE_BAIRROS.shp")
        bairros = bairros.to_crs(epsg=4326)
        return bairros
        
    except Exception as e:
        st.error(f"Erro ao carregar o shapefile: {str(e)}")
        return None

# Carrega os dados dos bairros
bairros = load_shapefile()

if bairros is not None:
    # Seção principal
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Entrada de Coordenadas")
        st.markdown("Digite as coordenadas geográficas (WGS84) do ponto que deseja verificar:")
        
        # Valores padrão para Curitiba
        default_lon = -49.2772  # Longitude do centro de Curitiba
        default_lat = -25.4284  # Latitude do centro de Curitiba
        
        lon = st.number_input("Longitude (ex: -49.2772):", 
                            value=default_lon,
                            min_value=-180.0,
                            max_value=180.0,
                            step=0.0001,
                            format="%.4f")
        
        lat = st.number_input("Latitude (ex: -25.4284):", 
                            value=default_lat,
                            min_value=-90.0,
                            max_value=90.0,
                            step=0.0001,
                            format="%.4f")
        
        if st.button("Identificar Bairro"):
            with st.spinner("Processando..."):
                # Cria o ponto com as coordenadas informadas
                ponto = Point(lon, lat)
                
                # Filtra o bairro que contém o ponto
                bairro_encontrado = bairros[bairros.geometry.contains(ponto)]
                
                if not bairro_encontrado.empty:
                    nome_bairro = bairro_encontrado.iloc[0]['NOME']
                    st.success(f"✅ O ponto pertence ao bairro: **{nome_bairro}**")
                    
                    # Cria o mapa
                    m = folium.Map(location=[lat, lon], zoom_start=14)
                    
                    # Adiciona todos os bairros
                    folium.GeoJson(
                        bairros.__geo_interface__,
                        name="Bairros de Curitiba",
                        style_function=lambda feature: {
                            'fillColor': '#cccccc',
                            'color': '#666666',
                            'fillOpacity': 0.2,
                            'weight': 1,
                        }
                    ).add_to(m)
                    
                    # Destaca o bairro encontrado
                    folium.GeoJson(
                        bairro_encontrado.__geo_interface__,
                        name="Bairro encontrado",
                        style_function=lambda feature: {
                            'fillColor': '#ff0000',
                            'color': '#ff0000',
                            'fillOpacity': 0.5,
                            'weight': 2,
                        }
                    ).add_to(m)
                    
                    # Adiciona marcador
                    folium.Marker(
                        [lat, lon],
                        popup=f"Ponto: {lat:.4f}, {lon:.4f}<br>Bairro: {nome_bairro}",
                        icon=folium.Icon(color='blue', icon='map-marker')
                    ).add_to(m)
                    
                    # Adiciona controle de camadas
                    folium.LayerControl().add_to(m)
                    
                    # Exibe o mapa
                    with col2:
                        st.header("Visualização do Mapa")
                        st_folium(m, width=700, height=500, returned_objects=[])
                else:
                    st.warning("O ponto não está dentro de nenhum bairro de Curitiba.")
                    with col2:
                        st.header("Visualização do Mapa")
                        m = folium.Map(location=[lat, lon], zoom_start=12)
                        folium.Marker([lat, lon]).add_to(m)
                        st_folium(m, width=700, height=500)

    # Sidebar com informações
    with st.sidebar:
        st.header("Sobre")
        st.info("""
        **Localizador de Bairros de Curitiba**  
        Identifica em qual bairro está um ponto com base em coordenadas geográficas.
        """)
        
        st.markdown("### Exemplos de coordenadas:")
        st.code("""
        Centro: -49.2772, -25.4284
        Batel: -49.2856, -25.4428
        Santa Felicidade: -49.3069, -25.3939
        """)
        
        st.markdown("### Como usar:")
        st.write("1. Insira as coordenadas")
        st.write("2. Clique em 'Identificar Bairro'")
        st.write("3. Veja o resultado e o mapa")
        
        st.markdown("---")
        st.markdown("Desenvolvido por [Seu Nome]")

# Se não carregou o shapefile
else:
    st.error("""
    O shapefile dos bairros não pôde ser carregado.  
    Verifique se o arquivo está disponível no repositório.
    """)
