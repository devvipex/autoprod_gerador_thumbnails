# Contratos - Thumbnail Generator MVP

## Visão Geral dos Contratos

Este documento define todos os contratos de API, modelos de dados e interfaces para integração entre frontend e backend do sistema de geração de thumbnails.

## Contratos de API REST

### 1. Inicialização do Sistema

**Endpoint:** `POST /api/initialize`

**Request:** Vazio

**Response:**
```json
{
  "success": boolean,
  "gradio_available": boolean,
  "message": string
}
```

### 2. Listar Backgrounds

**Endpoint:** `GET /api/backgrounds`

**Response:**
```json
{
  "backgrounds": BackgroundInfo[],
  "count": number
}
```

### 3. Validar Imagem

**Endpoint:** `POST /api/validate-image`

**Request:**
```json
{
  "image_path": string
}
```

**Response:**
```json
{
  "valid": boolean,
  "error": string | null,
  "size_mb": number,
  "dimensions": [number, number],
  "format": string
}
```

### 4. Compor Preview

**Endpoint:** `POST /api/compose-preview`

**Request:**
```json
{
  "product_path": string,
  "background_path": string,
  "transform": Transform
}
```

**Response:**
```json
{
  "success": boolean,
  "preview_base64": string,
  "composition_size": [number, number],
  "transform_applied": Transform
}
```

### 5. Exportar Thumbnail

**Endpoint:** `POST /api/export-thumbnail`

**Request:**
```json
{
  "product_path": string,
  "background_path": string,
  "transform": Transform,
  "filename": string | null,
  "original_name": string
}
```

**Response:**
```json
{
  "success": boolean,
  "export_path": string,
  "filename": string,
  "size_mb": number,
  "dimensions": [number, number],
  "format": string
}
```

### 6. Status do Sistema

**Endpoint:** `GET /api/status`

**Response:**
```json
{
  "current_step": string,
  "original_image": string | null,
  "processed_image": string | null,
  "gradio_available": boolean,
  "backgrounds_count": number,
  "last_composition": CompositionInfo | null
}
```

### 7. Gerenciar Templates

**Endpoint:** `POST /api/templates`

**Request:**
```json
{
  "name": string,
  "description": string,
  "transform": Transform,
  "background_preference": string
}
```

**Endpoint:** `GET /api/templates`

**Response:**
```json
{
  "templates": Template[]
}
```

## Modelos de Dados TypeScript

### Transform
```typescript
interface Transform {
  x: number;        // Posição X: -500 a 500
  y: number;        // Posição Y: -500 a 500
  scale: number;    // Escala: 0.1 a 3.0
  rotation: number; // Rotação: -180 a 180 graus
}
```

### BackgroundInfo
```typescript
interface BackgroundInfo {
  filename: string;      // Nome do arquivo
  path: string;          // Caminho completo
  thumbnail_path: string; // Caminho do thumbnail
  dimensions: [number, number]; // [largura, altura]
}
```

### ValidationResult
```typescript
interface ValidationResult {
  valid: boolean;
  error: string | null;
  size_mb: number;
  dimensions: [number, number];
  format?: string;
}
```

### ExportResult
```typescript
interface ExportResult {
  success: boolean;
  export_path: string;
  filename: string;
  size_mb: number;
  dimensions: [number, number];
  format: string;
}
```

### CompositionInfo
```typescript
interface CompositionInfo {
  product: string;
  background: string;
  transform: Transform;
  timestamp?: string;
}
```

### Template
```typescript
interface Template {
  id: string;
  name: string;
  description: string;
  transform: Transform;
  background_preference: string;
  created_at: string;
}
```

## Contratos de Estado da Aplicação

### AppState
```typescript
interface AppState {
  current_step: 'upload' | 'processing' | 'composing' | 'completed' | 'error';
  original_image: string | null;
  processed_image: string | null;
  selected_background: string | null;
  current_transform: Transform;
  composition: any | null; // PIL Image object
}
```

## Códigos de Erro Padronizados

### Estrutura de Erro
```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  }
}
```

### Códigos de Erro

- `INVALID_IMAGE`: Imagem inválida ou formato não suportado
- `FILE_NOT_FOUND`: Arquivo não encontrado
- `PROCESSING_ERROR`: Erro durante processamento
- `EXPORT_ERROR`: Erro durante exportação
- `GRADIO_UNAVAILABLE`: Serviço Gradio indisponível
- `INVALID_TRANSFORM`: Parâmetros de transformação inválidos
- `TEMPLATE_NOT_FOUND`: Template não encontrado

## Limites e Validações

### Limites de Transform
```typescript
const TRANSFORM_LIMITS = {
  x: { min: -500, max: 500 },
  y: { min: -500, max: 500 },
  scale: { min: 0.1, max: 3.0 },
  rotation: { min: -180, max: 180 }
};
```

### Formatos Suportados
```typescript
const SUPPORTED_FORMATS = ['PNG', 'JPG', 'JPEG'];
const MAX_FILE_SIZE_MB = 10;
const TARGET_DIMENSIONS = [1080, 1080];
```

## Eventos WebSocket (Futuro)

### Client → Server
```typescript
interface ClientEvent {
  event: 'preview_update' | 'transform_change' | 'background_change';
  data: {
    transform?: Transform;
    background_path?: string;
    product_path?: string;
  };
}
```

### Server → Client
```typescript
interface ServerEvent {
  event: 'preview_ready' | 'processing_status' | 'error';
  data: {
    preview_base64?: string;
    status?: string;
    progress?: number;
    error?: ApiError;
    timestamp: string;
  };
}
```

## Contratos de Integração Python

### ThumbnailGeneratorApp Interface
```python
class ThumbnailGeneratorApp:
    def initialize(self) -> bool
    def validate_image(self, image_path: str) -> bool
    def load_backgrounds(self) -> List[str]
    def compose_preview(self, product_path: str, background_path: str, transform: Transform) -> Optional[Image.Image]
    def export_thumbnail(self, composition: Image.Image, filename: Optional[str], original_name: Optional[str]) -> Optional[str]
    def get_status(self) -> Dict[str, Any]
```

### Use Cases Interface
```python
class ImageValidationUseCase:
    def execute(self, image_path: str) -> ValidationResult

class BackgroundLoaderUseCase:
    def execute(self) -> List[BackgroundInfo]

class ThumbnailExportUseCase:
    def execute(self, composition: Image.Image, filename: Optional[str], original_name: Optional[str]) -> ExportResult
```

## Versionamento de API

### Headers Obrigatórios
```
API-Version: 1.0
Content-Type: application/json
Accept: application/json
```

### Compatibilidade
- Versão atual: `1.0`
- Mudanças breaking requerem nova versão major
- Mudanças aditivas incrementam versão minor
- Correções incrementam versão patch

## Exemplo de Implementação de Cliente

### Classe Cliente TypeScript
```typescript
class ThumbnailGeneratorClient {
  private baseUrl: string;
  
  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }
  
  async initialize(): Promise<{success: boolean, gradio_available: boolean}> {
    const response = await fetch(`${this.baseUrl}/api/initialize`, {
      method: 'POST',
      headers: { 'API-Version': '1.0' }
    });
    return response.json();
  }
  
  async getBackgrounds(): Promise<{backgrounds: BackgroundInfo[], count: number}> {
    const response = await fetch(`${this.baseUrl}/api/backgrounds`);
    return response.json();
  }
  
  async composePreview(request: {
    product_path: string,
    background_path: string,
    transform: Transform
  }): Promise<{success: boolean, preview_base64: string}> {
    const response = await fetch(`${this.baseUrl}/api/compose-preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'API-Version': '1.0'
      },
      body: JSON.stringify(request)
    });
    return response.json();
  }
  
  async exportThumbnail(request: {
    product_path: string,
    background_path: string,
    transform: Transform,
    filename?: string,
    original_name: string
  }): Promise<ExportResult> {
    const response = await fetch(`${this.baseUrl}/api/export-thumbnail`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'API-Version': '1.0'
      },
      body: JSON.stringify(request)
    });
    return response.json();
  }
}
```

## Contratos de Interface

### 1. Upload & Validação

#### `validate_image(file) → ValidationResult`
**Descrição:** Valida arquivo de imagem carregado

**Input:**
```python
file: UploadedFile  # Streamlit file object
```

**Output:**
```python
ValidationResult = {
    "valid": bool,
    "error": str | None,
    "image": PIL.Image | None,
    "size_mb": float,
    "dimensions": (width: int, height: int)
}
```

**Exemplo:**
```python
# Sucesso
{
    "valid": True,
    "error": None,
    "image": <PIL.Image>,
    "size_mb": 2.5,
    "dimensions": (800, 600)
}

# Erro
{
    "valid": False,
    "error": "Formato não suportado. Use PNG ou JPG.",
    "image": None,
    "size_mb": 0,
    "dimensions": (0, 0)
}
```

**Estados:**
- `idle`: Aguardando upload
- `validating`: Processando arquivo
- `success`: Arquivo válido
- `error`: Arquivo inválido

---

### 2. Remoção de Fundo

#### `remove_background(image_path) → BackgroundRemovalResult`
**Descrição:** Remove fundo via API Gradio BRIA RMBG-1.4

**Input:**
```python
image_path: str  # Caminho absoluto da imagem
```

**Output:**
```python
BackgroundRemovalResult = {
    "success": bool,
    "image_no_bg": PIL.Image | None,
    "error": str | None,
    "processing_time": float,
    "api_status": "success" | "timeout" | "api_error" | "network_error"
}
```

**Exemplo:**
```python
# Sucesso
{
    "success": True,
    "image_no_bg": <PIL.Image>,
    "error": None,
    "processing_time": 12.5,
    "api_status": "success"
}

# Erro API
{
    "success": False,
    "image_no_bg": None,
    "error": "API Gradio indisponível. Tente novamente.",
    "processing_time": 30.0,
    "api_status": "timeout"
}
```

**Estados:**
- `idle`: Aguardando imagem
- `processing`: Chamando API Gradio
- `success`: Fundo removido
- `api_error`: Falha na API
- `timeout`: Timeout 30s

---

### 3. Gerenciamento de Backgrounds

#### `load_backgrounds() → List[BackgroundInfo]`
**Descrição:** Carrega backgrounds disponíveis da pasta

**Output:**
```python
BackgroundInfo = {
    "filename": str,
    "path": str,
    "thumbnail": PIL.Image,  # 150x150px preview
    "dimensions": (width: int, height: int),
    "size_mb": float
}
```

**Exemplo:**
```python
[
    {
        "filename": "Podium1.png",
        "path": "backgrounds/Podium1.png",
        "thumbnail": <PIL.Image>,
        "dimensions": (1080, 1080),
        "size_mb": 1.2
    }
]
```

---

### 4. Composição e Preview

#### `compose_preview(product, background, transform) → PIL.Image`
**Descrição:** Gera preview da composição final

**Input:**
```python
product: PIL.Image        # Produto sem fundo
background: PIL.Image     # Background selecionado
transform: Transform      # Transformações aplicadas
```

**Transform DTO:**
```python
Transform = {
    "x": int,           # Posição X (-540 a 540)
    "y": int,           # Posição Y (-540 a 540)
    "scale": float,     # Escala (0.1 a 2.0)
    "rotation": float   # Rotação (-45 a 45 graus)
}
```

**Output:**
```python
PIL.Image  # Preview 1080x1080px
```

**Exemplo Transform:**
```python
{
    "x": 0,      # Centro horizontal
    "y": -100,   # Ligeiramente acima do centro
    "scale": 0.8, # 80% do tamanho original
    "rotation": 0 # Sem rotação
}
```

---

### 5. Export Final

#### `export_thumbnail(composition, filename) → ExportResult`
**Descrição:** Salva thumbnail final padronizado

**Input:**
```python
composition: PIL.Image  # Composição final
filename: str | None    # Nome opcional (auto-gerado se None)
```

**Output:**
```python
ExportResult = {
    "success": bool,
    "file_path": str | None,
    "filename": str | None,
    "error": str | None,
    "size_mb": float
}
```

**Exemplo:**
```python
# Sucesso
{
    "success": True,
    "file_path": "thumbnails-prontas/produto_20250124_143022.png",
    "filename": "produto_20250124_143022.png",
    "error": None,
    "size_mb": 0.8
}

# Erro
{
    "success": False,
    "file_path": None,
    "filename": None,
    "error": "Erro ao salvar arquivo. Verifique permissões.",
    "size_mb": 0
}
```

## Estados da Aplicação

### Estado Global
```python
AppState = {
    "current_step": "upload" | "remove_bg" | "compose" | "export",
    "original_image": PIL.Image | None,
    "processed_image": PIL.Image | None,
    "selected_background": str | None,
    "transform": Transform,
    "preview": PIL.Image | None,
    "is_processing": bool,
    "error_message": str | None
}
```

### Fluxo de Estados
```
upload → remove_bg → compose → export
   ↓         ↓          ↓        ↓
 idle → processing → ready → success
   ↓         ↓          ↓        ↓
 error ← api_error ← error ← error
```

## Configurações e Constantes

```python
CONFIG = {
    "MAX_FILE_SIZE_MB": 10,
    "SUPPORTED_FORMATS": ["PNG", "JPG", "JPEG"],
    "OUTPUT_SIZE": (1080, 1080),
    "API_TIMEOUT": 30,
    "GRADIO_ENDPOINT": "https://briaai-bria-rmbg-1-4.hf.space/--replicas/ev34l/",
    "BACKGROUNDS_DIR": "backgrounds/",
    "OUTPUT_DIR": "thumbnails-prontas/",
    "TRANSFORM_LIMITS": {
        "x": (-540, 540),
        "y": (-540, 540),
        "scale": (0.1, 2.0),
        "rotation": (-45, 45)
    }
}
```

## Error Codes

| Code | Descrição | Ação Usuário |
|------|-----------|---------------|
| `INVALID_FORMAT` | Formato não suportado | Usar PNG/JPG |
| `FILE_TOO_LARGE` | Arquivo > 10MB | Reduzir tamanho |
| `API_TIMEOUT` | Gradio timeout | Tentar novamente |
| `API_ERROR` | Falha API Gradio | Verificar internet |
| `SAVE_ERROR` | Erro ao salvar | Verificar permissões |
| `BACKGROUND_NOT_FOUND` | Background inválido | Selecionar outro |

---

**Última atualização:** 2025-01-24  
**Próxima revisão:** Durante implementação das stories