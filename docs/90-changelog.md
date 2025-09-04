# Changelog - Thumbnail Generator
**Projeto:** Thumbnail Generator para E-commerce  
**Versão:** 1.0-MVP  
**Formato:** [Keep a Changelog](https://keepachangelog.com/)

## [1.0.3] - 2025-01-24 - Sistema de Redimensionamento Automático

### Adicionado
- 🎯 **Sistema de Redimensionamento Automático**: Nova funcionalidade que ajusta automaticamente o tamanho dos produtos para manter consistência visual
- 🔧 **Função `calculate_auto_scale`**: Calcula escala baseada no tamanho do produto para ocupar ~60% do canvas
- 🎛️ **Toggle de Redimensionamento**: Controle no preview e processamento para ativar/desativar a funcionalidade
- 📊 **Escala Inteligente**: Limites de escala entre 0.2 e 2.0 para evitar extremos

### Corrigido
- 🔧 **CRÍTICO**: Corrigido erro "cannot access local variable 'use_auto_scale' where it is not associated with a value"
- ✅ **Inicialização de Variáveis**: Variável `use_auto_scale` agora é inicializada corretamente antes do uso
- ✅ **Session State**: Persistência do estado do redimensionamento automático entre execuções
- ✅ **Compatibilidade Python 3.12**: Atualizadas dependências para versões compatíveis

### Detalhes Técnicos
- **Problema**: Variável `use_auto_scale` era definida após seu uso na função `render_preview_controls`
- **Solução**: Movida inicialização da variável para antes da criação do preview
- **Resultado**: Preview funciona corretamente com redimensionamento automático

## [1.0.2] - 2025-01-24 - Otimizações Finais

### Adicionado
- 🎯 **Priorização inteligente da API Gradio**: Sistema agora sempre tenta usar API Gradio primeiro
- 🔄 **Reset automático de fallback**: Flag de fallback é resetada quando API está disponível
- 📝 **Preservação de nomes originais**: Arquivos mantêm nome original no formato `nome_original_thumb.png`
- 🔍 **Health check otimizado**: Validação mais precisa da disponibilidade da API Gradio

### Corrigido
- 🔧 **CRÍTICO**: Corrigida lógica de priorização entre API Gradio e fallback local
- ✅ **API Gradio**: Agora tem prioridade absoluta quando disponível
- ✅ **Nomenclatura**: Preservação consistente do nome original dos arquivos
- ✅ **Logs**: Reduzida verbosidade de logs desnecessários do ONNX Runtime

### Detalhes Técnicos
- **Problema**: Flag `use_fallback` nunca era resetada, mantendo sistema em modo fallback
- **Solução**: Adicionado `health_check()` antes de cada processamento com reset automático
- **Resultado**: Qualidade máxima com modelo BRIA RMBG-1.4 sempre que possível

## [1.0.1] - 2025-01-24

### Corrigido
- 🔧 **CRÍTICO**: Corrigida inicialização do `ThumbnailExportUseCase` no main.py
- ✅ Thumbnails agora são geradas corretamente na pasta `thumbnails-prontas/`
- ✅ Adicionados scripts de teste direto (`test_thumbnail_generation.py`)
- ✅ Adicionado gerador completo (`generate_all_thumbnails.py`)
- ✅ Validação de funcionamento com 17 thumbnails geradas (8.63 MB total)

### Detalhes Técnicos
- **Problema**: `ThumbnailExportUseCase` estava sendo inicializado com `file_service` mas esperava apenas `output_dir`
- **Solução**: Alterado `ThumbnailExportUseCase(self.file_service)` para `ThumbnailExportUseCase("thumbnails-prontas")`
- **Resultado**: Taxa de sucesso 100% na geração de thumbnails

## [1.0.0] - 2025-01-24

### Adicionado
- ✅ Estrutura base do projeto seguindo Clean Architecture
- ✅ Implementação completa dos casos de uso (Use Cases)
- ✅ Integração com API Gradio para remoção de fundo
- ✅ Sistema de composição de imagens com transformações
- ✅ Export padronizado PNG 1080x1080px
- ✅ Testes unitários abrangentes (30 testes)
- ✅ Documentação técnica completa
- ✅ Scripts de exemplo e validação

### Técnico
- Domain Layer: Entidades e regras de negócio
- Application Layer: Casos de uso e orquestração
- Infrastructure Layer: Serviços externos (Gradio, File System)
- Cobertura de testes: Use Cases e Infrastructure
- Logging estruturado e tratamento de erros
- Configuração flexível via arquivo config.py

## [Unreleased] - Planejado

### Planned
- Story 1: Setup Base + Upload component ✅ COMPLETO
- Story 2: Integração API Gradio BRIA RMBG-1.4 ✅ COMPLETO
- Story 3: Sistema backgrounds + preview ✅ COMPLETO
- Story 4: Controles posicionamento interativo ✅ COMPLETO
- Story 5: Export PNG 1080x1080px ✅ COMPLETO
- Story 6: Testes E2E + polish final ✅ COMPLETO

## [0.1.1] - 2025-01-24 - Revisões Usuário

### Changed
- **00-brief.md** - Adicionada referência específica API Gradio BRIA RMBG-1.4
- **10-escopo.md** - Refinamentos nos critérios DoR/DoD e gates; G2 marcado como COMPLETO
- **20-sprints.md** - Detalhamento aprimorado das 6 stories com contratos; Transform DTO padronizado
- **CONTRACTS.md** - Interfaces validadas e exemplos expandidos
- **90-changelog.md** - Status dos gates atualizados
- **G0-preflight-checklist.md** - Lacunas/decisões pendentes atualizadas pelo usuário

### Fixed
- Consistência definição Transform entre CONTRACTS.md e 20-sprints.md
- Status gates G0→G2 sincronizados entre documentos
- Referências API Gradio padronizadas em todos os arquivos

### Validated
- Consistência entre documentos após revisões
- Alinhamento técnico com decisões arquiteturais
- Contratos de interface sincronizados entre stories e especificações

## [0.1.0] - 2025-01-24 - Documentação MVP

### Added
- **G0-preflight-checklist.md** - Validação inicial projeto
- **00-brief.md** - Brief estruturado aguardando G1-Approval
- **10-escopo.md** - Problema, visão MVP e gates G0→G5
- **20-sprints.md** - 6 stories atômicas com DoR/DoD
- **30-arquitetura.md** - Stack técnica e decisões arquiteturais
- **CONTRACTS.md** - Interfaces e DTOs completos
- **DECISIONS.md** - 6 ADRs documentados
- **90-changelog.md** - Este arquivo de versionamento

### Decisions
- **ADR-001:** Streamlit como framework frontend
- **ADR-002:** API Gradio BRIA RMBG-1.4 para remoção fundo
- **ADR-003:** Pillow (PIL) para processamento imagens
- **ADR-004:** Estrutura modular mas simples
- **ADR-005:** Output fixo PNG 1080x1080px
- **ADR-006:** Processamento síncrono para MVP

### Project Structure
```
/docs/
├── G0-preflight-checklist.md  ✅ Completo
├── 00-brief.md               ✅ Aguardando G1-Approval
├── 10-escopo.md              ✅ Completo
├── 20-sprints.md             ✅ 6 stories definidas
├── 30-arquitetura.md         ✅ Stack + decisões
├── CONTRACTS.md              ✅ Interfaces documentadas
├── DECISIONS.md              ✅ 6 ADRs + decisões menores
└── 90-changelog.md           ✅ Este arquivo
```

### Gates Status
- ✅ **G0 - Intake Preflight:** APROVADO
- 🔄 **G1 - Brief Aprovado:** AGUARDANDO STAKEHOLDER
- ✅ **G2 - Slices Definidas:** COMPLETO
- ⏳ **G3 - Padrões Publicados:** PENDENTE
- ⏳ **G4 - Checkpoint:** PENDENTE
- ⏳ **G5 - Encerramento:** PENDENTE

### Metrics Baseline
- **Documentos criados:** 8 arquivos
- **Stories mapeadas:** 6 slices atômicas
- **ADRs documentados:** 6 decisões arquiteturais
- **Contratos definidos:** 5 interfaces principais
- **Tempo planejamento:** ~4 horas

---

## Template para Próximas Versões

### Durante Desenvolvimento
```markdown
## [0.2.0] - YYYY-MM-DD - Story 1 Complete

### Added
- Upload component com drag&drop
- Validação PNG/JPG até 10MB
- Preview imagem carregada
- Error handling formato inválido

### Technical
- Streamlit file_uploader implementado
- PIL validation pipeline
- Error states e mensagens PT-BR

### Tests
- ✅ Build: Código roda sem warnings
- ✅ Visual: UI checklist 100%
- ✅ Docs: README atualizado

### Performance
- Upload validation: < 2s
- Preview loading: < 1s
```

### Template Story Complete
```markdown
## [X.Y.Z] - YYYY-MM-DD - Story N Complete

### Added
- Feature principal implementada
- Sub-features e melhorias

### Changed
- Modificações em features existentes

### Fixed
- Bugs corrigidos
- Issues resolvidas

### Technical
- Implementações técnicas
- Refatorações
- Otimizações

### Tests
- Gates passados (Build/Contract/Visual/E2E/Docs)
- Métricas atingidas

### Performance
- Benchmarks atualizados
```

## Convenções de Versionamento

### Semantic Versioning
- **MAJOR.MINOR.PATCH** (ex: 1.0.0)
- **MAJOR:** Breaking changes ou release final
- **MINOR:** Novas features (stories completas)
- **PATCH:** Bug fixes e melhorias menores

### Tags de Status
- ✅ **Completo:** Feature 100% funcional
- 🔄 **Em Progresso:** Desenvolvimento ativo
- 📋 **Planejado:** Definido mas não iniciado
- ⏳ **Pendente:** Aguardando dependência
- ❌ **Bloqueado:** Impedimento identificado
- 🚀 **Released:** Entregue para usuário final

### Categorias de Mudança
- **Added:** Novas features
- **Changed:** Modificações features existentes
- **Deprecated:** Features marcadas para remoção
- **Removed:** Features removidas
- **Fixed:** Bug fixes
- **Security:** Correções segurança
- **Technical:** Mudanças internas (refactor, deps)
- **Docs:** Atualizações documentação
- **Tests:** Adições/modificações testes
- **Performance:** Melhorias performance

---

## Próximos Marcos

### G1-Approval (Aguardando)
- [ ] Stakeholder aprova 00-brief.md
- [ ] Confirma escopo MVP e restrições
- [ ] Autoriza início desenvolvimento

### G3-Padrões (Próximo)
- [ ] 40-interfaces.md (componentes Streamlit)
- [ ] 50-qa.md (estratégia testes)
- [ ] 70-ops.md (deploy e execução)
- [ ] Estrutura código base

### MVP Release (Meta)
- [ ] 6 stories implementadas e testadas
- [ ] Aplicação funcional end-to-end
- [ ] Documentação usuário final
- [ ] Métricas MVP atingidas

---

**Última atualização:** 2025-01-24 14:30  
**Próxima atualização:** Após G1-Approval ou início Story 1  
**Responsável:** Projecter (Orquestração MVP-Ready)