"""Main Application - Thumbnail Generator MVP"""
import logging
import sys
from pathlib import Path
from typing import Optional
from PIL import Image

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('thumbnail_generator.log')
    ]
)

# Silenciar logs verbosos de bibliotecas externas
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('gradio_client').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)

# Imports do projeto
try:
    # Imports relativos (quando usado como módulo)
    from .domain.entities import Transform, AppState
    from .application.use_cases import (
        ImageValidationUseCase,
        BackgroundRemovalUseCase,
        BackgroundLoaderUseCase,
        ThumbnailExportUseCase
    )
    from .infrastructure.gradio_client import GradioBackgroundRemovalClient
    from .infrastructure.image_service import ImageCompositionService
    from .infrastructure.file_service import FileService
except ImportError:
    # Imports absolutos (quando executado diretamente)
    from domain.entities import Transform, AppState
    from application.use_cases import (
        ImageValidationUseCase,
        BackgroundRemovalUseCase,
        BackgroundLoaderUseCase,
        ThumbnailExportUseCase
    )
    from infrastructure.gradio_client import GradioBackgroundRemovalClient
    from infrastructure.image_service import ImageCompositionService
    from infrastructure.file_service import FileService


class ThumbnailGeneratorApp:
    """Aplicação principal do gerador de thumbnails"""
    
    def __init__(self, base_path: str = "."):
        self.logger = logging.getLogger(__name__)
        self.base_path = Path(base_path)
        
        # Inicializar serviços de infraestrutura
        self.file_service = FileService(base_path)
        self.gradio_client = GradioBackgroundRemovalClient()
        self.image_service = ImageCompositionService()
        
        # Inicializar casos de uso
        self.image_validator = ImageValidationUseCase()
        self.background_remover = BackgroundRemovalUseCase(self.gradio_client)
        self.background_loader = BackgroundLoaderUseCase("backgrounds")
        self.thumbnail_exporter = ThumbnailExportUseCase("thumbnails-prontas")
        
        # Estado da aplicação
        self.app_state = AppState(
            current_step="upload",
            original_image=None,
            processed_image=None,
            selected_background=None,
            current_transform=Transform(x=0, y=0, scale=1.0, rotation=0),
            composition=None
        )
        
        self.logger.info("ThumbnailGeneratorApp inicializada")
    
    def initialize(self) -> bool:
        """Inicializa aplicação e verifica dependências"""
        try:
            self.logger.info("Inicializando aplicação...")
            
            # Garantir diretórios
            self.file_service.ensure_directories()
            
            # Verificar permissões
            if not self.file_service.validate_write_permissions(self.file_service.output_dir):
                self.logger.error("Sem permissões de escrita no diretório de saída")
                return False
            
            # Health check da API Gradio
            if not self.gradio_client.health_check():
                self.logger.warning("API Gradio não está disponível")
                # Continuar mesmo assim, pois pode ser temporário
            
            self.logger.info("Aplicação inicializada com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização: {e}")
            return False
    
    def validate_image(self, image_path: str) -> bool:
        """Valida imagem de entrada"""
        try:
            self.app_state.current_step = "validating"
            
            result = self.image_validator.execute(image_path)
            
            if result.valid:
                self.app_state.original_image = image_path
                self.logger.info(f"Imagem válida: {image_path}")
                return True
            else:
                self.logger.error(f"Imagem inválida: {result.error}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro na validação: {e}")
            return False
    
    def remove_background(self, image_path: str) -> Optional[str]:
        """Remove fundo da imagem"""
        try:
            self.app_state.current_step = "removing_background"
            
            result = self.background_remover.execute(image_path)
            
            if result.success and result.image_no_bg:
                self.app_state.processed_image = result.image_no_bg
                self.logger.info(f"Fundo removido com sucesso em {result.processing_time:.2f}s")
                return result.image_no_bg
            else:
                self.logger.error(f"Falha na remoção de fundo: {result.error}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro na remoção de fundo: {e}")
            return None
    
    def load_backgrounds(self) -> list[str]:
        """Carrega lista de backgrounds disponíveis"""
        try:
            backgrounds = self.background_loader.execute()
            
            # Extrair apenas os paths dos BackgroundInfo
            background_paths = [bg.path for bg in backgrounds]
            
            self.logger.info(f"Carregados {len(background_paths)} backgrounds")
            return background_paths
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar backgrounds: {e}")
            return []
    
    def list_backgrounds(self) -> list[str]:
        """Lista backgrounds disponíveis (alias para load_backgrounds)"""
        return self.load_backgrounds()
    
    def compose_preview(self, product_path: str, background_path: str, transform: Transform = None) -> Optional[Image.Image]:
        """Compõe preview da thumbnail"""
        try:
            self.app_state.current_step = "composing"
            
            # Usar transformação padrão se não fornecida
            if transform is None:
                transform = Transform(x=0, y=0, scale=1.0, rotation=0)
            
            # Carregar imagens
            product = self.file_service.load_image(product_path)
            background = self.file_service.load_image(background_path)
            
            if not product or not background:
                self.logger.error("Erro ao carregar imagens para composição")
                return None
            
            # Compor imagem
            composition = self.image_service.compose_preview(product, background, transform)
            
            self.logger.info("Preview composto com sucesso")
            return composition
            
        except Exception as e:
            self.logger.error(f"Erro na composição: {e}")
            return None
    
    def export_thumbnail(self, composition: Image.Image, filename: str = None, original_name: str = None) -> Optional[str]:
        """Exporta thumbnail final"""
        try:
            self.app_state.current_step = "exporting"
            
            result = self.thumbnail_exporter.execute(composition, filename, original_name)
            
            if result.success:
                self.app_state.current_step = "completed"
                self.logger.info(f"Thumbnail exportada: {result.file_path} ({result.size_mb}MB)")
                return result.file_path
            else:
                self.logger.error(f"Erro na exportação: {result.error}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro na exportação: {e}")
            return None
    
    def process_complete_workflow(self, image_path: str, background_path: str, 
                                transform: Transform = None, output_filename: str = None) -> Optional[str]:
        """Executa workflow completo de geração de thumbnail"""
        try:
            self.logger.info(f"Iniciando workflow completo para: {image_path}")
            
            # 1. Validar imagem
            if not self.validate_image(image_path):
                return None
            
            # 2. Remover fundo
            processed_image_path = self.remove_background(image_path)
            if not processed_image_path:
                return None
            
            # 3. Compor com background
            composition = self.compose_preview(processed_image_path, background_path, transform)
            if not composition:
                return None
            
            # 4. Exportar thumbnail
            # Extrair nome original do arquivo para nomenclatura
            original_name = Path(image_path).name
            final_path = self.export_thumbnail(composition, output_filename, original_name)
            if not final_path:
                return None
            
            self.logger.info(f"Workflow completo finalizado: {final_path}")
            return final_path
            
        except Exception as e:
            self.logger.error(f"Erro no workflow completo: {e}")
            return None
    
    def get_status(self) -> dict:
        """Retorna status atual da aplicação"""
        return {
            'current_step': self.app_state.current_step,
            'original_image': self.app_state.original_image,
            'processed_image': self.app_state.processed_image,
            'gradio_available': self.gradio_client.health_check(),
            'backgrounds_count': len(self.load_backgrounds())
        }


def main():
    """Função principal para teste"""
    app = ThumbnailGeneratorApp()
    
    if not app.initialize():
        print("Erro na inicialização da aplicação")
        return
    
    # Exemplo de uso
    print("Status da aplicação:")
    status = app.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Listar backgrounds disponíveis
    backgrounds = app.load_backgrounds()
    print(f"\nBackgrounds disponíveis: {len(backgrounds)}")
    for bg in backgrounds[:3]:  # Mostrar apenas os primeiros 3
        print(f"  - {Path(bg).name}")


if __name__ == "__main__":
    main()