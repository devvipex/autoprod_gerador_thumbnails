import streamlit as st
import sys
from pathlib import Path
from PIL import Image
import io
import base64
import time
import zipfile
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict, Any
import json

# Adicionar src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from main import ThumbnailGeneratorApp
from domain.entities import Transform, AppState

# Configuração da página mobile-friendly
st.set_page_config(
    page_title="Autoprod 0.1",
    page_icon="▲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização do estado da sessão
def initialize_session_state():
    """Inicializa o estado da sessão"""
    # Inicializar aplicação
    if 'app' not in st.session_state:
        try:
            st.session_state.app = ThumbnailGeneratorApp()
            success = st.session_state.app.initialize()
            st.session_state.system_ready = success
        except Exception as e:
            st.session_state.system_ready = False
            st.session_state.app = None
    
    # Estados da interface
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'selected_background' not in st.session_state:
        st.session_state.selected_background = None
    if 'available_backgrounds' not in st.session_state:
        st.session_state.available_backgrounds = []
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = {'active': False, 'progress': 0}
    if 'batch_results' not in st.session_state:
        st.session_state.batch_results = []
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 0
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []

def load_available_backgrounds():
    """Carrega backgrounds disponíveis"""
    backgrounds_dir = Path("backgrounds")
    if backgrounds_dir.exists():
        backgrounds = []
        for bg_file in backgrounds_dir.glob("*.png"):
            if bg_file.is_file():
                backgrounds.append(str(bg_file))
        st.session_state.available_backgrounds = backgrounds
    else:
        st.session_state.available_backgrounds = []

def render_mobile_header():
    """Renderiza cabeçalho mobile-friendly"""
    st.title("Autoprod 0.1")
    st.markdown("Gerador profissional de thumbnails para produtos")

def render_upload_section():
    """Renderiza seção de upload mobile-friendly"""
    st.subheader("Faça Upload dos seus Produtos")
    
    # Upload de arquivos
    uploaded_files = st.file_uploader(
        "Selecione os arquivos",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Formatos suportados: PNG, JPG, JPEG"
    )
    
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        
        # Mostrar arquivos carregados
        with st.expander(f"{len(uploaded_files)} arquivo(s) carregado(s)", expanded=True):
            for i, file in enumerate(uploaded_files):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(file.name)
                with col2:
                    st.caption(f"{file.size // 1024} KB")
    else:
        st.info("Faça upload dos seus produtos para começar")
        st.write("Formatos suportados: PNG, JPG, JPEG")
        st.write("Processamento em massa até 60 imagens")

def render_background_removal_section():
    """Renderiza seção de remoção de fundo com preview"""
    st.subheader("Remoção de Fundo")
    
    if not st.session_state.uploaded_files:
        st.info("↑ Carregue imagens primeiro")
        return
    
    st.write("Preview das imagens carregadas:")
    
    # Grid de preview das imagens
    cols = st.columns(3)
    for idx, uploaded_file in enumerate(st.session_state.uploaded_files):
        col_idx = idx % 3
        with cols[col_idx]:
            # Mostrar imagem original
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Original: {uploaded_file.name}", width=200)
    
    st.markdown("---")
    
    # Botão único para processar todas as imagens
    total_images = len(st.session_state.uploaded_files)
    
    # Verificar se já existem imagens processadas
    has_processed = hasattr(st.session_state, 'processed_images') and st.session_state.processed_images
    
    if not has_processed:
        if st.button(f"Remover Fundo de Todas as Imagens ({total_images})", 
                    key="remove_all_bg", 
                    type="primary"):
            
            # Inicializar app se necessário
            if 'app' not in st.session_state:
                st.session_state.app = ThumbnailGeneratorApp()
                st.session_state.app.initialize()
            
            # Inicializar container para imagens processadas
            st.session_state.processed_images = {}
            
            # Barra de progresso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Processar todas as imagens
            for idx, uploaded_file in enumerate(st.session_state.uploaded_files):
                progress = (idx + 1) / total_images
                progress_bar.progress(progress)
                status_text.text(f"Removendo fundo de {uploaded_file.name}... ({idx+1}/{total_images})")
                
                try:
                    # Salvar arquivo temporário
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_path = tmp_file.name
                    
                    try:
                        # Remover fundo via API Gradio
                        result = st.session_state.app.background_remover.execute(temp_path)
                        
                        if result.success:
                            st.session_state.processed_images[uploaded_file.name] = result.image_no_bg
                            add_notification(f"Fundo removido de {uploaded_file.name}", "success")
                        else:
                            add_notification(f"Erro ao remover fundo de {uploaded_file.name}: {result.error}", "error")
                    
                    finally:
                        # Limpar arquivo temporário
                        if Path(temp_path).exists():
                            Path(temp_path).unlink()
                        
                except Exception as e:
                    add_notification(f"Erro ao processar {uploaded_file.name}: {str(e)}", "error")
            
            status_text.text("✅ Processamento concluído!")
            progress_bar.progress(1.0)
            st.rerun()
    
    # Mostrar imagens processadas se existirem
    if has_processed:
        st.write("Imagens com fundo removido:")
        
        processed_cols = st.columns(3)
        for idx, (filename, processed_image) in enumerate(st.session_state.processed_images.items()):
            col_idx = idx % 3
            with processed_cols[col_idx]:
                # Verificar se imagem tem transparência
                if processed_image.mode == 'RGBA':
                    # Criar uma versão com fundo xadrez para mostrar transparência
                    import numpy as np
                    
                    # Criar padrão xadrez
                    checker_size = 20
                    h, w = processed_image.size[1], processed_image.size[0]
                    checker = np.zeros((h, w, 3), dtype=np.uint8)
                    
                    for i in range(0, h, checker_size):
                        for j in range(0, w, checker_size):
                            if (i // checker_size + j // checker_size) % 2 == 0:
                                checker[i:i+checker_size, j:j+checker_size] = [240, 240, 240]
                            else:
                                checker[i:i+checker_size, j:j+checker_size] = [200, 200, 200]
                    
                    checker_img = Image.fromarray(checker, 'RGB')
                    
                    # Compor imagem sobre o fundo xadrez
                    display_img = checker_img.copy()
                    display_img.paste(processed_image, (0, 0), processed_image)
                    
                    st.image(display_img, caption=f"Sem fundo: {filename}", width=200)
                else:
                    st.image(processed_image, caption=f"Sem fundo: {filename}", width=200)
        
        # Botão para avançar
        if st.button("Selecionar Background", key="advance_to_bg", type="primary"):
            st.session_state.current_tab = 2
            st.rerun()

def render_background_section():
    """Renderiza seção de seleção de background"""
    st.subheader("◐ Seleção de Background")
    
    # Carregar backgrounds disponíveis
    load_available_backgrounds()
    
    if not st.session_state.available_backgrounds:
        st.warning("[AVISO] Nenhum background encontrado")
        st.info("Adicione imagens de background na pasta 'backgrounds/'")
        return
    
    # Seleção de background
    background_options = [Path(bg).name for bg in st.session_state.available_backgrounds]
    selected_bg_name = st.selectbox(
        "Escolha um background:",
        options=background_options,
        help="Selecione o background para suas miniaturas"
    )
    
    if selected_bg_name:
        selected_bg_path = next(
            bg for bg in st.session_state.available_backgrounds 
            if Path(bg).name == selected_bg_name
        )
        st.session_state.selected_background = selected_bg_path
        add_notification(f"Background selecionado: {selected_bg_name}", "success")

def render_preview_controls():
    """Renderiza controles de preview configurável com layout lado a lado"""
    st.subheader("[PREVIEW] Configurar Posicionamento")
    
    # Verificar se há imagem e background selecionados
    if not st.session_state.uploaded_files or not st.session_state.selected_background:
        st.info("↑ Selecione uma imagem e background para ver o preview")
        return
    
    # Verificar se há imagens processadas (com ou sem remoção de fundo)
    has_processed = hasattr(st.session_state, 'processed_images') and st.session_state.processed_images
    
    # Seleção da imagem para preview
    if has_processed:
        # Usar imagens processadas
        image_options = list(st.session_state.processed_images.keys())
        selected_image_name = st.selectbox(
            "Escolha a imagem para preview:",
            options=image_options,
            help="Selecione qual imagem processada usar no preview"
        )
        selected_image = st.session_state.processed_images[selected_image_name]
        use_processed = True
    else:
        # Usar imagens originais
        image_options = [f.name for f in st.session_state.uploaded_files]
        selected_image_name = st.selectbox(
            "Escolha a imagem para preview:",
            options=image_options,
            help="Selecione qual imagem usar no preview"
        )
        # Encontrar o arquivo correspondente
        selected_image = next(f for f in st.session_state.uploaded_files if f.name == selected_image_name)
        use_processed = False
    
    # Inicializar configurações se não existirem
    if 'transform_settings' not in st.session_state:
        st.session_state.transform_settings = {
            'x_position': 0,
            'y_position': 0,
            'scale': 1.0,
            'rotation': 0
        }
    
    # Inicializar use_auto_scale com valor padrão
    use_auto_scale = st.session_state.get('use_auto_scale', True)
    
    # Layout: Preview à esquerda, Controles à direita
    preview_col, controls_col = st.columns([1, 1])
    
    with preview_col:
        st.markdown("**Preview da Composição:**")
        try:
            
            # Criar preview com as configurações atuais
            preview_image = create_preview_composition(
                selected_image,
                st.session_state.selected_background,
                st.session_state.transform_settings['x_position'],
                st.session_state.transform_settings['y_position'],
                st.session_state.transform_settings['scale'],
                st.session_state.transform_settings['rotation'],
                use_auto_scale
            )
            
            if preview_image:
                st.image(preview_image, caption="Composição final")
            else:
                st.warning("[AVISO] Não foi possível gerar preview")
                
        except Exception as e:
            st.error(f"[ERRO] Falha no preview: {e}")
    
    with controls_col:
        st.markdown("Controles de Transformação:")
        
        # Sistema de presets
        render_preset_controls()
        
        st.markdown("---")
        
        # Toggle para redimensionamento automático
        use_auto_scale = st.checkbox(
            "🎯 Redimensionamento Automático",
            value=st.session_state.get('use_auto_scale', True),
            help="Ajusta automaticamente o tamanho do produto para manter consistência visual"
        )
        
        # Salvar no session_state
        st.session_state.use_auto_scale = use_auto_scale
        
        if use_auto_scale:
            st.info("💡 O produto será redimensionado automaticamente para ocupar ~60% do canvas")
        
        st.markdown("---")
        
        # Controles de transformação
        x_position = st.slider(
            "Posição X (horizontal)",
            min_value=-200,
            max_value=200,
            value=st.session_state.transform_settings['x_position'],
            step=5,
            key="x_position_slider"
        )
        
        y_position = st.slider(
            "Posição Y (vertical)",
            min_value=-200,
            max_value=200,
            value=st.session_state.transform_settings['y_position'],
            step=5,
            key="y_position_slider"
        )
        
        scale = st.slider(
            "Escala",
            min_value=0.1,
            max_value=3.0,
            value=st.session_state.transform_settings['scale'],
            step=0.1,
            key="scale_slider"
        )
        
        rotation = st.slider(
            "Rotação (graus)",
            min_value=-180,
            max_value=180,
            value=st.session_state.transform_settings['rotation'],
            step=5,
            key="rotation_slider"
        )
        
        # Atualizar configurações
        st.session_state.transform_settings.update({
            'x_position': x_position,
            'y_position': y_position,
            'scale': scale,
            'rotation': rotation
        })
        
        # Botão de reset
        if st.button("[RESET] Resetar Configurações", key="reset_transform"):
            st.session_state.transform_settings = {
                'x_position': 0,
                'y_position': 0,
                'scale': 1.0,
                'rotation': 0
            }
            st.rerun()

def calculate_auto_scale(product_image, canvas_size=1080, target_coverage=0.6):
    """Calcula escala automática baseada no tamanho do produto para manter consistência visual"""
    try:
        # Obter dimensões do produto
        width, height = product_image.size
        
        # Calcular a maior dimensão
        max_dimension = max(width, height)
        
        # Calcular tamanho alvo baseado na cobertura desejada do canvas
        target_size = canvas_size * target_coverage
        
        # Calcular escala necessária
        auto_scale = target_size / max_dimension
        
        # Limitar escala entre 0.2 e 2.0 para evitar extremos
        auto_scale = max(0.2, min(2.0, auto_scale))
        
        return auto_scale
        
    except Exception:
        return 1.0  # Fallback para escala padrão

def create_preview_composition(image_input, background_path, x_pos, y_pos, scale, rotation, use_auto_scale=True):
    """Cria uma composição de preview com as configurações especificadas"""
    try:
        # Carregar imagens - aceita tanto UploadedFile quanto PIL Image
        if isinstance(image_input, Image.Image):
            # Já é uma imagem PIL (processada)
            product_image = image_input.copy()
        else:
            # É um UploadedFile do Streamlit
            product_image = Image.open(image_input)
        
        background_image = Image.open(background_path)
        
        # Redimensionar background para 1080x1080
        background_image = background_image.resize((1080, 1080), Image.Resampling.LANCZOS)
        
        # Aplicar escala automática se habilitada
        final_scale = scale
        if use_auto_scale:
            auto_scale = calculate_auto_scale(product_image)
            final_scale = scale * auto_scale
        
        # Aplicar transformações na imagem do produto
        if final_scale != 1.0:
            new_size = (int(product_image.width * final_scale), int(product_image.height * final_scale))
            product_image = product_image.resize(new_size, Image.Resampling.LANCZOS)
        
        if rotation != 0:
            product_image = product_image.rotate(rotation, expand=True)
        
        # Calcular posição de colagem
        paste_x = (background_image.width - product_image.width) // 2 + x_pos
        paste_y = (background_image.height - product_image.height) // 2 + y_pos
        
        # Criar composição
        result = background_image.copy()
        
        # Colar imagem do produto
        if product_image.mode == 'RGBA':
            result.paste(product_image, (paste_x, paste_y), product_image)
        else:
            result.paste(product_image, (paste_x, paste_y))
        
        return result
        
    except Exception as e:
        st.error(f"[ERRO] Falha na composição: {e}")
        return None

def render_processing_controls():
    """Renderiza controles de processamento"""
    st.subheader("Controles de Processamento")
    
    # Verificar se pode processar
    can_process = (
        st.session_state.uploaded_files and 
        st.session_state.selected_background and
        st.session_state.get('system_ready', False)
    )
    
    if not can_process:
        missing = []
        if not st.session_state.uploaded_files:
            missing.append("Imagens")
        if not st.session_state.selected_background:
            missing.append("Background")
        if not st.session_state.get('system_ready', False):
            missing.append("Sistema")
        
        st.warning(f"Faltam: {', '.join(missing)}")
        return
    
    # Opções de processamento
    with st.expander("Opções Avançadas", expanded=False):
        quality = st.slider(
            "Qualidade da imagem",
            min_value=70,
            max_value=100,
            value=95,
            help="Qualidade da imagem final (70-100%)"
        )
        
        # Controle de redimensionamento automático para processamento
        use_auto_scale_processing = st.checkbox(
            "🎯 Aplicar Redimensionamento Automático no Processamento",
            value=True,
            help="Aplica redimensionamento automático durante o processamento em lote"
        )
        
        # Armazenar no session_state
        st.session_state.use_auto_scale_processing = use_auto_scale_processing
    
    # Botão de processamento
    if st.button(
        "Iniciar processo",
        type="primary",

        disabled=st.session_state.processing_status.get('active', False)
    ):
        start_processing(True, quality)  # True para aplicar remoção de fundo no processamento final

def start_processing(remove_background=True, quality=95):
    """Inicia o processamento das imagens"""
    st.session_state.processing_status = {'active': True, 'progress': 0}
    st.session_state.batch_results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        total_files = len(st.session_state.uploaded_files)
        
        for i, uploaded_file in enumerate(st.session_state.uploaded_files):
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"Processando {uploaded_file.name}... ({i+1}/{total_files})")
            
            try:
                # Processar imagem
                result = process_single_image(
                    uploaded_file,
                    st.session_state.selected_background,
                    remove_background,
                    quality
                )
                st.session_state.batch_results.append(result)
                
            except Exception as e:
                st.session_state.batch_results.append({
                    'filename': uploaded_file.name,
                    'status': 'error',
                    'error': str(e)
                })
        
        st.session_state.processing_status = {'active': False, 'completed': True}
        status_text.text("[OK] Processamento concluído!")
        
    except Exception as e:
        st.session_state.processing_status = {'active': False, 'error': str(e)}
        st.error(f"Erro no processamento: {e}")

def process_single_image(uploaded_file, background_path, remove_background, quality):
    """Processa uma única imagem com configurações de transformação"""
    try:
        if not st.session_state.get('app'):
            return {
                'filename': uploaded_file.name,
                'status': 'error',
                'message': 'Sistema não inicializado'
            }
        
        app = st.session_state.app
        
        # Obter configurações de transformação
        transform_settings = st.session_state.get('transform_settings', {
            'x_position': 0,
            'y_position': 0,
            'scale': 1.0,
            'rotation': 0
        })
        
        # Obter configuração de redimensionamento automático
        use_auto_scale = st.session_state.get('use_auto_scale_processing', True)
        
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        try:
            # Processar imagem com transformações customizadas
            result_path = process_image_with_transforms(
                temp_path,
                background_path,
                transform_settings,
                remove_background,
                uploaded_file.name,
                use_auto_scale
            )
            
            if result_path and Path(result_path).exists():
                # Ler resultado
                with open(result_path, 'rb') as f:
                    image_data = f.read()
                
                return {
                    'filename': uploaded_file.name,
                    'status': 'success',
                    'data': base64.b64encode(image_data).decode(),
                    'size': len(image_data),
                    'path': result_path
                }
            else:
                return {
                    'filename': uploaded_file.name,
                    'status': 'error',
                    'message': 'Falha no processamento'
                }
                
        finally:
            # Limpar arquivo temporário
            if Path(temp_path).exists():
                Path(temp_path).unlink()
                
    except Exception as e:
        return {
            'filename': uploaded_file.name,
            'status': 'error',
            'message': str(e)
        }

def process_image_with_transforms(image_path, background_path, transform_settings, remove_background=True, original_filename=None, use_auto_scale=True):
    """Processa imagem aplicando transformações customizadas"""
    try:
        # Carregar imagens
        product_image = Image.open(image_path)
        background_image = Image.open(background_path)
        
        # Remover fundo se necessário
        if remove_background and st.session_state.get('app'):
            app = st.session_state.app
            # Usar a API do Gradio para remover fundo
            try:
                result_image = app.gradio_client.remove_background(product_image)
                if result_image:
                    product_image = result_image
            except Exception as e:
                st.warning(f"[AVISO] Falha na remoção de fundo: {e}")
        
        # Redimensionar background para 1080x1080
        background_image = background_image.resize((1080, 1080), Image.Resampling.LANCZOS)
        
        # Aplicar transformações
        scale = transform_settings.get('scale', 1.0)
        rotation = transform_settings.get('rotation', 0)
        x_pos = transform_settings.get('x_position', 0)
        y_pos = transform_settings.get('y_position', 0)
        
        # Aplicar escala automática se habilitada
        final_scale = scale
        if use_auto_scale:
            auto_scale = calculate_auto_scale(product_image)
            final_scale = scale * auto_scale
        
        if final_scale != 1.0:
            new_size = (int(product_image.width * final_scale), int(product_image.height * final_scale))
            product_image = product_image.resize(new_size, Image.Resampling.LANCZOS)
        
        if rotation != 0:
            product_image = product_image.rotate(rotation, expand=True)
        
        # Calcular posição de colagem
        paste_x = (background_image.width - product_image.width) // 2 + x_pos
        paste_y = (background_image.height - product_image.height) // 2 + y_pos
        
        # Criar composição final
        result = background_image.copy()
        
        # Colar imagem do produto
        if product_image.mode == 'RGBA':
            result.paste(product_image, (paste_x, paste_y), product_image)
        else:
            result.paste(product_image, (paste_x, paste_y))
        
        # Salvar resultado
        output_dir = Path("thumbnails-prontas")
        output_dir.mkdir(exist_ok=True)
        
        # Usar nome original do arquivo se fornecido, senão usar o nome do arquivo temporário
        if original_filename:
            base_name = Path(original_filename).stem
        else:
            base_name = Path(image_path).stem
        
        output_path = output_dir / f"{base_name}_thumb.png"
        
        # Garantir nome único
        counter = 1
        while output_path.exists():
            output_path = output_dir / f"{base_name}_thumb_{counter}.png"
            counter += 1
        
        # Salvar como PNG
        result.save(output_path, "PNG", optimize=True)
        
        return str(output_path)
        
    except Exception as e:
        st.error(f"[ERRO] Falha no processamento: {e}")
        return None

def render_results_section():
    """Renderiza seção de resultados"""
    if not st.session_state.batch_results:
        return
    
    st.subheader("Relatório de Processamento")
    
    # Estatísticas
    total = len(st.session_state.batch_results)
    successful = len([r for r in st.session_state.batch_results if r['status'] == 'success'])
    failed = total - successful
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", total)
    with col2:
        st.metric("Sucesso", successful)
    with col3:
        st.metric("Erro", failed)
    
    # Mostrar resultados
    if successful > 0:
        with st.expander(f"Imagens Processadas ({successful})", expanded=True):
            # Grid de imagens em miniatura
            cols = st.columns(4)  # 4 colunas para mostrar lado a lado
            for idx, result in enumerate(st.session_state.batch_results):
                if result['status'] == 'success':
                    col_idx = idx % 4
                    with cols[col_idx]:
                        img_data = base64.b64decode(result['data'])
                        
                        # Calcular tamanho da imagem
                        img_size_kb = len(img_data) // 1024
                        
                        # Container para a imagem
                        container = st.container()
                        with container:
                            # Mostrar imagem
                            st.image(img_data, width=150)
                            
                            # Informações da imagem
                            st.caption(f"**{result['filename']}**")
                            st.caption(f"Tamanho: {img_size_kb} KB")
            

        
        # Botão de download
        if st.button("Baixar Todas as Imagens"):
            zip_data = create_results_zip()
            if zip_data:
                st.download_button(
                    label="Download ZIP",
                    data=zip_data,
                    file_name=f"thumbnails_{int(time.time())}.zip",
                    mime="application/zip",
        
                )
    
    # Mostrar erros se houver
    if failed > 0:
        with st.expander(f"Erros ({failed})", expanded=False):
            for result in st.session_state.batch_results:
                if result['status'] == 'error':
                    add_notification(f"Erro em {result['filename']}: {result['message']}", "error")

def create_results_zip():
    """Cria arquivo ZIP com os resultados"""
    try:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for result in st.session_state.batch_results:
                if result['status'] == 'success':
                    img_data = base64.b64decode(result['data'])
                    filename = f"thumb_{result['filename']}"
                    zip_file.writestr(filename, img_data)
        
        return zip_buffer.getvalue()
    except Exception as e:
        st.error(f"Erro ao criar ZIP: {e}")
        return None

def render_preset_controls():
    """Renderiza controles de presets de posicionamento"""
    st.markdown("Presets de Posicionamento:")
    
    presets = {
        "Centro": {'x_position': 0, 'y_position': 0, 'scale': 1.0, 'rotation': 0},
        "Esquerda": {'x_position': -100, 'y_position': 0, 'scale': 1.0, 'rotation': 0},
        "Direita": {'x_position': 100, 'y_position': 0, 'scale': 1.0, 'rotation': 0},
        "Superior": {'x_position': 0, 'y_position': -80, 'scale': 1.0, 'rotation': 0},
        "Inferior": {'x_position': 0, 'y_position': 80, 'scale': 1.0, 'rotation': 0},
        "Grande": {'x_position': 0, 'y_position': 0, 'scale': 1.5, 'rotation': 0},
        "Pequeno": {'x_position': 0, 'y_position': 0, 'scale': 0.7, 'rotation': 0}
    }
    
    preset_cols = st.columns(3)
    for i, (preset_name, preset_values) in enumerate(presets.items()):
        col_idx = i % 3
        with preset_cols[col_idx]:
            if st.button(preset_name, key=f"preset_{preset_name}"):
                st.session_state.transform_settings.update(preset_values)
                st.rerun()

def render_sidebar():
    """Renderiza sidebar com botões visuais"""
    with st.sidebar:
        st.markdown("### Navegação")
        
        # Botões de navegação estilizados
        nav_buttons = [
            {"title": "Carregar Imagens", "step": 0},
            {"title": "Remover Fundo", "step": 1},
            {"title": "Selecionar Background", "step": 2},
            {"title": "Processar Produtos", "step": 3},
            {"title": "Ver Resultado", "step": 4}
        ]
        
        current_step = st.session_state.get('current_tab', 0)
        
        for btn in nav_buttons:
            # Estilo do botão baseado no estado
            if btn["step"] == current_step:
                button_type = "primary"
            else:
                button_type = "secondary"
            
            if st.button(
                btn['title'],
                key=f"nav_btn_{btn['step']}",
                type=button_type,
        
            ):
                st.session_state.current_tab = btn["step"]
                st.rerun()
        
        # Botão de voltar removido conforme solicitado
        
        st.markdown("---")
        
        # Botão de reset
        if st.button("Resetar Tudo"):
            for key in ['uploaded_files', 'selected_background', 'batch_results', 'processing_status']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_tab = 0
            st.rerun()

def render_navigation_controls():
    """Renderiza controles de navegação automática"""
    # Navegação automática sempre ativa
    pass

def add_notification(message, type="info", duration=3000):
    """Adiciona uma notificação temporária"""
    notification = {
        'id': f"notif_{int(time.time() * 1000)}",
        'message': message,
        'type': type,
        'timestamp': time.time(),
        'duration': duration
    }
    st.session_state.notifications.append(notification)

def render_status_corner():
    """Renderiza status no canto usando componentes nativos do Streamlit"""
    # Apenas mostrar status críticos via notificações dinâmicas
    pass

def render_notifications():
    """Renderiza notificações usando componentes nativos do Streamlit"""
    if not hasattr(st.session_state, 'notifications'):
        return
        
    current_time = time.time()
    notifications_to_show = []
    notifications_to_keep = []
    
    # Processar notificações
    for notif in st.session_state.notifications:
        elapsed_ms = (current_time - notif['timestamp']) * 1000
        if elapsed_ms < notif['duration']:
            # Verificar se ainda não foi exibida
            if not notif.get('displayed', False):
                notifications_to_show.append(notif)
                notif['displayed'] = True
            notifications_to_keep.append(notif)
    
    # Atualizar lista mantendo apenas notificações ativas
    st.session_state.notifications = notifications_to_keep
    
    # Exibir novas notificações
    for notif in notifications_to_show:
        if notif['type'] == 'success':
            st.toast(notif['message'], icon='✅')
        elif notif['type'] == 'error':
            st.toast(notif['message'], icon='❌')
        elif notif['type'] == 'warning':
            st.toast(notif['message'], icon='⚠️')
        else:
            st.toast(notif['message'], icon='ℹ️')

def main():
    """Função principal da aplicação"""
    try:
        # Inicializar estado
        initialize_session_state()
        
        # Renderizar sidebar
        render_sidebar()
        
        # Renderizar cabeçalho
        render_mobile_header()
        
        # Controles de navegação
        render_navigation_controls()
        
        # Renderizar conteúdo baseado na aba selecionada
        current_tab = st.session_state.get('current_tab', 0)
        
        if current_tab == 0:  # Upload
            render_upload_section()
            # Auto-avançar quando imagens forem carregadas
            if st.session_state.uploaded_files:
                if st.button("Remover Fundo", key="auto_next_1", type="primary"):
                    st.session_state.current_tab = 1
                    st.rerun()
        elif current_tab == 1:  # Remoção de Fundo
            render_background_removal_section()
        elif current_tab == 2:  # Background
            render_background_section()
            # Adicionar preview configurável na mesma aba
            if st.session_state.uploaded_files and st.session_state.selected_background:
                st.markdown("---")
                render_preview_controls()
                # Auto-avançar quando background for selecionado
                if st.button("Processar Produtos", key="auto_next_2", type="primary"):
                    st.session_state.current_tab = 3
                    st.rerun()
        elif current_tab == 3:  # Processar
            render_processing_controls()
        elif current_tab == 4:  # Resultados
            render_results_section()
        
        # Renderizar notificações dinâmicas
        render_notifications()
        
    except Exception as e:
        st.error(f"Erro na aplicação: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()