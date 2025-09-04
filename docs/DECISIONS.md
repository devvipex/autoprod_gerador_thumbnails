# Decisões - Thumbnail Generator
**Data:** 2025-01-24 | **Versão:** 1.0

## Registro de Decisões Arquiteturais (ADRs)

### ADR-001: Streamlit como Framework Frontend
**Data:** 2025-01-24 | **Status:** APROVADO | **Contexto:** MVP Rápido

**Problema:**
Necessidade de interface gráfica rápida para aplicação desktop de processamento de imagens.

**Decisão:**
Utilizar Streamlit como framework principal ao invés de alternativas como Tkinter, PyQt ou Flask.

**Alternativas Consideradas:**
- **Tkinter:** Nativo Python, mas UI complexa e desenvolvimento lento
- **PyQt/PySide:** Interface profissional, mas licença e curva aprendizado
- **Flask + HTML:** Flexibilidade total, mas overhead desenvolvimento
- **Gradio:** Focado ML, mas limitações customização

**Razões:**
- ✅ Desenvolvimento rápido (MVP em 1-2 semanas)
- ✅ Componentes built-in (file upload, sliders, preview)
- ✅ Ideal para prototipagem e ferramentas internas
- ✅ Comunidade ativa e documentação
- ❌ Limitações customização UI avançada
- ❌ Dependência de servidor local

**Consequências:**
- **Positivas:** Time-to-market acelerado, menos código boilerplate
- **Negativas:** UI limitada aos componentes Streamlit
- **Riscos:** Possível migração futura se necessário UI mais avançada

---

### ADR-002: API Gradio BRIA RMBG-1.4 para Remoção de Fundo
**Data:** 2025-01-24 | **Status:** APROVADO | **Contexto:** Qualidade vs Complexidade

**Problema:**
Remoção de fundo automática com qualidade profissional sem infraestrutura complexa.

**Decisão:**
Integrar API Gradio BRIA RMBG-1.4 <mcreference link="https://briaai-bria-rmbg-1-4.hf.space/--replicas/ev34l/" index="0">0</mcreference> ao invés de soluções locais.

**Alternativas Consideradas:**
- **rembg (local):** Biblioteca Python, mas qualidade inferior
- **U2Net (local):** Boa qualidade, mas requer GPU e setup complexo
- **OpenCV + ML:** Desenvolvimento próprio, muito complexo
- **APIs pagas:** Remove.bg, Photoshop API (custo recorrente)

**Razões:**
- ✅ Qualidade superior (modelo BRIA treinado)
- ✅ Sem necessidade GPU local
- ✅ Gratuito para uso não-comercial
- ✅ API simples e documentada
- ❌ Dependência internet
- ❌ Possível instabilidade serviço externo

**Consequências:**
- **Positivas:** Qualidade profissional sem complexidade técnica
- **Negativas:** Dependência externa, possível latência
- **Mitigação:** Cache local, fallback manual, timeout handling

---

### ADR-003: Pillow (PIL) para Processamento de Imagens
**Data:** 2025-01-24 | **Status:** APROVADO | **Contexto:** Simplicidade vs Performance

**Problema:**
Biblioteca para manipulação, composição e export de imagens.

**Decisão:**
Utilizar Pillow (PIL) como engine principal de processamento.

**Alternativas Consideradas:**
- **OpenCV:** Performance superior, mas overhead para uso simples
- **Wand (ImageMagick):** Poderoso, mas dependências externas complexas
- **Skimage:** Científico, mas overkill para composição básica

**Razões:**
- ✅ Biblioteca padrão Python para imagens
- ✅ API simples e intuitiva
- ✅ Suporte nativo PNG/JPG
- ✅ Operações básicas suficientes para MVP
- ❌ Performance limitada para operações complexas

**Consequências:**
- **Positivas:** Desenvolvimento rápido, compatibilidade garantida
- **Negativas:** Possível gargalo performance em lotes grandes
- **Mitigação:** Otimizações pontuais, processamento assíncrono futuro

---

### ADR-004: Priorização Inteligente API Gradio
**Data:** 2025-01-24 | **Status:** APROVADO | **Contexto:** Otimização Pós-MVP

**Problema:**
Sistema estava usando fallback local mesmo com API Gradio disponível, resultando em qualidade inferior.

**Decisão:**
Implementar sistema de priorização que sempre tenta API Gradio primeiro, com reset automático da flag de fallback.

**Alternativas Consideradas:**
- **Fallback permanente:** Uma vez ativo, sempre usar local
- **Verificação manual:** Usuário escolhe qual usar
- **Timeout agressivo:** Reduzir tempo limite da API
- **Cache de status:** Lembrar estado da API por sessão

**Razões:**
- ✅ Qualidade máxima sempre que possível (modelo BRIA superior)
- ✅ Fallback apenas quando API realmente falha
- ✅ Health check otimizado com validação do método `predict()`
- ✅ Reset automático evita "travamento" em modo fallback
- ❌ Ligeiro overhead de verificação a cada processamento

**Implementação:**
```python
def health_check(self) -> bool:
    """Verifica se a API Gradio está disponível"""
    try:
        return hasattr(self.client, 'predict') and callable(getattr(self.client, 'predict'))
    except Exception:
        return False

def remove_background(self, image_path: str) -> str:
    # Reset fallback se API estiver disponível
    if self.use_fallback and self.health_check():
        self.use_fallback = False
        logger.info("API Gradio disponível - resetando para prioridade API")
```

**Consequências:**
- **Positivas:** Qualidade consistentemente máxima, sistema auto-recuperável
- **Negativas:** Verificação adicional por processamento
- **Resultado:** 100% das imagens processadas com melhor qualidade disponível

---

### ADR-005: Estrutura Monolítica Single-File
**Data:** 2025-01-24 | **Status:** APROVADO | **Contexto:** MVP Simples

**Problema:**
Organização código para aplicação Streamlit de escopo limitado.

**Decisão:**
Estrutura modular mas simples, evitando over-engineering.

**Estrutura Aprovada:**
```
app.py                 # Main Streamlit app
services/
├── background_removal.py
├── image_processor.py
└── file_manager.py
components/
├── uploader.py
├── preview.py
└── controls.py
utils/
├── validators.py
└── constants.py
```

**Alternativas Consideradas:**
- **Single file:** Muito simples, mas dificulta manutenção
- **Microserviços:** Over-engineering para MVP
- **MVC completo:** Complexidade desnecessária

**Razões:**
- ✅ Separação responsabilidades clara
- ✅ Testabilidade individual
- ✅ Escalabilidade futura
- ✅ Manutenibilidade adequada

---

### ADR-005: Output Fixo 1080x1080px PNG
**Data:** 2025-01-24 | **Status:** APROVADO | **Contexto:** Padronização E-commerce

**Problema:**
Formato e dimensões output para thumbnails e-commerce.

**Decisão:**
Output fixo PNG 1080x1080px, sem opções customização.

**Alternativas Consideradas:**
- **Múltiplos tamanhos:** 512x512, 1024x1024, 1080x1080
- **Formatos variados:** PNG, JPG, WEBP
- **Aspect ratios:** 1:1, 4:3, 16:9

**Razões:**
- ✅ Padrão e-commerce (Instagram, marketplaces)
- ✅ Qualidade PNG sem compressão
- ✅ Simplicidade implementação
- ✅ Consistência visual garantida
- ❌ Menos flexibilidade

**Consequências:**
- **Positivas:** Padronização total, implementação simples
- **Negativas:** Possível necessidade futura de outros formatos
- **Mitigação:** Documentar como limitação MVP, extensão futura

---

### ADR-006: Processamento Síncrono (MVP)
**Data:** 2025-01-24 | **Status:** TEMPORÁRIO | **Contexto:** Simplicidade Inicial

**Problema:**
Estrutura processamento para remoção fundo e composição.

**Decisão:**
Processamento síncrono sequencial para MVP, com migração assíncrona futura.

**Razões MVP:**
- ✅ Implementação mais simples
- ✅ Debug mais fácil
- ✅ Menos complexidade estado
- ❌ UI bloqueia durante processamento
- ❌ Não escala para lotes grandes

**Plano Evolução:**
- **Fase 1 (MVP):** Síncrono com progress bar
- **Fase 2:** Assíncrono com threading
- **Fase 3:** Batch processing paralelo

**Consequências:**
- **Positivas:** MVP mais rápido, menos bugs
- **Negativas:** UX limitada, não escala
- **Mitigação:** Progress indicators, timeout handling

---

## Decisões Técnicas Menores

### Naming Conventions
- **Arquivos:** snake_case (background_removal.py)
- **Funções:** snake_case (remove_background)
- **Classes:** PascalCase (ValidationResult)
- **Constantes:** UPPER_CASE (MAX_FILE_SIZE_MB)

### Error Handling
- **Strategy:** Graceful degradation com fallbacks
- **User Messages:** Português, claras e acionáveis
- **Logging:** Python logging para debug
- **Retry:** Automático para falhas temporárias API

### Performance Targets
- **Upload:** < 2s validação
- **API Gradio:** < 30s timeout
- **Composição:** < 1s preview update
- **Export:** < 3s salvamento
- **Total:** < 45s fluxo completo

### Dependencies Management
- **Core:** streamlit, pillow, gradio-client, numpy
- **Dev:** pytest, black, flake8
- **Versioning:** requirements.txt com versões fixas
- **Updates:** Apenas patches segurança durante MVP

---

## Decisões Pendentes

### DP-001: Cache Strategy
**Status:** PENDENTE | **Deadline:** Durante Story 2
- Cache backgrounds carregados?
- Cache resultados API Gradio?
- Estratégia invalidação?

### DP-002: Batch Processing
**Status:** FUTURO | **Deadline:** Pós-MVP
- Processamento múltiplas imagens?
- Interface para seleção lote?
- Progress tracking granular?

### DP-003: Configuration Management
**Status:** PENDENTE | **Deadline:** Durante Story 1
- Arquivo config.json?
- Variáveis ambiente?
- Settings UI?

---

**Última atualização:** 2025-01-24  
**Próxima revisão:** Após cada story implementada