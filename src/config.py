"""Configuration - Centralized Settings"""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class GradioConfig:
    """Configurações da API Gradio"""
    endpoint: str = "https://briaai-bria-rmbg-1-4.hf.space/--replicas/ev34l/"
    timeout: int = 30
    api_name: str = "/predict"
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class ImageConfig:
    """Configurações de processamento de imagem"""
    canvas_size: tuple[int, int] = (1080, 1080)
    max_file_size_mb: int = 50
    supported_formats: tuple[str, ...] = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
    default_quality: int = 95
    thumbnail_size: tuple[int, int] = (150, 150)


@dataclass
class PathConfig:
    """Configurações de caminhos"""
    base_path: Path
    backgrounds_dir: Path
    products_dir: Path
    output_dir: Path
    temp_dir: Optional[Path] = None
    
    def __post_init__(self):
        if self.temp_dir is None:
            self.temp_dir = self.base_path / "temp"


@dataclass
class LoggingConfig:
    """Configurações de logging"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "thumbnail_generator.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


class AppConfig:
    """Configuração principal da aplicação"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
        
        # Configurações específicas
        self.gradio = GradioConfig(
            endpoint=os.getenv("GRADIO_ENDPOINT", GradioConfig.endpoint),
            timeout=int(os.getenv("GRADIO_TIMEOUT", str(GradioConfig.timeout))),
            max_retries=int(os.getenv("GRADIO_MAX_RETRIES", str(GradioConfig.max_retries)))
        )
        
        self.image = ImageConfig(
            canvas_size=self._parse_size(os.getenv("CANVAS_SIZE", "1080x1080")),
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", str(ImageConfig.max_file_size_mb))),
            default_quality=int(os.getenv("IMAGE_QUALITY", str(ImageConfig.default_quality)))
        )
        
        self.paths = PathConfig(
            base_path=self.base_path,
            backgrounds_dir=self.base_path / os.getenv("BACKGROUNDS_DIR", "backgrounds"),
            products_dir=self.base_path / os.getenv("PRODUCTS_DIR", "produtos-sem-fundo"),
            output_dir=self.base_path / os.getenv("OUTPUT_DIR", "thumbnails-prontas"),
            temp_dir=self.base_path / os.getenv("TEMP_DIR", "temp")
        )
        
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", LoggingConfig.level),
            file_path=os.getenv("LOG_FILE", LoggingConfig.file_path)
        )
        
        # Configurações gerais
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.version = "1.0.0"
    
    def _parse_size(self, size_str: str) -> tuple[int, int]:
        """Parse string de tamanho (ex: '1080x1080')"""
        try:
            width, height = size_str.split('x')
            return (int(width), int(height))
        except (ValueError, AttributeError):
            return ImageConfig.canvas_size
    
    def validate(self) -> list[str]:
        """Valida configurações e retorna lista de erros"""
        errors = []
        
        # Validar caminhos
        if not self.paths.base_path.exists():
            errors.append(f"Diretório base não existe: {self.paths.base_path}")
        
        # Validar configurações de imagem
        if self.image.canvas_size[0] <= 0 or self.image.canvas_size[1] <= 0:
            errors.append("Tamanho do canvas deve ser positivo")
        
        if self.image.max_file_size_mb <= 0:
            errors.append("Tamanho máximo de arquivo deve ser positivo")
        
        # Validar Gradio
        if not self.gradio.endpoint.startswith(('http://', 'https://')):
            errors.append("Endpoint Gradio deve ser uma URL válida")
        
        if self.gradio.timeout <= 0:
            errors.append("Timeout Gradio deve ser positivo")
        
        return errors
    
    def create_directories(self) -> None:
        """Cria diretórios necessários"""
        for directory in [self.paths.backgrounds_dir, self.paths.products_dir, 
                         self.paths.output_dir, self.paths.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> dict:
        """Converte configuração para dicionário"""
        return {
            'version': self.version,
            'environment': self.environment,
            'debug': self.debug,
            'base_path': str(self.paths.base_path),
            'gradio': {
                'endpoint': self.gradio.endpoint,
                'timeout': self.gradio.timeout,
                'max_retries': self.gradio.max_retries
            },
            'image': {
                'canvas_size': self.image.canvas_size,
                'max_file_size_mb': self.image.max_file_size_mb,
                'supported_formats': self.image.supported_formats,
                'default_quality': self.image.default_quality
            },
            'paths': {
                'backgrounds': str(self.paths.backgrounds_dir),
                'products': str(self.paths.products_dir),
                'output': str(self.paths.output_dir),
                'temp': str(self.paths.temp_dir)
            }
        }


# Instância global de configuração
config = AppConfig()


def load_config(base_path: str = ".") -> AppConfig:
    """Carrega configuração da aplicação"""
    global config
    config = AppConfig(base_path)
    
    # Validar configuração
    errors = config.validate()
    if errors:
        raise ValueError(f"Erros na configuração: {'; '.join(errors)}")
    
    return config


def get_config() -> AppConfig:
    """Retorna configuração atual"""
    return config