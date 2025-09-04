# Thumbnail Generator MVP

🎨 **Gerador de Thumbnails Automatizado com Remoção de Fundo**

Sistema MVP para geração automatizada de thumbnails 1080x1080px, integrando remoção de fundo via API Gradio BRIA RMBG-1.4 e composição com backgrounds personalizados.

## 📋 Funcionalidades

- ✅ **Validação de Imagens**: Suporte a PNG, JPG, JPEG, WebP, BMP
- 🎯 **Remoção de Fundo**: Integração com API Gradio BRIA RMBG-1.4
- 🖼️ **Composição Inteligente**: Combinação produto + background com transformações
- 📐 **Padronização**: Export automático em 1080x1080px PNG
- 🏗️ **Clean Architecture**: Separação clara de responsabilidades
- 🧪 **Testes Unitários**: Cobertura das funcionalidades críticas
- 📊 **Logging Estruturado**: Rastreabilidade completa do processo

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- pip ou conda

### Setup do Projeto

```bash
# 1. Clonar/baixar o projeto
cd thumbnail-generator-mvp

# 2. Criar ambiente virtual (recomendado)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente (opcional)
cp .env.example .env
# Editar .env conforme necessário

# 5. Criar estrutura de diretórios
mkdir backgrounds produtos-sem-fundo thumbnails-prontas
```

## 📁 Estrutura do Projeto

```
thumbnail-generator-mvp/
├── src/
│   ├── domain/              # Entidades e regras de negócio
│   │   ├── __init__.py
│   │   └── entities.py
│   ├── application/         # Casos de uso
│   │   ├── __init__.py
│   │   └── use_cases.py
│   ├── infrastructure/      # Implementações concretas
│   │   ├── __init__.py
│   │   ├── gradio_client.py
│   │   ├── image_service.py
│   │   └── file_service.py
│   ├── config.py           # Configurações centralizadas
│   └── main.py             # Aplicação principal
├── tests/                  # Testes unitários
│   ├── __init__.py
│   ├── test_use_cases.py
│   └── test_infrastructure.py
├── backgrounds/            # Imagens de fundo
├── produtos-sem-fundo/     # Produtos processados
├── thumbnails-prontas/     # Saída final
├── requirements.txt        # Dependências
├── .env.example           # Configurações de exemplo
├── example_usage.py       # Exemplos de uso
└── README.md              # Esta documentação
```

## 🎯 Uso Básico

### Exemplo Rápido

```python
from src.main import ThumbnailGeneratorApp
from src.domain.entities import Transform

# Inicializar aplicação
app = ThumbnailGeneratorApp()
app.initialize()

# Workflow completo
result = app.process_complete_workflow(
    image_path="produtos-sem-fundo/produto.png",
    background_path="backgrounds/fundo.png",
    transform=Transform(x=0, y=0, scale=1.0, rotation=0),
    output_filename="minha_thumbnail"
)

print(f"Thumbnail gerada: {result}")
```

### Uso Passo a Passo

```python
from src.main import ThumbnailGeneratorApp
from src.domain.entities import Transform

app = ThumbnailGeneratorApp()
app.initialize()

# 1. Validar imagem
if app.validate_image("produto.png"):
    print("✓ Imagem válida")

# 2. Remover fundo (requer API Gradio)
processed = app.remove_background("produto.png")
if processed:
    print("✓ Fundo removido")

# 3. Listar backgrounds disponíveis
backgrounds = app.load_backgrounds()
print(f"Backgrounds: {len(backgrounds)}")

# 4. Compor preview
transform = Transform(x=50, y=-20, scale=1.2, rotation=5)
composition = app.compose_preview(
    processed, 
    backgrounds[0], 
    transform
)

# 5. Exportar thumbnail final
final_path = app.export_thumbnail(composition, "minha_thumbnail")
print(f"Salvo em: {final_path}")
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```env
# API Gradio
GRADIO_ENDPOINT=https://briaai-bria-rmbg-1-4.hf.space/--replicas/ev34l/
GRADIO_TIMEOUT=30
GRADIO_MAX_RETRIES=3

# Processamento
CANVAS_SIZE=1080x1080
MAX_FILE_SIZE_MB=50
IMAGE_QUALITY=95

# Diretórios
BACKGROUNDS_DIR=backgrounds
PRODUCTS_DIR=produtos-sem-fundo
OUTPUT_DIR=thumbnails-prontas

# Logging
LOG_LEVEL=INFO
LOG_FILE=thumbnail_generator.log
```

### Configuração Programática

```python
from src.config import AppConfig

config = AppConfig(base_path="/meu/projeto")
config.gradio.timeout = 60
config.image.canvas_size = (1200, 1200)

# Validar configuração
errors = config.validate()
if errors:
    print(f"Erros: {errors}")
```

## 📊 API Reference

### ThumbnailGeneratorApp

#### Métodos Principais

```python
# Inicialização
app.initialize() -> bool

# Validação
app.validate_image(image_path: str) -> bool

# Processamento
app.remove_background(image_path: str) -> Optional[str]
app.load_backgrounds() -> List[str]
app.compose_preview(product_path: str, background_path: str, transform: Transform) -> Optional[Image.Image]
app.export_thumbnail(composition: Image.Image, filename: str = None) -> Optional[str]

# Workflow completo
app.process_complete_workflow(
    image_path: str,
    background_path: str,
    transform: Transform = None,
    output_filename: str = None
) -> Optional[str]

# Status
app.get_status() -> dict
```

### Transform

```python
from src.domain.entities import Transform

transform = Transform(
    x=0,        # Offset horizontal (px)
    y=0,        # Offset vertical (px)
    scale=1.0,  # Escala (1.0 = 100%)
    rotation=0  # Rotação (graus)
)
```

### Entidades de Resultado

```python
# ValidationResult
result.is_valid: bool
result.error: Optional[str]
result.width: int
result.height: int
result.format: str
result.file_size: int

# BackgroundRemovalResult
result.success: bool
result.image_no_bg: Optional[str]
result.error: Optional[str]
result.processing_time: float
result.api_status: str  # 'idle', 'processing', 'success', 'api_error', 'timeout'

# ExportResult
result.success: bool
result.file_path: Optional[str]
result.filename: str
result.error: Optional[str]
result.size_mb: float
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Testes com cobertura
pytest --cov=src

# Testes específicos
pytest tests/test_use_cases.py
pytest tests/test_infrastructure.py

# Testes verbosos
pytest -v
```

## 📝 Exemplos Práticos

### Executar Exemplos

```bash
# Executar todos os exemplos
python example_usage.py
```

### Batch Processing

```python
import os
from src.main import ThumbnailGeneratorApp
from src.domain.entities import Transform

app = ThumbnailGeneratorApp()
app.initialize()

# Processar todos os produtos
products_dir = "produtos-sem-fundo"
background_path = "backgrounds/fundo_padrao.png"

for filename in os.listdir(products_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        product_path = os.path.join(products_dir, filename)
        
        result = app.process_complete_workflow(
            image_path=product_path,
            background_path=background_path,
            output_filename=f"thumb_{filename}"
        )
        
        if result:
            print(f"✓ {filename} -> {result}")
        else:
            print(f"❌ Erro processando {filename}")
```

### Transformações Personalizadas

```python
# Produto pequeno no canto
transform_canto = Transform(x=-300, y=-300, scale=0.6, rotation=0)

# Produto grande centralizado
transform_destaque = Transform(x=0, y=0, scale=1.5, rotation=0)

# Produto rotacionado
transform_artistico = Transform(x=0, y=0, scale=1.0, rotation=15)
```

## 🔍 Troubleshooting

### Problemas Comuns

**1. API Gradio indisponível**
```
Erro: Health check falhou
Solução: Verificar conectividade e endpoint da API
```

**2. Permissões de arquivo**
```
Erro: Sem permissão de escrita
Solução: Verificar permissões do diretório de saída
```

**3. Formato de imagem não suportado**
```
Erro: Formato não suportado
Solução: Converter para PNG, JPG, JPEG, WebP ou BMP
```

**4. Arquivo muito grande**
```
Erro: Arquivo excede limite
Solução: Redimensionar imagem ou ajustar MAX_FILE_SIZE_MB
```

### Logs e Debug

```python
# Ativar debug
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Verificar logs
tail -f thumbnail_generator.log
```

## 🏗️ Arquitetura

### Clean Architecture

- **Domain**: Entidades e regras de negócio puras
- **Application**: Casos de uso e orquestração
- **Infrastructure**: Implementações concretas (APIs, arquivos, etc.)

### Dependências

- **Pillow**: Processamento de imagens
- **gradio-client**: Integração com API Gradio
- **requests**: Comunicação HTTP
- **pytest**: Framework de testes

## 📈 Performance

### Otimizações

- Cache de backgrounds carregados
- Processamento assíncrono (futuro)
- Compressão inteligente de imagens
- Cleanup automático de arquivos temporários

### Limites

- Tamanho máximo: 50MB por imagem
- Timeout API: 30 segundos
- Formatos suportados: PNG, JPG, JPEG, WebP, BMP
- Saída padronizada: 1080x1080px PNG

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente com testes
4. Execute `pytest` e `black src/`
5. Submeta um Pull Request

## 📄 Licença

Este projeto é um MVP para uso interno. Consulte a documentação específica do projeto para termos de uso.

---

**Desenvolvido com Clean Architecture e boas práticas de Backend** 🚀