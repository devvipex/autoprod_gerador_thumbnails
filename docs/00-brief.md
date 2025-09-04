# Brief - Thumbnail Generator para E-commerce
**Data:** 2025-01-24 | **Versão:** 1.0 | **Status:** Aguardando G1-Approval

## Objetivo
Criar aplicação offline Python+Streamlit que automatize a criação de thumbnails padronizados (1080x1080px) para produtos de e-commerce, removendo fundos via API Gradio e permitindo composição visual interativa.

## Cenários Top 3

### 1. Processamento Básico
**Usuário** carrega imagem produto → **Sistema** remove fundo via Gradio → **Usuário** posiciona sobre background → **Sistema** exporta PNG 1080x1080px

### 2. Ajuste Visual
**Usuário** ajusta escala/posição do produto → **Preview** atualiza em tempo real → **Usuário** confirma e salva thumbnail final

### 3. Lote de Produtos
**Usuário** carrega múltiplas imagens → **Sistema** processa sequencialmente → **Usuário** ajusta cada uma → **Sistema** salva lote completo

## Escopo MVP

### ✅ Incluído
- **Upload:** Drag&drop ou seleção de imagens (PNG/JPG)
- **Remoção Fundo:** Integração API Gradio BRIA RMBG-1.4 <mcreference link="https://briaai-bria-rmbg-1-4.hf.space/--replicas/ev34l/" index="0">0</mcreference>
- **Backgrounds:** Seleção de fundos pré-definidos (pasta backgrounds/)
- **Posicionamento:** Controles interativos (X/Y, escala, rotação)
- **Preview:** Visualização tempo real da composição
- **Export:** Salvar PNG 1080x1080px (pasta thumbnails-prontas/)
- **Interface:** Streamlit responsivo com controles intuitivos

### ❌ Fora de Escopo
- Upload de backgrounds customizados
- Edição avançada (filtros, correção cor)
- Processamento batch automático
- Integração com plataformas e-commerce
- Versionamento/histórico de thumbnails

## Métricas de Sucesso
- **Performance:** < 30s processamento por imagem
- **Qualidade:** Remoção fundo sem artefatos visíveis
- **Usabilidade:** Posicionamento intuitivo sem tutorial
- **Output:** 100% thumbnails 1080x1080px válidos
- **Confiabilidade:** 95% sucesso remoção fundo

## Restrições

### Técnicas
- **Stack obrigatória:** Python 3.8+ + Streamlit
- **API externa:** Gradio BRIA RMBG-1.4 (requer internet)
- **Formato fixo:** Output PNG 1080x1080px apenas
- **Modo:** Aplicação local/offline (exceto API)

### Recursos
- **Prazo:** Sprint única (1-2 semanas)
- **Dados:** Imagens teste já disponíveis
- **Ambiente:** Desenvolvimento local Windows

## Regras Negativas
- **NÃO** implementar upload de backgrounds customizados
- **NÃO** adicionar filtros/efeitos avançados
- **NÃO** criar sistema de usuários/autenticação
- **NÃO** integrar com APIs e-commerce
- **NÃO** suportar formatos além PNG/JPG input
- **NÃO** permitir outputs diferentes de 1080x1080px

---

## 🚨 Solicitação G1-Approval
**Este brief está pronto para aprovação. Confirme se:**
1. Objetivo e cenários estão claros
2. Escopo MVP é suficiente e factível
3. Restrições são aceitáveis
4. Métricas são mensuráveis

**Próximo passo:** Após aprovação → G2 (Definir Slices e Sprints)