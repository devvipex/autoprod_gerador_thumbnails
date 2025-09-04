# Escopo - Thumbnail Generator para E-commerce
**Data:** 2025-01-24 | **Versão:** 1.0

## Problema

### Situação Atual
Criação manual de thumbnails para produtos de e-commerce é:
- **Demorada:** Remoção de fundo manual por imagem
- **Inconsistente:** Tamanhos e posicionamentos variados
- **Custosa:** Requer designer ou ferramentas pagas
- **Limitante:** Dificulta escala de catálogo

### Impacto no Negócio
- Tempo excessivo para lançar produtos
- Inconsistência visual prejudica conversão
- Custo alto para manter catálogo atualizado
- Dependência de recursos externos

## Visão MVP

### Solução Proposta
**Aplicação desktop que automatiza 80% do processo de criação de thumbnails**, permitindo:

1. **Upload simples** de imagens de produtos
2. **Remoção automática** de fundo via IA
3. **Composição visual** com backgrounds padronizados
4. **Ajuste interativo** de posição e escala
5. **Export padronizado** em 1080x1080px

### Valor Entregue
- **Velocidade:** De 15min → 2min por thumbnail
- **Consistência:** 100% thumbnails no padrão 1080x1080px
- **Qualidade:** Remoção de fundo profissional via IA
- **Autonomia:** Sem dependência de designer externo

## Definition of Ready (DoR)

### Para Iniciar Qualquer Feature
- [ ] **Contrato/stub** documentado em CONTRACTS.md
- [ ] **Rotas/wire** descritos (componentes Streamlit)
- [ ] **Estados UX** definidos (loading/empty/error/success)
- [ ] **Owner/labels** atribuídos com critérios de aceite
- [ ] **Mock/dados teste** disponíveis

### Exemplo DoR - Feature Upload
- [x] Contrato: `upload_image(file) → validated_image`
- [x] Estados: idle, uploading, success, error (formato inválido)
- [x] Mock: Imagens teste em `produtos-sem-fundo/`
- [x] Critérios: Aceita PNG/JPG, rejeita outros, mostra preview

## Definition of Done (DoD)

### Gates Obrigatórios
- [ ] **Build:** Código roda sem erros, lint OK
- [ ] **Contract:** Interface documentada e testada
- [ ] **Visual:** UI checklist 100% (responsivo, estados, a11y)
- [ ] **E2E:** Fluxo crítico funciona end-to-end
- [ ] **Docs:** Documentação atualizada

### Critérios Específicos MVP
- [ ] **Performance:** < 30s processamento por imagem
- [ ] **Output:** PNG 1080x1080px válido sempre
- [ ] **Error Handling:** Falhas API não quebram app
- [ ] **UX:** Interface intuitiva sem tutorial

## Gates do Projeto (G0 → G5)

### ✅ G0 - Intake Preflight
**Status:** APROVADO  
**Objetivo:** Alinhar objetivo/escopo/restrições  
**Entregues:**
- [x] Checklist Pre-flight completo
- [x] Lacunas e decisões mapeadas
- [x] DoR validado

### ✅ G1 - Brief Aprovado
**Status:** AGUARDANDO APROVAÇÃO  
**Objetivo:** Brief estruturado (≤1 pág)  
**Entregues:**
- [x] `/docs/00-brief.md` criado
- [ ] **PENDENTE:** Aprovação stakeholder

### ✅ G2 - Slices Definidas
**Status:** COMPLETO  
**Objetivo:** Fatiar MVP e definir sprints  
**Entregas:**
- [x] `/docs/10-escopo.md` (este arquivo)
- [x] `/docs/20-sprints.md` com slices atômicas

### ⏳ G3 - Padrões Publicados
**Status:** PENDENTE  
**Objetivo:** Publicar padrões e ADRs  
**Entregas:**
- [ ] `/docs/40-interfaces.md` (componentes Streamlit)
- [ ] `/docs/50-qa.md` (testes e validações)
- [ ] `/docs/70-ops.md` (deploy e execução)
- [ ] `/docs/60-decisoes/` (ADRs técnicos)

### ⏳ G4 - Checkpoint Projecter
**Status:** PENDENTE  
**Objetivo:** Verificar gates e evidências  
**Entregas:**
- [ ] Checklist checkpoint completo
- [ ] `/docs/90-changelog.md` atualizado
- [ ] ADRs ajustadas conforme implementação

### ⏳ G5 - Encerramento
**Status:** PENDENTE  
**Objetivo:** Fechar ciclo com release notes  
**Entregas:**
- [ ] Resumo + métricas atingidas
- [ ] Próxima sprint proposta (melhorias)

## Restrições e Limitações

### Técnicas
- **Stack fixa:** Python + Streamlit (não negociável)
- **API externa:** Dependência internet para Gradio
- **Formato output:** Apenas PNG 1080x1080px
- **Processamento:** Síncrono (uma imagem por vez)

### Funcionais
- **Backgrounds:** Apenas pré-definidos (sem upload customizado)
- **Formatos input:** PNG e JPG apenas
- **Batch:** Processamento sequencial manual
- **Integração:** Sem conexão com plataformas e-commerce

### Não-Funcionais
- **Performance:** < 30s por imagem (incluindo API)
- **Disponibilidade:** Aplicação local (sem servidor)
- **Usabilidade:** Interface intuitiva sem treinamento
- **Confiabilidade:** 95% sucesso remoção fundo

## Próximos Passos

1. **Aguardar G1-Approval** do brief
2. **Criar 20-sprints.md** com slices atômicas
3. **Definir interfaces** em 40-interfaces.md
4. **Iniciar desenvolvimento** após G3 aprovado

---
**Última atualização:** 2025-01-24  
**Próxima revisão:** Após G1-Approval