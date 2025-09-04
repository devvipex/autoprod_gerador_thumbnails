"""Testes para Use Cases"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import tempfile
import os

from src.domain.entities import ValidationResult, BackgroundRemovalResult, Transform
from src.application.use_cases import (
    ImageValidationUseCase,
    BackgroundRemovalUseCase,
    BackgroundLoaderUseCase,
    ThumbnailExportUseCase
)


class TestImageValidationUseCase:
    """Testes para validação de imagens"""
    
    def setup_method(self):
        self.use_case = ImageValidationUseCase()
    
    def test_validate_valid_image(self):
        """Testa validação de imagem válida"""
        # Criar imagem temporária
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
            
        try:
            # Criar imagem de teste
            test_image = Image.new('RGB', (100, 100), color='red')
            test_image.save(temp_path)
            
            result = self.use_case.execute(temp_path)
            
            assert result.valid is True
            assert result.error is None
            assert result.width == 100
            assert result.height == 100
            
        finally:
            os.unlink(temp_path)
    
    def test_validate_nonexistent_file(self):
        """Testa validação de arquivo inexistente"""
        result = self.use_case.execute("/path/that/does/not/exist.png")
        
        assert result.valid is False
        assert "não encontrado" in result.error.lower()
    
    def test_validate_unsupported_format(self):
        """Testa validação de formato não suportado"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name
            f.write(b"not an image")
        
        try:
            result = self.use_case.execute(temp_path)
            
            assert result.valid is False
            assert "formato" in result.error.lower()
            
        finally:
            os.unlink(temp_path)


class TestBackgroundRemovalUseCase:
    """Testes para remoção de fundo"""
    
    def setup_method(self):
        self.mock_client = Mock()
        self.use_case = BackgroundRemovalUseCase(self.mock_client)
    
    def test_successful_background_removal(self):
        """Testa remoção de fundo bem-sucedida"""
        # Mock do cliente Gradio
        mock_result_image = Image.new('RGBA', (100, 100))
        self.mock_client.remove_background.return_value = mock_result_image
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
            test_image = Image.new('RGB', (100, 100), color='blue')
            test_image.save(temp_path)
        
        try:
            result = self.use_case.execute(temp_path)
            
            assert result.success is True
            assert result.image_no_bg is not None
            assert result.error is None
            assert result.processing_time > 0
            
        finally:
            os.unlink(temp_path)
    
    def test_gradio_api_error(self):
        """Testa erro na API Gradio"""
        # Mock de erro na API
        self.mock_client.remove_background.side_effect = Exception("API Error")
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
            test_image = Image.new('RGB', (100, 100), color='blue')
            test_image.save(temp_path)
        
        try:
            result = self.use_case.execute(temp_path)
            
            assert result.success is False
            assert result.image_no_bg is None
            assert "API Error" in result.error
            assert result.api_status == "api_error"
            
        finally:
            os.unlink(temp_path)
    
    def test_invalid_image_path(self):
        """Testa caminho de imagem inválido"""
        result = self.use_case.execute("/invalid/path.png")
        
        assert result.success is False
        assert result.api_status == "network_error"
        assert "não encontrado" in result.error.lower() or "no such file" in result.error.lower()


class TestBackgroundLoaderUseCase:
    """Testes para carregamento de backgrounds"""
    
    def setup_method(self):
        self.mock_file_service = Mock()
        self.use_case = BackgroundLoaderUseCase(self.mock_file_service)
    
    def test_load_backgrounds_success(self):
        """Testa carregamento bem-sucedido de backgrounds"""
        # Criar diretório temporário com imagens de teste
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Criar imagem de teste
            test_image = Image.new('RGB', (100, 100), color='red')
            bg_path = os.path.join(temp_dir, 'test_bg.png')
            test_image.save(bg_path)
            
            # Usar o diretório temporário
            use_case = BackgroundLoaderUseCase(temp_dir)
            result = use_case.execute()
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].filename == 'test_bg.png'
    
    def test_load_backgrounds_empty(self):
        """Testa pasta vazia de backgrounds"""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            use_case = BackgroundLoaderUseCase(temp_dir)
            result = use_case.execute()
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_load_backgrounds_error(self):
        """Testa pasta inexistente"""
        use_case = BackgroundLoaderUseCase("/pasta/que/nao/existe")
        result = use_case.execute()
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestThumbnailExportUseCase:
    """Testes para exportação de thumbnails"""
    
    def setup_method(self):
        self.mock_file_service = Mock()
        self.use_case = ThumbnailExportUseCase(self.mock_file_service)
    
    def test_export_success(self):
        """Testa exportação bem-sucedida"""
        # Mock da composição
        mock_composition = Image.new('RGB', (1080, 1080), color='green')
        
        # Mock do file service
        self.mock_file_service.generate_unique_filename.return_value = "test_thumbnail.png"
        self.mock_file_service.get_output_path.return_value = "/output/test_thumbnail.png"
        self.mock_file_service.save_image.return_value = True
        self.mock_file_service.get_file_info.return_value = {
            'size_mb': 2.5,
            'exists': True
        }
        
        result = self.use_case.execute(mock_composition, "test")
        
        assert result.success is True
        assert result.file_path == "/output/test_thumbnail.png"
        assert result.filename == "test_thumbnail.png"
        assert result.size_mb == 2.5
        assert result.error is None
    
    def test_export_save_error(self):
        """Testa erro na gravação do arquivo"""
        mock_composition = Image.new('RGB', (1080, 1080), color='green')
        
        # Mock de erro na gravação
        self.mock_file_service.generate_unique_filename.return_value = "test_thumbnail.png"
        self.mock_file_service.get_output_path.return_value = "/output/test_thumbnail.png"
        self.mock_file_service.save_image.return_value = False
        
        result = self.use_case.execute(mock_composition, "test")
        
        assert result.success is False
        assert result.file_path is None
        assert "Erro ao salvar" in result.error
    
    def test_export_invalid_composition(self):
        """Testa exportação com composição inválida"""
        result = self.use_case.execute(None, "test")
        
        assert result.success is False
        assert "Composição inválida" in result.error


if __name__ == "__main__":
    pytest.main([__file__])