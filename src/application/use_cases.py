"""Use Cases - Application Layer"""
import os
import logging
from datetime import datetime
from typing import Optional, List
from PIL import Image

try:
    from domain.entities import (
        ValidationResult,
        BackgroundRemovalResult,
        BackgroundInfo,
        Transform,
        ExportResult
    )
except ImportError:
    from domain.entities import (
        ValidationResult,
        BackgroundRemovalResult,
        BackgroundInfo,
        Transform,
        ExportResult
    )


class ImageValidationUseCase:
    """Caso de uso para validação de imagens"""
    
    ALLOWED_FORMATS = {'PNG', 'JPG', 'JPEG'}
    MAX_SIZE_MB = 10
    
    def execute(self, uploaded_file) -> ValidationResult:
        """Valida imagem carregada"""
        try:
            # Verificar se arquivo existe
            if uploaded_file is None:
                return ValidationResult(
                    valid=False,
                    error="Nenhum arquivo selecionado",
                    image=None,
                    size_mb=0,
                    dimensions=(0, 0)
                )
            
            # Tratar diferentes tipos de entrada
            if isinstance(uploaded_file, str):
                # Caminho do arquivo
                from pathlib import Path
                file_path = Path(uploaded_file)
                if not file_path.exists():
                    return ValidationResult(
                        valid=False,
                        error=f"Arquivo não encontrado: {uploaded_file}",
                        image=None,
                        size_mb=0,
                        dimensions=(0, 0)
                    )
                
                size_mb = file_path.stat().st_size / (1024 * 1024)
                image = Image.open(file_path)
            else:
                # Objeto de arquivo (BytesIO, etc.)
                size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
                image = Image.open(uploaded_file)
            
            # Verificar tamanho
            if size_mb > self.MAX_SIZE_MB:
                return ValidationResult(
                    valid=False,
                    error=f"Arquivo muito grande ({size_mb:.1f}MB). Máximo: {self.MAX_SIZE_MB}MB",
                    image=None,
                    size_mb=size_mb,
                    dimensions=(0, 0)
                )
            
            # Verificar formato
            if image.format not in self.ALLOWED_FORMATS:
                return ValidationResult(
                    valid=False,
                    error=f"Formato {image.format} não suportado. Use: {', '.join(self.ALLOWED_FORMATS)}",
                    image=None,
                    size_mb=size_mb,
                    dimensions=image.size
                )
            
            return ValidationResult(
                valid=True,
                error=None,
                image=image,
                size_mb=size_mb,
                dimensions=image.size
            )
            
        except Exception as e:
            logging.error(f"Erro na validação: {e}")
            return ValidationResult(
                valid=False,
                error=f"Erro ao processar imagem: {str(e)}",
                image=None,
                size_mb=0,
                dimensions=(0, 0)
            )


class BackgroundRemovalUseCase:
    """Caso de uso para remoção de fundo via API Gradio"""
    
    def __init__(self, gradio_client):
        self.gradio_client = gradio_client
        self.timeout = 30
    
    def execute(self, image_path: str) -> BackgroundRemovalResult:
        """Remove fundo da imagem usando API Gradio com fallback local"""
        start_time = datetime.now()
        
        try:
            # Verificar se arquivo existe
            if not os.path.exists(image_path):
                return BackgroundRemovalResult(
                    success=False,
                    image_no_bg=None,
                    error="Arquivo não encontrado",
                    processing_time=0,
                    api_status="api_error"
                )
            
            # Carregar imagem
            input_image = Image.open(image_path)
            
            # Chamar método de remoção de fundo (com fallback automático)
            result_image = self.gradio_client.remove_background(input_image)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if result_image:
                api_status = "fallback_local" if self.gradio_client.use_fallback else "success"
                return BackgroundRemovalResult(
                    success=True,
                    image_no_bg=result_image,
                    error=None,
                    processing_time=processing_time,
                    api_status=api_status
                )
            else:
                return BackgroundRemovalResult(
                    success=False,
                    image_no_bg=None,
                    error="Falha na remoção de fundo (API e fallback)",
                    processing_time=processing_time,
                    api_status="api_error"
                )
                
        except TimeoutError:
            return BackgroundRemovalResult(
                success=False,
                image_no_bg=None,
                error="Timeout na API Gradio (30s)",
                processing_time=self.timeout,
                api_status="timeout"
            )
        except Exception as e:
            # Reduzir verbosidade para erros conhecidos da API Gradio
            if "has not enabled verbose error reporting" in str(e):
                logging.debug(f"API Gradio indisponível, usando fallback: {e}")
                error_msg = "API Gradio indisponível, usando processamento local"
            else:
                logging.error(f"Erro na remoção de fundo: {e}")
                error_msg = f"Erro na API: {str(e)}"
            
            return BackgroundRemovalResult(
                success=False,
                image_no_bg=None,
                error=error_msg,
                processing_time=(datetime.now() - start_time).total_seconds(),
                api_status="network_error"
            )


class BackgroundLoaderUseCase:
    """Caso de uso para carregar backgrounds disponíveis"""
    
    def __init__(self, backgrounds_dir: str = "backgrounds"):
        self.backgrounds_dir = backgrounds_dir
    
    def execute(self) -> List[BackgroundInfo]:
        """Carrega lista de backgrounds disponíveis"""
        backgrounds = []
        
        try:
            if not os.path.exists(self.backgrounds_dir):
                logging.warning(f"Pasta {self.backgrounds_dir} não encontrada")
                return backgrounds
            
            for filename in os.listdir(self.backgrounds_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    path = os.path.join(self.backgrounds_dir, filename)
                    
                    try:
                        with Image.open(path) as img:
                            backgrounds.append(BackgroundInfo(
                                filename=filename,
                                path=path,
                                thumbnail_path=path,  # Por enquanto, usar a própria imagem
                                dimensions=img.size
                            ))
                    except Exception as e:
                        logging.warning(f"Erro ao carregar {filename}: {e}")
                        continue
            
            return backgrounds
            
        except Exception as e:
            logging.error(f"Erro ao carregar backgrounds: {e}")
            return backgrounds


class ThumbnailExportUseCase:
    """Caso de uso para export de thumbnails padronizados"""
    
    def __init__(self, output_dir: str = "thumbnails-prontas"):
        self.output_dir = output_dir
        self.target_size = (1080, 1080)
    
    def execute(self, composition: Image.Image, filename: Optional[str] = None, original_name: Optional[str] = None) -> ExportResult:
        """Exporta thumbnail final padronizado"""
        try:
            # Criar pasta de output se não existir
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Gerar nome seguindo padrão: nome_original_thumb.png
            if filename is None:
                if original_name:
                    # Remove extensão do nome original e adiciona sufixo _thumb
                    base_name = os.path.splitext(original_name)[0]
                    filename = f"{base_name}_thumb.png"
                else:
                    # Fallback para timestamp se não tiver nome original
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"produto_{timestamp}_thumb.png"
            else:
                # Se filename foi fornecido, garantir que termina com _thumb
                base_name = os.path.splitext(filename)[0]
                if not base_name.endswith('_thumb'):
                    filename = f"{base_name}_thumb.png"
                elif not filename.lower().endswith('.png'):
                    filename = f"{filename}.png"
            
            file_path = os.path.join(self.output_dir, filename)
            
            # Redimensionar para 1080x1080 mantendo proporção
            resized_composition = self._resize_to_target(composition)
            
            # Salvar como PNG
            resized_composition.save(file_path, "PNG", optimize=True)
            
            # Calcular tamanho do arquivo
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            return ExportResult(
                success=True,
                file_path=file_path,
                filename=filename,
                error=None,
                size_mb=size_mb
            )
            
        except Exception as e:
            logging.error(f"Erro no export: {e}")
            return ExportResult(
                success=False,
                file_path=None,
                filename=None,
                error=f"Erro ao salvar arquivo: {str(e)}",
                size_mb=0
            )
    
    def _resize_to_target(self, image: Image.Image) -> Image.Image:
        """Redimensiona imagem para 1080x1080 mantendo proporção"""
        # Criar canvas 1080x1080 com fundo transparente
        canvas = Image.new('RGBA', self.target_size, (0, 0, 0, 0))
        
        # Se a imagem já está no tamanho correto, usar diretamente
        if image.size == self.target_size:
            return image
        
        # Calcular redimensionamento mantendo proporção
        img_ratio = image.width / image.height
        target_ratio = self.target_size[0] / self.target_size[1]
        
        if img_ratio > target_ratio:
            # Imagem mais larga - ajustar pela largura
            new_width = self.target_size[0]
            new_height = int(new_width / img_ratio)
        else:
            # Imagem mais alta - ajustar pela altura
            new_height = self.target_size[1]
            new_width = int(new_height * img_ratio)
        
        # Redimensionar imagem
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Centralizar no canvas
        x = (self.target_size[0] - new_width) // 2
        y = (self.target_size[1] - new_height) // 2
        
        canvas.paste(resized, (x, y), resized if resized.mode == 'RGBA' else None)
        
        return canvas