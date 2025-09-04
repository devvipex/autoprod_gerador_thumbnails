# G0 - Intake Preflight Checklist
**Data:** 2025-01-24  
**Objetivo:** Alinhar objetivo/escopo/restrições/risco/métricas e validar DoR

## ✅ Confirmações Realizadas

### Tipo de Projeto
- [x] **Aplicação Web Offline** - Python + Streamlit
- [x] **Processamento de Imagens** - Remoção de fundo + composição
- [x] **Ferramenta de Produtividade** - Criação de thumbnails e-commerce

### Objetivo (1-2 frases)
**Criar uma aplicação offline que permita remover fundos de imagens de produtos e compor thumbnails padronizados (1080x1080px) para e-commerce, com interface intuitiva para posicionamento e escala dos elementos.**

### Métricas de Sucesso
- Processar imagens em lote com remoção de fundo automática
- Gerar thumbnails 1080x1080px consistentes
- Interface responsiva para ajuste de posicionamento/escala
- Tempo de processamento < 30s por imagem

### Restrições Confirmadas
- **Stack:** Python + Streamlit (obrigatório)
- **API Externa:** Gradio BRIA RMBG-1.4 para remoção de fundo
- **Formato Output:** PNG 1080x1080px fixo
- **Modo:** Aplicação offline/local
- **Dependência:** Internet para API Gradio

### Ambientes/Dados de Teste
- [x] **Pasta de produtos:** `produtos-sem-fundo/` (4 imagens disponíveis)
- [x] **Backgrounds:** `backgrounds/Podium1.png` disponível
- [x] **Exemplo referência:** `exemplo.png` presente
- [x] **Output:** `thumbnails-prontas/` (pasta existente)

### Riscos/Dependências Mapeados

| Risco | Impacto | Mitigação |
|-------|---------|----------|
| API Gradio indisponível | Alto | Cache local + fallback manual |
| Qualidade remoção fundo | Médio | Validação visual + ajuste manual |
| Performance lote grande | Médio | Processamento assíncrono + progress |
| Dependência internet | Baixo | Documentar requisito + offline mode |

### Lacunas/Decisões Pendentes
- [x] **Formatos input aceitos** (PNG, JPG, WEBP?)
- [x] **Limite tamanho arquivo** (MB máximo?)
- [x] **Backgrounds customizados** (upload próprio?) (tem a pasta background e visualiza-se eles na interface)
- [x] **Presets posicionamento** (centro, canto, etc?)
- [x] **Batch processing** (quantas imagens simultâneas?) (Quantas for possível)

## ✅ DoR Validado
- [x] **Objetivo claro:** Thumbnails e-commerce padronizados
- [x] **Stack definida:** Python + Streamlit + Gradio API
- [x] **Dados teste:** Imagens produtos + backgrounds disponíveis
- [x] **Output especificado:** PNG 1080x1080px
- [x] **Critérios aceite:** Interface posicionamento + export funcional

## Próximos Passos
1. **G1 - Brief Aprovado:** Criar 00-brief.md estruturado
2. **Definir MVP Slices:** Upload → Remoção → Composição → Export
3. **Arquitetura técnica:** Streamlit components + Gradio integration

---
**Status:** ✅ G0 APROVADO - Prosseguir para G1