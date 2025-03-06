import streamlit as st
import requests
import io
import base64
import pandas as pd
from PIL import Image
import json
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
    
    # Configurações padrão para cada ferramenta
    if tool_name == "DocTR":
        st.session_state.config = {
            "model_type": "resnet50",
            "detection_threshold": 0.5,
            "recognition_threshold": 0.3,
            "assume_straight_pages": True,
            "straighten_pages": True,
            "preserve_interword_spaces": True
        }
    elif tool_name == "OCR.Space":
        st.session_state.config = {
            "language": "por",
            "isOverlayRequired": True,
            "detectOrientation": True,
            "scale": True,
            "OCREngine": 2,  # More accurate OCR Engine 2
            "filetype": "auto"
        }
    
    go_to_config()

# Função para processar OCR com DocTR
def process_doctr(file_bytes, config):
    try:
        # Em um ambiente real, carregaríamos o modelo DocTR
        # Como o DocTR requer TensorFlow/PyTorch, vamos simular a resposta
        # para fins de demonstração no Streamlit Cloud
        
        # Simulação de processamento
        result = f"DocTR OCR Processing Result\n\n"
        result += f"Modelo: {config['model_type']}\n"
        result += f"Limiar de detecção: {config['detection_threshold']}\n"
        result += f"Limiar de reconhecimento: {config['recognition_threshold']}\n"
        result += f"Assumir páginas retas: {config['assume_straight_pages']}\n"
        result += f"Endireitar páginas: {config['straighten_pages']}\n"
        result += f"Preservar espaços entre palavras: {config['preserve_interword_spaces']}\n\n"
        
        # Texto simulado
        result += "Este é um exemplo de texto extraído pelo DocTR.\n"
        result += "Em uma implementação real, você veria o texto do seu documento aqui."
        
        return result
    except Exception as e:
        return f"Erro ao processar com DocTR: {str(e)}"

# Função para processar OCR com OCR.Space
def process_ocrspace(file_bytes, config, api_key):
    try:
        # Preparar os parâmetros para a API
        payload = {
            'apikey': api_key,
            'language': config['language'],
            'isOverlayRequired': config['isOverlayRequired'],
            'detectOrientation': config['detectOrientation'],
            'scale': config['scale'],
            'OCREngine': config['OCREngine']
        }
        
        # Enviar arquivo para a API OCR.Space
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(file_bytes)
            tmp_filename = tmp.name
        
        with open(tmp_filename, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files=files,
                data=payload
            )
        
        # Remover arquivo temporário
        os.unlink(tmp_filename)
        
        # Verificar resposta
        if response.status_code == 200:
            result_json = response.json()
            
            if result_json['IsErroredOnProcessing']:
                return f"Erro da API OCR.Space: {result_json['ErrorMessage']}"
            
            extracted_text = ""
            if 'ParsedResults' in result_json and result_json['ParsedResults']:
                for parsed_result in result_json['ParsedResults']:
                    extracted_text += parsed_result['ParsedText']
                return extracted_text
            else:
                return "Não foi possível extrair texto do documento."
        else:
            return f"Erro na requisição à API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erro ao processar com OCR.Space: {str(e)}"

# Função principal para processamento de OCR
def process_ocr(uploaded_file):
    if uploaded_file is None:
        return "Por favor, faça o upload de um arquivo."
    
    # Ler o arquivo
    file_bytes = uploaded_file.getvalue()
    
    if st.session_state.selected_tool == "DocTR":
        return process_doctr(file_bytes, st.session_state.config)
    elif st.session_state.selected_tool == "OCR.Space":
        if not st.session_state.api_key:
            return "É necessário fornecer uma chave de API para usar o OCR.Space."
        return process_ocrspace(file_bytes, st.session_state.config, st.session_state.api_key)
    else:
        return "Ferramenta não selecionada ou não suportada."

# Interface da página inicial
def render_home():
    st.title("🔎 Seletor de Ferramentas OCR")
    st.markdown("""
    Bem-vindo ao sistema de reconhecimento óptico de caracteres (OCR). 
    Escolha uma ferramenta abaixo para começar a extrair texto de imagens e documentos.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("DocTR")
        st.markdown("""
        **Melhor para:** Documentos complexos, tabelas e múltiplas línguas
        
        **Vantagens:**
        - Código aberto
        - Não requer API externa
        - Excelente para documentos estruturados
        - Suporte para detecção de tabelas
        
        **Limitações:**
        - Mais pesado computacionalmente
        """)
        st.button("Selecionar DocTR", on_click=lambda: select_tool("DocTR"), key="btn_doctr")

    with col2:
        st.subheader("OCR.Space")
        st.markdown("""
        **Melhor para:** Imagens simples, texto em vários idiomas
        
        **Vantagens:**
        - API fácil de usar
        - Excelente para textos simples
        - Suporte para múltiplos idiomas
        - Processamento rápido
        
        **Limitações:**
        - Requer chave de API
        - Número limitado de requisições gratuitas
        """)
        st.button("Selecionar OCR.Space", on_click=lambda: select_tool("OCR.Space"), key="btn_ocrspace")

# Interface da página de configuração
def render_config():
    st.title(f"⚙️ Configurar {st.session_state.selected_tool}")
    
    if st.session_state.selected_tool == "DocTR":
        st.markdown("""
        Configure os parâmetros do DocTR. Os valores padrão são recomendados para a maioria dos casos.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.config['model_type'] = st.selectbox(
                "Tipo de modelo",
                ["resnet50", "mobilenet_v3_small", "mobilenet_v3_large"],
                index=0,
                help="Modelo de rede neural a ser usado. ResNet50 oferece melhor precisão, enquanto MobileNet é mais rápido."
            )
            
            st.session_state.config['detection_threshold'] = st.slider(
                "Limiar de detecção",
                min_value=0.1,
                max_value=0.9,
                value=st.session_state.config['detection_threshold'],
                step=0.1,
                help="Limiar de confiança para detecção de texto. Valores mais altos são mais seletivos."
            )
            
            st.session_state.config['recognition_threshold'] = st.slider(
                "Limiar de reconhecimento",
                min_value=0.1,
                max_value=0.9,
                value=st.session_state.config['recognition_threshold'],
                step=0.1,
                help="Limiar de confiança para reconhecimento de caracteres. Valores mais altos são mais seletivos."
            )
        
        with col2:
            st.session_state.config['assume_straight_pages'] = st.checkbox(
                "Assumir páginas retas",
                value=st.session_state.config['assume_straight_pages'],
                help="Assumir que as páginas estão retas, o que pode acelerar o processamento."
            )
            
            st.session_state.config['straighten_pages'] = st.checkbox(
                "Endireitar páginas",
                value=st.session_state.config['straighten_pages'],
                help="Tentar endireitar as páginas automaticamente antes do processamento."
            )
            
            st.session_state.config['preserve_interword_spaces'] = st.checkbox(
                "Preservar espaços entre palavras",
                value=st.session_state.config['preserve_interword_spaces'],
                help="Manter os espaços entre palavras no texto extraído."
            )
    
    elif st.session_state.selected_tool == "OCR.Space":
        st.markdown("""
        Configure os parâmetros do OCR.Space. Os valores padrão são recomendados para a maioria dos casos.
        Para usar o OCR.Space, você precisa de uma chave de API.
        Você pode obter uma chave gratuita em [OCR.Space](https://ocr.space/ocrapi).
        """)
        
        st.session_state.api_key = st.text_input(
            "Chave de API OCR.Space",
            value=st.session_state.api_key,
            type="password",
            help="Sua chave de API OCR.Space."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
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
                }[x],
                help="Idioma principal do texto no documento."
            )
            
            st.session_state.config['OCREngine'] = st.radio(
                "Motor OCR",
                [1, 2, 3],
                index=1,
                format_func=lambda x: {
                    1: "Motor 1 (Mais rápido)",
                    2: "Motor 2 (Mais preciso)",
                    3: "Motor 3 (Multi-idioma)"
                }[x],
                help="Motor OCR a ser usado. O Motor 2 é geralmente mais preciso para a maioria dos casos."
            )
        
        with col2:
            st.session_state.config['detectOrientation'] = st.checkbox(
                "Detectar orientação",
                value=st.session_state.config['detectOrientation'],
                help="Detectar e corrigir automaticamente a orientação do texto."
            )
            
            st.session_state.config['isOverlayRequired'] = st.checkbox(
                "Requisitar sobreposição",
                value=st.session_state.config['isOverlayRequired'],
                help="Retorna informações de localização do texto na imagem."
            )
            
            st.session_state.config['scale'] = st.checkbox(
                "Escalar imagem",
                value=st.session_state.config['scale'],
                help="Escalar automaticamente imagens grandes para melhor processamento."
            )
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("← Voltar para seleção de ferramentas", on_click=go_to_home)
    with col2:
        st.button("Prosseguir para extração de texto →", on_click=go_to_extraction, type="primary")

# Interface da página de extração
def render_extraction():
    st.title(f"📄 Extração de Texto com {st.session_state.selected_tool}")
    
    st.markdown(f"""
    Faça o upload de um arquivo para extrair o texto usando {st.session_state.selected_tool}.
    Os parâmetros configurados serão aplicados durante o processamento.
    """)
    
    uploaded_file = st.file_uploader("Escolha um arquivo", type=["jpg", "jpeg", "png", "pdf", "tiff", "bmp"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("← Voltar para configurações", on_click=go_to_config)
    with col2:
        if st.button("Processar", type="primary"):
            if uploaded_file is not None:
                with st.spinner('Processando o documento...'):
                    st.session_state.result = process_ocr(uploaded_file)
                st.success('Processamento concluído!')
    
    if st.session_state.result:
        st.subheader("Resultado da Extração")
        st.text_area("Texto Extraído", st.session_state.result, height=400)
        
        # Botão para download do resultado
        txt_download = st.session_state.result.encode('utf-8')
        st.download_button(
            label="📥 Download do Texto",
            data=txt_download,
            file_name="texto_extraido.txt",
            mime="text/plain"
        )

# Renderizar a página apropriada
if st.session_state.page == 'home':
    render_home()
elif st.session_state.page == 'config':
    render_config()
elif st.session_state.page == 'extraction':
    render_extraction()
