"""Gradio Client - Infrastructure Layer"""
import os
import logging
import tempfile
from typing import Optional
from gradio_client import Client
from PIL import Image

# Fallback local para remoção de fundo
try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False


class GradioBackgroundRemovalClient:
    """Cliente para API Gradio BRIA RMBG-1.4"""
    
    def __init__(self, endpoint: str = "briaai/BRIA-RMBG-1.4"):
        self.endpoint = endpoint
        self.client = None
        self.timeout = 60
        self.logger = logging.getLogger(__name__)
        self.use_fallback = False
        
        # Inicializar sessão rembg se disponível
        if REMBG_AVAILABLE:
            try:
                self.rembg_session = new_session('u2net')
                self.logger.info("Fallback local rembg inicializado")
            except Exception as e:
                self.logger.warning(f"Erro ao inicializar rembg: {e}")
                self.rembg_session = None
        else:
            self.rembg_session = None
    
    def _get_client(self) -> Client:
        """Inicializa cliente Gradio se necessário"""
        if self.client is None:
            try:
                # Usar endpoint do Hugging Face Spaces
                self.client = Client(self.endpoint)
                self.logger.info(f"Cliente Gradio conectado: {self.endpoint}")
            except Exception as e:
                self.logger.error(f"Erro ao conectar Gradio: {e}")
                # Ativar fallback imediatamente se não conseguir conectar
                self.use_fallback = True
                raise
        return self.client
    
    def predict(self, image_path: str) -> Optional[str]:
        """Chama API Gradio para remoção de fundo"""
        try:
            client = self._get_client()
            
            # Verificar se arquivo existe
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {image_path}")
            
            self.logger.debug(f"Enviando imagem para Gradio: {image_path}")
            
            # Chamar API com timeout
            result = client.predict(
                image_path,
                api_name="/predict"
            )
            
            if result:
                self.logger.debug(f"Resultado recebido: {result}")
                return result
            else:
                self.logger.debug("API retornou resultado vazio")
                return None
                
        except Exception as e:
            # Reduzir verbosidade dos logs de erro da API Gradio
            if "has not enabled verbose error reporting" in str(e):
                self.logger.debug(f"API Gradio indisponível: {e}")
            else:
                self.logger.error(f"Erro na chamada Gradio: {e}")
            # Ativar fallback para próximas chamadas
            self.use_fallback = True
            raise
    
    def _remove_background_local(self, image: Image.Image) -> Optional[Image.Image]:
        """Remove fundo usando rembg local como fallback"""
        if not self.rembg_session:
            self.logger.error("Rembg não disponível para fallback")
            return None
            
        try:
            self.logger.debug("Usando fallback local rembg")
            
            # Converter para bytes
            import io
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Remover fundo
            output = remove(img_byte_arr, session=self.rembg_session)
            
            # Converter de volta para PIL
            result_image = Image.open(io.BytesIO(output))
            
            self.logger.debug("Remoção de fundo local concluída")
            return result_image
            
        except Exception as e:
            self.logger.error(f"Erro no fallback local: {e}")
            return None
    
    def remove_background(self, image: Image.Image) -> Optional[Image.Image]:
        """Remove fundo de uma imagem PIL com fallback local"""
        temp_input = None
        temp_output = None
        
        # Sempre tentar API Gradio primeiro se estiver disponível
        if self.health_check():
            self.use_fallback = False  # Reset flag se API estiver disponível
            
        if not self.use_fallback:
            try:
                # Salvar imagem temporariamente
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                    temp_input = f.name
                    image.save(temp_input, 'PNG')
                
                # Chamar API
                result_path = self.predict(temp_input)
                
                if result_path and os.path.exists(result_path):
                    # Carregar resultado
                    result_image = Image.open(result_path)
                    temp_output = result_path
                    return result_image
                else:
                    raise Exception("API retornou resultado vazio")
                    
            except Exception as e:
                # Reduzir verbosidade para erros conhecidos da API Gradio
                if "has not enabled verbose error reporting" in str(e):
                    self.logger.debug(f"API Gradio indisponível, usando fallback local")
                else:
                    self.logger.warning(f"API Gradio falhou: {e}")
                self.use_fallback = True  # Ativar fallback para próximas chamadas
                
            finally:
                # Limpar arquivos temporários
                for temp_file in [temp_input, temp_output]:
                    if temp_file and os.path.exists(temp_file):
                        try:
                            os.unlink(temp_file)
                        except Exception as e:
                            self.logger.warning(f"Erro ao limpar arquivo temporário {temp_file}: {e}")
        
        # Usar fallback local
        return self._remove_background_local(image)
    
    def health_check(self) -> bool:
        """Verifica se API está disponível"""
        try:
            client = self._get_client()
            
            # Se chegou até aqui, o cliente foi criado com sucesso
            # Isso significa que a API está disponível
            # Verificar se o cliente tem os métodos necessários
            if hasattr(client, 'predict'):
                return True
            else:
                self.logger.warning("Health check falhou - cliente não tem método predict")
                return False
                
        except Exception as e:
            self.logger.error(f"Health check falhou: {e}")
            return False