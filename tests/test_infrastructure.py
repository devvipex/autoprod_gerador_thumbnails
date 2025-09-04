"""Testes para Infrastructure Layer"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import tempfile
import os
from pathlib import Path

from src.infrastructure.file_service import FileService
from src.infrastructure.image_service import ImageCompositionService
from src.domain.entities import Transform


class TestFileService:
    """Testes para FileService"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file_service = FileService(self.temp_dir)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_ensure_directories(self):
        """Testa criação de diretórios"""
        self.file_service.ensure_directories()
        
        assert self.file_service.backgrounds_dir.exists()
        assert self.file_service.products_dir.exists()
        assert self.file_service.output_dir.exists()
    
    def test_load_valid_image(self):
        """Testa carregamento de imagem válida"""
        # Criar imagem de teste
        test_image = Image.new('RGB', (100, 100), color='red')
        test_path = Path(self.temp_dir) / "test.png"
        test_image.save(test_path)
        
        loaded_image = self.file_service.load_image(str(test_path))
        
        assert loaded_image is not None
        assert loaded_image.size == (100, 100)
    
    def test_load_nonexistent_image(self):
        """Testa carregamento de imagem inexistente"""
        result = self.file_service.load_image("/path/that/does/not/exist.png")
        assert result is None
    
    def test_save_image(self):
        """Testa salvamento de imagem"""
        test_image = Image.new('RGB', (100, 100), color='blue')
        test_path = Path(self.temp_dir) / "saved_test.png"
        
        success = self.file_service.save_image(test_image, str(test_path))
        
        assert success is True
        assert test_path.exists()
        
        # Verificar se imagem foi salva corretamente
        loaded = Image.open(test_path)
        assert loaded.size == (100, 100)
    
    def test_list_backgrounds(self):
        """Testa listagem de backgrounds"""
        self.file_service.ensure_directories()
        
        # Criar alguns arquivos de teste
        bg1 = Image.new('RGB', (50, 50), color='green')
        bg2 = Image.new('RGB', (50, 50), color='yellow')
        
        bg1.save(self.file_service.backgrounds_dir / "bg1.png")
        bg2.save(self.file_service.backgrounds_dir / "bg2.jpg")
        
        # Criar arquivo não-imagem (deve ser ignorado)
        (self.file_service.backgrounds_dir / "readme.txt").write_text("test")
        
        backgrounds = self.file_service.list_backgrounds()
        
        assert len(backgrounds) == 2
        assert any("bg1.png" in bg for bg in backgrounds)
        assert any("bg2.jpg" in bg for bg in backgrounds)
    
    def test_generate_unique_filename(self):
        """Testa geração de nome único"""
        filename1 = self.file_service.generate_unique_filename("test")
        filename2 = self.file_service.generate_unique_filename("test")
        
        assert filename1 != filename2
        assert filename1.endswith(".png")
        assert "test" in filename1
    
    def test_validate_write_permissions(self):
        """Testa validação de permissões de escrita"""
        # Diretório temporário deve ter permissões de escrita
        assert self.file_service.validate_write_permissions(self.temp_dir) is True
    
    def test_get_file_info(self):
        """Testa obtenção de informações de arquivo"""
        # Criar arquivo de teste
        test_image = Image.new('RGB', (100, 100), color='purple')
        test_path = Path(self.temp_dir) / "info_test.png"
        test_image.save(test_path)
        
        info = self.file_service.get_file_info(str(test_path))
        
        assert info['exists'] is True
        assert info['name'] == "info_test.png"
        assert info['size'] > 0
        assert info['extension'] == ".png"


class TestImageCompositionService:
    """Testes para ImageCompositionService"""
    
    def setup_method(self):
        self.service = ImageCompositionService()
    
    def test_compose_preview_basic(self):
        """Testa composição básica de preview"""
        # Criar imagens de teste
        product = Image.new('RGBA', (200, 200), color=(255, 0, 0, 255))
        background = Image.new('RGB', (1080, 1080), color=(0, 255, 0))
        transform = Transform(x=0, y=0, scale=1.0, rotation=0)
        
        result = self.service.compose_preview(product, background, transform)
        
        assert result is not None
        assert result.size == (1080, 1080)
        assert result.mode == 'RGB'
    
    def test_prepare_background(self):
        """Testa preparação de background"""
        # Background com tamanho diferente
        bg = Image.new('RGB', (500, 300), color='blue')
        
        prepared = self.service._prepare_background(bg)
        
        assert prepared.size == (1080, 1080)
        assert prepared.mode == 'RGB'
    
    def test_apply_transform_scale(self):
        """Testa aplicação de escala"""
        image = Image.new('RGBA', (100, 100), color='red')
        transform = Transform(x=0, y=0, scale=2.0, rotation=0)
        
        transformed = self.service._apply_transform(image, transform)
        
        assert transformed.size == (200, 200)
    
    def test_apply_transform_rotation(self):
        """Testa aplicação de rotação"""
        image = Image.new('RGBA', (100, 100), color='red')
        transform = Transform(x=0, y=0, scale=1.0, rotation=45)
        
        transformed = self.service._apply_transform(image, transform)
        
        # Rotação deve expandir a imagem
        assert transformed.size[0] > 100 or transformed.size[1] > 100
    
    def test_create_thumbnail(self):
        """Testa criação de thumbnail"""
        image = Image.new('RGB', (1000, 1000), color='orange')
        
        thumbnail = self.service.create_thumbnail(image, (150, 150))
        
        assert thumbnail.size[0] <= 150
        assert thumbnail.size[1] <= 150
    
    def test_validate_image_format(self):
        """Testa validação de formato de imagem"""
        rgb_image = Image.new('RGB', (100, 100))
        rgba_image = Image.new('RGBA', (100, 100))
        
        assert self.service.validate_image_format(rgb_image) is True
        assert self.service.validate_image_format(rgba_image) is True
    
    def test_ensure_rgba(self):
        """Testa conversão para RGBA"""
        rgb_image = Image.new('RGB', (100, 100), color='red')
        
        rgba_image = self.service.ensure_rgba(rgb_image)
        
        assert rgba_image.mode == 'RGBA'
        assert rgba_image.size == (100, 100)
    
    def test_remove_transparency(self):
        """Testa remoção de transparência"""
        # Criar imagem RGBA com transparência
        rgba_image = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        
        rgb_image = self.service.remove_transparency(rgba_image, (255, 255, 255))
        
        assert rgb_image.mode == 'RGB'
        assert rgb_image.size == (100, 100)
    
    def test_compose_images_with_offset(self):
        """Testa composição com offset"""
        background = Image.new('RGB', (1080, 1080), color='white')
        product = Image.new('RGBA', (100, 100), color=(255, 0, 0, 255))
        transform = Transform(x=100, y=-50, scale=1.0, rotation=0)
        
        result = self.service._compose_images(background, product, transform)
        
        assert result is not None
        assert result.size == (1080, 1080)
    
    def test_compose_images_boundary_check(self):
        """Testa verificação de limites na composição"""
        background = Image.new('RGB', (1080, 1080), color='white')
        product = Image.new('RGBA', (200, 200), color=(0, 255, 0, 255))
        
        # Transform que colocaria produto fora dos limites
        transform = Transform(x=2000, y=2000, scale=1.0, rotation=0)
        
        result = self.service._compose_images(background, product, transform)
        
        # Deve funcionar sem erro, produto deve ser reposicionado
        assert result is not None
        assert result.size == (1080, 1080)


if __name__ == "__main__":
    pytest.main([__file__])