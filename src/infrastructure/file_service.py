"""File Service - Infrastructure Layer"""
import os
import logging
from typing import List, Optional
from pathlib import Path
from PIL import Image
import uuid
from datetime import datetime


class FileService:
    """Serviço para operações de arquivo"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.logger = logging.getLogger(__name__)
        
        # Diretórios padrão
        self.backgrounds_dir = self.base_path / "backgrounds"
        self.products_dir = self.base_path / "produtos-sem-fundo"
        self.output_dir = self.base_path / "thumbnails-prontas"
        
        # Formatos suportados
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
    
    def ensure_directories(self) -> None:
        """Garante que diretórios necessários existem"""
        for directory in [self.backgrounds_dir, self.products_dir, self.output_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Diretório garantido: {directory}")
    
    def load_image(self, file_path: str) -> Optional[Image.Image]:
        """Carrega imagem de arquivo"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                self.logger.error(f"Arquivo não encontrado: {file_path}")
                return None
            
            if path.suffix.lower() not in self.supported_formats:
                self.logger.error(f"Formato não suportado: {path.suffix}")
                return None
            
            image = Image.open(path)
            self.logger.info(f"Imagem carregada: {file_path} ({image.size})")
            return image
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar imagem {file_path}: {e}")
            return None
    
    def save_image(self, image: Image.Image, file_path: str, quality: int = 95) -> bool:
        """Salva imagem em arquivo"""
        try:
            path = Path(file_path)
            
            # Criar diretório pai se necessário
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Determinar formato baseado na extensão
            format_map = {
                '.png': 'PNG',
                '.jpg': 'JPEG',
                '.jpeg': 'JPEG',
                '.webp': 'WEBP',
                '.bmp': 'BMP'
            }
            
            file_format = format_map.get(path.suffix.lower(), 'PNG')
            
            # Configurar parâmetros de salvamento
            save_kwargs = {}
            if file_format == 'JPEG':
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
                # Converter RGBA para RGB se necessário
                if image.mode == 'RGBA':
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
            elif file_format == 'PNG':
                save_kwargs['optimize'] = True
            
            # Salvar imagem
            image.save(path, format=file_format, **save_kwargs)
            
            # Verificar se arquivo foi criado
            if path.exists():
                file_size = path.stat().st_size
                self.logger.info(f"Imagem salva: {file_path} ({file_size} bytes)")
                return True
            else:
                self.logger.error(f"Falha ao salvar: {file_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar imagem {file_path}: {e}")
            return False
    
    def list_backgrounds(self) -> List[str]:
        """Lista arquivos de background disponíveis"""
        try:
            if not self.backgrounds_dir.exists():
                self.logger.warning(f"Diretório de backgrounds não existe: {self.backgrounds_dir}")
                return []
            
            backgrounds = []
            for file_path in self.backgrounds_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                    backgrounds.append(str(file_path))
            
            self.logger.info(f"Encontrados {len(backgrounds)} backgrounds")
            return sorted(backgrounds)
            
        except Exception as e:
            self.logger.error(f"Erro ao listar backgrounds: {e}")
            return []
    
    def list_products(self) -> List[str]:
        """Lista arquivos de produto disponíveis"""
        try:
            if not self.products_dir.exists():
                self.logger.warning(f"Diretório de produtos não existe: {self.products_dir}")
                return []
            
            products = []
            for file_path in self.products_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                    products.append(str(file_path))
            
            self.logger.info(f"Encontrados {len(products)} produtos")
            return sorted(products)
            
        except Exception as e:
            self.logger.error(f"Erro ao listar produtos: {e}")
            return []
    
    def generate_unique_filename(self, base_name: str, extension: str = ".png") -> str:
        """Gera nome único para arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Limpar base_name
        clean_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_name = clean_name.replace(' ', '_')
        
        if clean_name:
            filename = f"{clean_name}_{timestamp}_{unique_id}{extension}"
        else:
            filename = f"thumbnail_{timestamp}_{unique_id}{extension}"
        
        return filename
    
    def get_output_path(self, filename: str) -> str:
        """Retorna caminho completo para arquivo de saída"""
        return str(self.output_dir / filename)
    
    def validate_write_permissions(self, directory: str) -> bool:
        """Valida permissões de escrita em diretório"""
        try:
            test_file = Path(directory) / ".write_test"
            test_file.touch()
            test_file.unlink()
            return True
        except Exception as e:
            self.logger.error(f"Sem permissão de escrita em {directory}: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """Retorna informações sobre arquivo"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {}
            
            stat = path.stat()
            return {
                'name': path.name,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'extension': path.suffix.lower(),
                'exists': True
            }
        except Exception as e:
            self.logger.error(f"Erro ao obter info do arquivo {file_path}: {e}")
            return {'exists': False, 'error': str(e)}
    
    def cleanup_temp_files(self, temp_dir: str = None) -> None:
        """Limpa arquivos temporários"""
        try:
            import tempfile
            temp_path = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
            
            # Procurar arquivos temporários do projeto
            for temp_file in temp_path.glob("thumbnail_temp_*"):
                try:
                    temp_file.unlink()
                    self.logger.info(f"Arquivo temporário removido: {temp_file}")
                except Exception as e:
                    self.logger.warning(f"Erro ao remover {temp_file}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Erro na limpeza de arquivos temporários: {e}")