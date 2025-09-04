# Arquitetura - Thumbnail Generator
**Data:** 2025-01-24 | **Versão:** 1.0

## Visão Geral
Aplicação desktop Python com interface Streamlit para processamento de imagens, integração API externa para remoção de fundo e composição visual interativa.

## Stack Técnica

### Frontend (Interface)
- **Streamlit 1.28+** - Interface web local
- **Streamlit Components** - Controles interativos (sliders, file upload)
- **HTML/CSS customizado** - Layout responsivo e preview

### Backend (Processamento)
- **Python 3.8+** - Runtime principal
- **Pillow (PIL)** - Manipulação de imagens
- **gradio_client** - Integração API remoção fundo
- **NumPy** - Operações matriciais para composição

### APIs Externas
- **Gradio BRIA RMBG-1.4** - Remoção de fundo
  - Endpoint: `https://briaai-bria-rmbg-1-4.hf.space/--replicas/ev34l/`
  - API: `/predict`
  - Input: Imagem (PNG/JPG)
  - Output: Imagem sem fundo (PNG)

## Arquitetura de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT UI                         │
├─────────────────┬─────────────────┬─────────────────────┤
│   File Upload   │   Preview Area  │   Controls Panel    │
│   - Drag&Drop   │   - Real-time   │   - Position X/Y    │
│   - Multi-file  │   - 1080x1080   │   - Scale slider    │
│   - PNG/JPG     │   - Background  │   - Rotation        │
└─────────────────┴─────────────────┴─────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────┐
│                 PROCESSING ENGINE                       │
├─────────────────┬─────────────────┬─────────────────────┤
│  Image Loader   │  Background     │   Composition       │
│  - Validation   │  Removal API    │   - Layer merge     │
│  - Format check │  - Gradio call  │   - Transform       │
│  - Size limit   │  - Error handle │   - Export PNG      │
└─────────────────┴─────────────────┴─────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────┐
│                   FILE SYSTEM                           │
├─────────────────┬─────────────────┬─────────────────────┤
│ produtos-sem-   │   backgrounds/  │  thumbnails-prontas/│
│ fundo/ (input)  │   (templates)   │     (output)        │
└─────────────────┴─────────────────┴─────────────────────┘
```

## Fluxo de Dados

### 1. Upload & Validação
```python
user_image → validate_format() → validate_size() → load_to_memory()
```

### 2. Remoção de Fundo
```python
original_image → gradio_client.predict() → background_removed_image
```

### 3. Composição Visual
```python
background + product_image → apply_transforms() → composite_preview
```

### 4. Export Final
```python
final_composition → resize_1080x1080() → save_png()
```

## Decisões Arquiteturais

### DA-001: Streamlit como Frontend
**Contexto:** Necessidade interface rápida e responsiva  
**Decisão:** Streamlit ao invés de Flask/FastAPI  
**Razão:** Desenvolvimento mais rápido, componentes built-in, ideal para MVP  
**Alternativas:** Tkinter (complexo), Flask (overhead), PyQt (licença)  
**Consequências:** (+) Rápido desenvolvimento (-) Limitações customização UI

### DA-002: Gradio API Externa
**Contexto:** Remoção de fundo com qualidade profissional  
**Decisão:** API Gradio BRIA RMBG-1.4 ao invés de libs locais  
**Razão:** Qualidade superior, modelo treinado, sem GPU local  
**Alternativas:** rembg (qualidade menor), U2Net (requer GPU)  
**Consequências:** (+) Qualidade alta (-) Dependência internet

### DA-003: Pillow para Composição
**Contexto:** Manipulação e composição de imagens  
**Decisão:** Pillow (PIL) como engine principal  
**Razão:** Biblioteca padrão Python, performance adequada, documentação  
**Alternativas:** OpenCV (overhead), Wand (dependências)  
**Consequências:** (+) Simplicidade (+) Compatibilidade (-) Performance limitada

## Estrutura de Arquivos

```
thumbnail-generator/
├── app.py                 # Streamlit main app
├── components/
│   ├── uploader.py       # File upload component
│   ├── preview.py        # Preview area component
│   └── controls.py       # Position/scale controls
├── services/
│   ├── background_removal.py  # Gradio API integration
│   ├── image_processor.py     # PIL operations
│   └── file_manager.py        # I/O operations
├── utils/
│   ├── validators.py     # Input validation
│   └── constants.py      # App constants
├── backgrounds/          # Background templates
├── produtos-sem-fundo/   # Input images
├── thumbnails-prontas/   # Output thumbnails
└── requirements.txt      # Dependencies
```

## Dependências Principais

```txt
streamlit>=1.28.0
pillow>=10.0.0
gradio-client>=0.7.0
numpy>=1.24.0
requests>=2.31.0
```

## Considerações de Performance

- **Processamento:** Síncrono por imagem (MVP)
- **Cache:** Streamlit cache para backgrounds
- **Memória:** Liberação após processamento
- **API:** Timeout 30s para Gradio calls
- **Preview:** Redimensionamento otimizado

## Segurança & Validação

- **Input:** Validação formato/tamanho arquivo
- **API:** Error handling para falhas Gradio
- **Output:** Sanitização nomes arquivo
- **Paths:** Validação diretórios permitidos