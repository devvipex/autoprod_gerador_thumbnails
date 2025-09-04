# API Documentation - Thumbnail Generator

## Visão Geral

Esta documentação descreve a API do sistema de geração de thumbnails para integração com o frontend. O sistema permite composição de produtos com backgrounds, aplicação de transformações e exportação de thumbnails padronizadas.

## Arquitetura

```
Frontend (Streamlit)
    ↓ HTTP/WebSocket
API Gateway/Backend
    ↓ Python Integration
ThumbnailGeneratorApp
    ↓
[Domain] ← [Application] ← [Infrastructure]
```

## Classe Principal: ThumbnailGeneratorApp

### Inicialização

```python
from src.main import ThumbnailGeneratorApp

app = ThumbnailGeneratorApp()
success = app.initialize()
```

## Endpoints da API

### 1. Inicialização do Sistema

**Endpoint:** `POST /api/initialize`

**Descrição:** Inicializa o sistema e verifica disponibilidade de serviços.

**Response:**
```json
{
  "success": true,
  "gradio_available": false,
  "message": "Sistema inicializado com sucesso"
}
```

### 2. Listar Backgrounds Disponíveis

**Endpoint:** `GET /api/backgrounds`

**Descrição:** Retorna lista de backgrounds disponíveis na pasta `backgrounds/`.

**Response:**
```json
{
  "backgrounds": [
    {
      "filename": "Podium1.png",
      "path": "backgrounds/Podium1.png",
      "thumbnail_path": "backgrounds/Podium1.png",
      "dimensions": [1080, 1080]
    },
    {
      "filename": "background_exemplo.png",
      "path": "backgrounds/background_exemplo.png",
      "thumbnail_path": "backgrounds/background_exemplo.png",
      "dimensions": [1080, 1080]
    }
  ],
  "count": 2
}
```

**Implementação Python:**
```python
def get_backgrounds():
    backgrounds = app.load_backgrounds()
    return {
        "backgrounds": [
            {
                "filename": Path(bg).name,
                "path": bg,
                "thumbnail_path": bg,
                "dimensions": [1080, 1080]  # Padrão
            } for bg in backgrounds
        ],
        "count": len(backgrounds)
    }
```

### 3. Validar Imagem de Produto

**Endpoint:** `POST /api/validate-image`

**Body:**
```json
{
  "image_path": "produtos-sem-fundo/produto.png"
}
```

**Response:**
```json
{
  "valid": true,
  "error": null,
  "size_mb": 0.5,
  "dimensions": [551, 550],
  "format": "PNG"
}
```

### 4. Remover Fundo (Opcional)

**Endpoint:** `POST /api/remove-background`

**Body:**
```json
{
  "image_path": "produtos-sem-fundo/produto.png"
}
```

**Response:**
```json
{
  "success": true,
  "processed_image_path": "temp/produto_processed.png",
  "processing_time": 2.5,
  "original_size": [551, 550],
  "processed_size": [551, 550]
}
```

### 5. Compor Preview

**Endpoint:** `POST /api/compose-preview`

**Body:**
```json
{
  "product_path": "produtos-sem-fundo/produto.png",
  "background_path": "backgrounds/Podium1.png",
  "transform": {
    "x": 50,
    "y": 25,
    "scale": 0.8,
    "rotation": 15
  }
}
```

**Response:**
```json
{
  "success": true,
  "preview_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "composition_size": [1080, 1080],
  "transform_applied": {
    "x": 50,
    "y": 25,
    "scale": 0.8,
    "rotation": 15
  }
}
```

### 6. Exportar Thumbnail Final

**Endpoint:** `POST /api/export-thumbnail`

**Body:**
```json
{
  "product_path": "produtos-sem-fundo/produto.png",
  "background_path": "backgrounds/Podium1.png",
  "transform": {
    "x": 50,
    "y": 25,
    "scale": 0.8,
    "rotation": 15
  },
  "filename": null,
  "original_name": "Produto Exemplo.png"
}
```

**Response:**
```json
{
  "success": true,
  "export_path": "thumbnails-prontas/Produto Exemplo_thumb.png",
  "filename": "Produto Exemplo_thumb.png",
  "size_mb": 0.15,
  "dimensions": [1080, 1080],
  "format": "PNG"
}
```

### 7. Obter Status do Sistema

**Endpoint:** `GET /api/status`

**Response:**
```json
{
  "current_step": "completed",
  "original_image": "produtos-sem-fundo/produto.png",
  "processed_image": null,
  "gradio_available": false,
  "backgrounds_count": 2,
  "last_composition": {
    "product": "produtos-sem-fundo/produto.png",
    "background": "backgrounds/Podium1.png",
    "transform": {
      "x": 50,
      "y": 25,
      "scale": 0.8,
      "rotation": 15
    }
  }
}
```

## Modelos de Dados

### Transform

```typescript
interface Transform {
  x: number;        // Posição X (-500 a 500)
  y: number;        // Posição Y (-500 a 500)
  scale: number;    // Escala (0.1 a 3.0)
  rotation: number; // Rotação em graus (-180 a 180)
}
```

### BackgroundInfo

```typescript
interface BackgroundInfo {
  filename: string;
  path: string;
  thumbnail_path: string;
  dimensions: [number, number];
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

## Sistema de Templates

### Salvar Template

**Endpoint:** `POST /api/templates`

**Body:**
```json
{
  "name": "Produto Centralizado",
  "description": "Produto centralizado com escala 0.8",
  "transform": {
    "x": 0,
    "y": 0,
    "scale": 0.8,
    "rotation": 0
  },
  "background_preference": "Podium1.png"
}
```

### Listar Templates

**Endpoint:** `GET /api/templates`

**Response:**
```json
{
  "templates": [
    {
      "id": "template-001",
      "name": "Produto Centralizado",
      "description": "Produto centralizado com escala 0.8",
      "transform": {
        "x": 0,
        "y": 0,
        "scale": 0.8,
        "rotation": 0
      },
      "background_preference": "Podium1.png",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Controles do Frontend

### 1. Seletor de Background

```typescript
// Componente para seleção de background
interface BackgroundSelector {
  backgrounds: BackgroundInfo[];
  selectedBackground: string;
  onBackgroundChange: (path: string) => void;
}
```

### 2. Controles de Transformação

```typescript
// Controles de posicionamento e escala
interface TransformControls {
  transform: Transform;
  onTransformChange: (transform: Transform) => void;
  
  // Limites
  limits: {
    x: { min: -500, max: 500 };
    y: { min: -500, max: 500 };
    scale: { min: 0.1, max: 3.0 };
    rotation: { min: -180, max: 180 };
  };
}
```

### 3. Preview em Tempo Real

```typescript
// Componente de preview
interface PreviewComponent {
  productPath: string;
  backgroundPath: string;
  transform: Transform;
  onPreviewUpdate: (previewData: string) => void;
}
```

## Fluxo de Trabalho Recomendado

### 1. Inicialização

```javascript
// 1. Inicializar sistema
const initResponse = await fetch('/api/initialize', { method: 'POST' });
const { success } = await initResponse.json();

// 2. Carregar backgrounds disponíveis
const backgroundsResponse = await fetch('/api/backgrounds');
const { backgrounds } = await backgroundsResponse.json();
```

### 2. Upload e Validação

```javascript
// 3. Validar imagem do produto
const validateResponse = await fetch('/api/validate-image', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ image_path: productPath })
});
const validation = await validateResponse.json();
```

### 3. Composição Interativa

```javascript
// 4. Atualizar preview em tempo real
const updatePreview = async (transform) => {
  const response = await fetch('/api/compose-preview', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      product_path: productPath,
      background_path: selectedBackground,
      transform: transform
    })
  });
  
  const { preview_base64 } = await response.json();
  previewImage.src = preview_base64;
};

// Debounce para performance
const debouncedUpdate = debounce(updatePreview, 300);
```

### 4. Exportação Final

```javascript
// 5. Exportar thumbnail final
const exportResponse = await fetch('/api/export-thumbnail', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    product_path: productPath,
    background_path: selectedBackground,
    transform: finalTransform,
    original_name: originalFileName
  })
});

const { export_path, filename } = await exportResponse.json();
```

## Tratamento de Erros

### Códigos de Status HTTP

- `200`: Sucesso
- `400`: Erro de validação (imagem inválida, parâmetros incorretos)
- `404`: Arquivo não encontrado
- `500`: Erro interno do servidor
- `503`: Serviço indisponível (Gradio offline)

### Estrutura de Erro

```json
{
  "error": {
    "code": "INVALID_IMAGE",
    "message": "Formato de imagem não suportado",
    "details": {
      "supported_formats": ["PNG", "JPG", "JPEG"],
      "received_format": "GIF"
    }
  }
}
```

## Performance e Otimizações

### 1. Cache de Backgrounds

- Backgrounds são carregados uma vez na inicialização
- Cache de thumbnails para preview rápido

### 2. Debounce de Preview

- Usar debounce de 300ms para atualizações de transform
- Cancelar requisições pendentes ao fazer nova alteração

### 3. Compressão de Imagens

- Preview em base64 com qualidade reduzida
- Export final em qualidade máxima

## Exemplo de Implementação Frontend (React)

```jsx
import React, { useState, useEffect, useCallback } from 'react';
import { debounce } from 'lodash';

const ThumbnailGenerator = () => {
  const [backgrounds, setBackgrounds] = useState([]);
  const [selectedBackground, setSelectedBackground] = useState('');
  const [transform, setTransform] = useState({
    x: 0, y: 0, scale: 1.0, rotation: 0
  });
  const [preview, setPreview] = useState('');
  const [productPath, setProductPath] = useState('');

  // Carregar backgrounds na inicialização
  useEffect(() => {
    const loadBackgrounds = async () => {
      const response = await fetch('/api/backgrounds');
      const { backgrounds } = await response.json();
      setBackgrounds(backgrounds);
      if (backgrounds.length > 0) {
        setSelectedBackground(backgrounds[0].path);
      }
    };
    loadBackgrounds();
  }, []);

  // Atualizar preview com debounce
  const updatePreview = useCallback(
    debounce(async (newTransform) => {
      if (!productPath || !selectedBackground) return;
      
      const response = await fetch('/api/compose-preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_path: productPath,
          background_path: selectedBackground,
          transform: newTransform
        })
      });
      
      const { preview_base64 } = await response.json();
      setPreview(preview_base64);
    }, 300),
    [productPath, selectedBackground]
  );

  // Atualizar preview quando transform mudar
  useEffect(() => {
    updatePreview(transform);
  }, [transform, updatePreview]);

  const handleExport = async () => {
    const response = await fetch('/api/export-thumbnail', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_path: productPath,
        background_path: selectedBackground,
        transform: transform,
        original_name: 'Produto.png'
      })
    });
    
    const result = await response.json();
    console.log('Thumbnail exportada:', result.filename);
  };

  return (
    <div className="thumbnail-generator">
      {/* Seletor de Background */}
      <div className="background-selector">
        <h3>Backgrounds</h3>
        {backgrounds.map(bg => (
          <button
            key={bg.path}
            onClick={() => setSelectedBackground(bg.path)}
            className={selectedBackground === bg.path ? 'active' : ''}
          >
            <img src={bg.thumbnail_path} alt={bg.filename} />
            {bg.filename}
          </button>
        ))}
      </div>

      {/* Controles de Transformação */}
      <div className="transform-controls">
        <h3>Posicionamento</h3>
        
        <label>
          X: {transform.x}
          <input
            type="range"
            min="-500"
            max="500"
            value={transform.x}
            onChange={(e) => setTransform(prev => ({
              ...prev,
              x: parseInt(e.target.value)
            }))}
          />
        </label>
        
        <label>
          Y: {transform.y}
          <input
            type="range"
            min="-500"
            max="500"
            value={transform.y}
            onChange={(e) => setTransform(prev => ({
              ...prev,
              y: parseInt(e.target.value)
            }))}
          />
        </label>
        
        <label>
          Escala: {transform.scale}
          <input
            type="range"
            min="0.1"
            max="3.0"
            step="0.1"
            value={transform.scale}
            onChange={(e) => setTransform(prev => ({
              ...prev,
              scale: parseFloat(e.target.value)
            }))}
          />
        </label>
        
        <label>
          Rotação: {transform.rotation}°
          <input
            type="range"
            min="-180"
            max="180"
            value={transform.rotation}
            onChange={(e) => setTransform(prev => ({
              ...prev,
              rotation: parseInt(e.target.value)
            }))}
          />
        </label>
      </div>

      {/* Preview */}
      <div className="preview">
        <h3>Preview</h3>
        {preview && (
          <img 
            src={preview} 
            alt="Preview" 
            style={{ maxWidth: '400px', maxHeight: '400px' }}
          />
        )}
      </div>

      {/* Ações */}
      <div className="actions">
        <button onClick={handleExport}>Exportar Thumbnail</button>
      </div>
    </div>
  );
};

export default ThumbnailGenerator;
```

## Considerações de Segurança

1. **Validação de Entrada**: Sempre validar paths de arquivo
2. **Sanitização**: Sanitizar nomes de arquivo para evitar path traversal
3. **Limites de Tamanho**: Implementar limites para upload de imagens
4. **Rate Limiting**: Implementar rate limiting para APIs de processamento
5. **CORS**: Configurar CORS adequadamente para frontend

## Monitoramento e Logs

- Logs estruturados para todas as operações
- Métricas de performance (tempo de processamento)
- Alertas para falhas de processamento
- Monitoramento de uso de recursos

---

**Versão:** 1.0.0  
**Última Atualização:** Janeiro 2024  
**Contato:** Backend Expert - TRAE AI