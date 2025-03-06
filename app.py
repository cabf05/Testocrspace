import streamlit as st
import requests
import tempfile
import os

# Configuração da página
st.set_page_config(
    page_title="OCR Tool Selector",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização da sessão
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_tool' not in st.session_state:
    st.session_state.selected_tool = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'config' not in st.session_state:
    st.session_state.config = {}
if 'result' not in st.session_state:
    st.session_state.result = ""

# Funções de navegação
def go_to_home():
    st.session_state.page = 'home'
    st.session_state.selected_tool = None
    st.session_state.config = {}
    st.session_state.result = ""

def go_to_config():
    st.session_state.page = 'config'

def go_to_extraction():
    st.session_state.page = 'extraction'

def select_tool(tool_name):
    st.session_state.selected_tool = tool_name
    if tool_name == "OCR.Space":
        st.session_state.config = {
            "language": "por",
            "isOverlayRequired": True,
            "detectOrientation": True,
            "scale": True,
            "OCREngine": 2,
        }
    go_to_config()

# Função para processar OCR com OCR.Space
def process_ocrspace(file_bytes, file_type, config, api_key):
    if not api_key:
        return "Chave de API não fornecida para OCR.Space."

    if len(file_bytes) > 1000000:  # 1MB (limite para contas gratuitas)
        return "Erro: O arquivo excede o limite de 1MB permitido para contas gratuitas no OCR.Space."

    payload = {
        'apikey': api_key,
        'language': config['language'],
        'isOverlayRequired': config['isOverlayRequired'],
        'detectOrientation': config['detectOrientation'],
        'scale': config['scale'],
        'OCREngine': config['OCREngine']
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_type) as tmp:
        tmp.write(file_bytes)
        tmp_filename = tmp.name

    with open(tmp_filename, 'rb') as f:
        files = {'file': f}
        response = requests.post('https://api.ocr.space/parse/image', files=files, data=payload)

    os.unlink(tmp_filename)

    if response.status_code != 200:
        return f"Erro HTTP {response.status_code}: {response.text}"

    result_json = response.json()

    if result_json.get('IsErroredOnProcessing'):
        return f"Erro do OCR.Space: {result_json.get('ErrorMessage', 'Erro desconhecido')}"
    
    extracted_text = "\n".join([res.get('ParsedText', '') for res in result_json.get('ParsedResults', [])])

    return extracted_text if extracted_text.strip() else "Nenhum texto foi extraído."

# Função principal para processamento de OCR
def process_ocr(uploaded_file):
    if not uploaded_file:
        return "Por favor, faça o upload de um arquivo."

    file_bytes = uploaded_file.getvalue()
    file_type = os.path.splitext(uploaded_file.name)[-1].lower()

    if file_type not in [".jpg", ".jpeg", ".png", ".pdf", ".tiff", ".bmp"]:
        return "Erro: Formato de arquivo não suportado. Use JPG, PNG, PDF, TIFF ou BMP."

    if st.session_state.selected_tool == "OCR.Space":
        return process_ocrspace(file_bytes, file_type, st.session_state.config, st.session_state.api_key)
    else:
        return "Ferramenta não selecionada ou não suportada."

# Interface da página inicial
def render_home():
    st.title("🔎 Seletor de Ferramentas OCR")
    st.markdown("Escolha uma ferramenta abaixo para extrair texto de imagens e documentos.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("OCR.Space")
        st.markdown("""
        **Vantagens:**  
        - API fácil de usar  
        - Suporte para múltiplos idiomas  
        - Processamento rápido  
        
        **Limitações:**  
        - Requer chave de API  
        - Número limitado de requisições gratuitas  
        """)
        st.button("Selecionar OCR.Space", on_click=lambda: select_tool("OCR.Space"))

# Interface da página de configuração
def render_config():
    st.title(f"⚙️ Configurar {st.session_state.selected_tool}")

    if st.session_state.selected_tool == "OCR.Space":
        st.session_state.api_key = st.text_input(
            "Chave de API OCR.Space",
            value=st.session_state.api_key,
            type="password",
            help="Obtenha uma chave gratuita em https://ocr.space/ocrapi."
        )

        st.session_state.config['language'] = st.selectbox(
            "Idioma",
            ["por", "eng", "spa", "fra", "deu", "ita", "jpn", "kor", "chi_sim", "chi_tra"],
            index=0,
            format_func=lambda x: {
                "por": "Português",
                "eng": "Inglês",
                "spa": "Espanhol",
                "fra": "Francês",
                "deu": "Alemão",
                "ita": "Italiano",
                "jpn": "Japonês",
                "kor": "Coreano",
                "chi_sim": "Chinês Simplificado",
                "chi_tra": "Chinês Tradicional"
            }[x]
        )

        st.session_state.config['OCREngine'] = st.radio(
            "Motor OCR",
            [1, 2, 3],
            index=1,
            format_func=lambda x: {
                1: "Motor 1 (Mais rápido)",
                2: "Motor 2 (Mais preciso)",
                3: "Motor 3 (Para PDFs e multi-idioma)"
            }[x]
        )

    col1, col2 = st.columns(2)
    with col1:
        st.button("← Voltar para seleção de ferramentas", on_click=go_to_home)
    with col2:
        st.button("Prosseguir para extração de texto →", on_click=go_to_extraction, type="primary")

# Interface da página de extração
def render_extraction():
    st.title(f"📄 Extração de Texto com {st.session_state.selected_tool}")
    st.markdown("Faça o upload de um arquivo para extrair o texto.")

    uploaded_file = st.file_uploader("Escolha um arquivo", type=["jpg", "jpeg", "png", "pdf", "tiff", "bmp"])

    col1, col2 = st.columns(2)
    with col1:
        st.button("← Voltar para configurações", on_click=go_to_config)
    with col2:
        if st.button("Processar", type="primary"):
            if uploaded_file is not None:
                with st.spinner('Processando...'):
                    st.session_state.result = process_ocr(uploaded_file)
                st.success('Processamento concluído!')

    if st.session_state.result:
        st.subheader("Resultado da Extração")
        st.text_area("Texto Extraído", st.session_state.result, height=300)

        txt_download = st.session_state.result.encode('utf-8')
        st.download_button("📥 Download do Texto", data=txt_download, file_name="texto_extraido.txt", mime="text/plain")

# Renderizar a página apropriada
if st.session_state.page == 'home':
    render_home()
elif st.session_state.page == 'config':
    render_config()
elif st.session_state.page == 'extraction':
    render_extraction()
