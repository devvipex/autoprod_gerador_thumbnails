"""Domain Entities - Thumbnail Generator MVP"""
from dataclasses import dataclass
from typing import Optional, Literal
from PIL import Image


@dataclass
class ValidationResult:
    """Resultado da validação de imagem"""
    valid: bool
    error: Optional[str]
    image: Optional[Image.Image]
    size_mb: float
    dimensions: tuple[int, int]


@dataclass
class BackgroundRemovalResult:
    """Resultado da remoção de fundo via API Gradio"""
    success: bool
    image_no_bg: Optional[Image.Image]
    error: Optional[str]
    processing_time: float
    api_status: Literal["success", "timeout", "api_error", "network_error"]


@dataclass
class BackgroundInfo:
    """Informações de um background disponível"""
    filename: str
    path: str
    thumbnail_path: str
    dimensions: tuple[int, int]


@dataclass
class Transform:
    """Transformações aplicadas ao produto"""
    x: int  # Posição X (-540 a 540)
    y: int  # Posição Y (-540 a 540)
    scale: float  # Escala (0.1 a 2.0)
    rotation: float  # Rotação (-45 a 45 graus)

    def __post_init__(self):
        """Validação dos limites"""
        self.x = max(-540, min(540, self.x))
        self.y = max(-540, min(540, self.y))
        self.scale = max(0.1, min(2.0, self.scale))
        self.rotation = max(-45, min(45, self.rotation))


@dataclass
class ExportResult:
    """Resultado do export de thumbnail"""
    success: bool
    file_path: Optional[str]
    filename: Optional[str]
    error: Optional[str]
    size_mb: float


@dataclass
class AppState:
    """Estado global da aplicação"""
    current_step: Literal["upload", "remove_bg", "compose", "export"]
    original_image: Optional[Image.Image]
    processed_image: Optional[Image.Image]
    selected_background: Optional[BackgroundInfo]
    current_transform: Transform
    composition: Optional[Image.Image]

    def __post_init__(self):
        if self.current_transform is None:
            self.current_transform = Transform(x=0, y=0, scale=1.0, rotation=0.0)