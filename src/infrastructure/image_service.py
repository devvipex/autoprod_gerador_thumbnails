"""Image Service - Infrastructure Layer"""
import logging
from typing import Optional
from PIL import Image, ImageOps
import numpy as np

from domain.entities import Transform


class ImageCompositionService:
    """Serviço para composição de imagens"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.canvas_size = (1080, 1080)
    
    def compose_preview(self, product: Image.Image, background: Image.Image, transform: Transform) -> Image.Image:
        """Compõe preview combinando produto e background"""
        try:
            # Preparar background
            bg_resized = self._prepare_background(background)
            
            # Aplicar transformações ao produto
            product_transformed = self._apply_transform(product, transform)
            
            # Compor imagem final
            composition = self._compose_images(bg_resized, product_transformed, transform)
            
            return composition
            
        except Exception as e:
            self.logger.error(f"Erro na composição: {e}")
            raise
    
    def _prepare_background(self, background: Image.Image) -> Image.Image:
        """Prepara background para composição"""
        # Redimensionar background para 1080x1080
        if background.size != self.canvas_size:
            # Redimensionar mantendo proporção e depois fazer crop central
            background = ImageOps.fit(
                background, 
                self.canvas_size, 
                Image.Resampling.LANCZOS,
                centering=(0.5, 0.5)
            )
        
        # Garantir modo RGB
        if background.mode != 'RGB':
            background = background.convert('RGB')
        
        return background
    
    def _apply_transform(self, image: Image.Image, transform: Transform) -> Image.Image:
        """Aplica transformações (escala, rotação) à imagem"""
        try:
            # Aplicar escala
            if transform.scale != 1.0:
                new_size = (
                    int(image.width * transform.scale),
                    int(image.height * transform.scale)
                )
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Aplicar rotação
            if transform.rotation != 0:
                image = image.rotate(
                    transform.rotation, 
                    expand=True, 
                    fillcolor=(0, 0, 0, 0) if image.mode == 'RGBA' else (255, 255, 255)
                )
            
            return image
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar transformações: {e}")
            raise
    
    def _compose_images(self, background: Image.Image, product: Image.Image, transform: Transform) -> Image.Image:
        """Compõe imagem final combinando background e produto"""
        try:
            # Criar canvas final
            canvas = background.copy()
            
            # Calcular posição do produto
            canvas_center_x = self.canvas_size[0] // 2
            canvas_center_y = self.canvas_size[1] // 2
            
            # Aplicar offset da transformação
            product_x = canvas_center_x + transform.x - (product.width // 2)
            product_y = canvas_center_y + transform.y - (product.height // 2)
            
            # Garantir que o produto está dentro dos limites
            product_x = max(0, min(product_x, self.canvas_size[0] - product.width))
            product_y = max(0, min(product_y, self.canvas_size[1] - product.height))
            
            # Colar produto no canvas
            if product.mode == 'RGBA':
                # Usar canal alpha para transparência
                canvas.paste(product, (product_x, product_y), product)
            else:
                # Sem transparência
                canvas.paste(product, (product_x, product_y))
            
            return canvas
            
        except Exception as e:
            self.logger.error(f"Erro na composição final: {e}")
            raise
    
    def create_thumbnail(self, image: Image.Image, size: tuple[int, int] = (150, 150)) -> Image.Image:
        """Cria thumbnail de uma imagem"""
        try:
            thumbnail = image.copy()
            thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
            return thumbnail
        except Exception as e:
            self.logger.error(f"Erro ao criar thumbnail: {e}")
            raise
    
    def validate_image_format(self, image: Image.Image) -> bool:
        """Valida se formato da imagem é suportado"""
        supported_formats = {'RGB', 'RGBA', 'L', 'P'}
        return image.mode in supported_formats
    
    def ensure_rgba(self, image: Image.Image) -> Image.Image:
        """Garante que imagem está em modo RGBA"""
        if image.mode != 'RGBA':
            return image.convert('RGBA')
        return image
    
    def remove_transparency(self, image: Image.Image, background_color: tuple = (255, 255, 255)) -> Image.Image:
        """Remove transparência substituindo por cor sólida"""
        if image.mode != 'RGBA':
            return image
        
        # Criar background sólido
        background = Image.new('RGB', image.size, background_color)
        
        # Compor imagem sobre background
        background.paste(image, mask=image.split()[-1])  # Usar canal alpha como máscara
        
        return background