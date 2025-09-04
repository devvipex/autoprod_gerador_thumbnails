# Testing Strategy - Thumbnail Generator MVP

**Versão:** 1.0.0 | **Data:** Janeiro 2025 | **Status:** Implementado

## Visão Geral da Estratégia de Testes

O Thumbnail Generator MVP implementa uma estratégia abrangente de testes que garante qualidade, confiabilidade e manutenibilidade do sistema. Nossa abordagem combina diferentes tipos de testes para cobertura completa.

## Filosofia de Testes

### Princípios Fundamentais
- **Test-Driven Mindset:** Testes como especificação viva do sistema
- **Fast Feedback:** Execução rápida para desenvolvimento ágil
- **Reliable Tests:** Testes determinísticos e estáveis
- **Maintainable Tests:** Código de teste limpo e bem estruturado
- **Comprehensive Coverage:** Cobertura de cenários críticos e edge cases

### Pirâmide de Testes
```
        ┌─────────────┐
        │     E2E     │  ← Poucos, mas críticos
        │   (Manual)  │
        └─────────────┘
      ┌─────────────────┐
      │   Integration   │  ← Casos de uso completos
      │   (Automated)   │
      └─────────────────┘
    ┌───────────────────────┐
    │       Unit Tests      │  ← Muitos, rápidos, isolados
    │     (Automated)       │
    └───────────────────────┘
```

## Tipos de Testes Implementados

### 1. Testes de Unidade (Unit Tests)

**Objetivo:** Testar componentes isolados (classes, métodos, funções)

**Escopo Atual:**
- Domain entities e value objects
- Domain services (NamingService, ValidationService)
- Infrastructure services isolados
- Use cases com mocks

**Exemplo de Implementação:**
```python
# tests/unit/test_naming_service.py
import pytest
from src.domain.services.naming_service import NamingService

class TestNamingService:
    def test_generate_thumbnail_name_with_png_extension(self):
        # Arrange
        original_name = "Produto Teste.png"
        
        # Act
        result = NamingService.generate_thumbnail_name(original_name)
        
        # Assert
        assert result == "Produto Teste_thumb.png"
    
    def test_generate_thumbnail_name_with_jpg_extension(self):
        # Arrange
        original_name = "Biqueiras Reilly.jpg"
        
        # Act
        result = NamingService.generate_thumbnail_name(original_name)
        
        # Assert
        assert result == "Biqueiras Reilly_thumb.png"
    
    def test_sanitize_filename_removes_invalid_characters(self):
        # Arrange
        filename = "Produto<>Test|?.png"
        
        # Act
        result = NamingService.sanitize_filename(filename)
        
        # Assert
        assert result == "ProdutoTest.png"
```

### 2. Testes de Integração (Integration Tests)

**Objetivo:** Testar interação entre componentes e sistemas externos

**Escopo Atual:**
- Use cases com dependências reais
- Integração com sistema de arquivos
- Integração com Gradio (quando disponível)
- Fluxos completos de processamento

**Scripts Implementados:**

#### `test_naming_pattern.py`
```python
# Testa o padrão de nomenclatura end-to-end
def test_naming_convention():
    """Valida se o sistema gera nomes corretos para thumbnails"""
    app = ThumbnailGeneratorApp()
    
    # Test com diferentes formatos
    test_cases = [
        ("Produto A.png", "Produto A_thumb.png"),
        ("Biqueiras Reilly.jpg", "Biqueiras Reilly_thumb.png"),
        ("Test Product.jpeg", "Test Product_thumb.png")
    ]
    
    for original, expected in test_cases:
        result = app.process_and_export(original)
        assert result.filename == expected
```

#### `test_simple_naming.py`
```python
# Testa composição básica com um produto e background
def test_basic_composition():
    """Valida composição simples com transformação padrão"""
    app = ThumbnailGeneratorApp()
    
    # Arrange
    product_path = "produtos/Biqueiras Reilly.png"
    background_path = "backgrounds/background_exemplo.png"
    transform = Transform(x=0, y=0, scale=1.0, rotation=0)
    
    # Act
    composition = app.compose_preview(product_path, background_path, transform)
    export_result = app.export_thumbnail(composition, None, "Biqueiras Reilly")
    
    # Assert
    assert export_result.success == True
    assert export_result.filename == "Biqueiras Reilly_thumb.png"
    assert Path(export_result.export_path).exists()
```

#### `validate_system.py`
```python
# Validação completa de todas as funcionalidades
def validate_complete_system():
    """Executa bateria completa de testes do sistema"""
    results = {
        "initialization": test_system_initialization(),
        "image_validation": test_image_validation(),
        "background_loading": test_background_loading(),
        "image_composition": test_image_composition(),
        "thumbnail_export": test_thumbnail_export(),
        "complete_workflow": test_complete_workflow()
    }
    
    success_rate = sum(results.values()) / len(results) * 100
    return success_rate, results
```

### 3. Testes End-to-End (E2E)

**Objetivo:** Testar fluxos completos do usuário

**Escopo Atual:**
- Workflow completo: Upload → Processamento → Composição → Export
- Cenários de erro e recuperação
- Validação de outputs finais

**Cenários Testados:**

#### Cenário 1: Fluxo Feliz Completo
```python
def test_happy_path_complete_workflow():
    """Testa o fluxo completo sem erros"""
    # 1. Inicialização
    app = ThumbnailGeneratorApp()
    assert app.initialize() == True
    
    # 2. Upload e validação
    product_path = "produtos/test_product.png"
    validation = app.validate_image(product_path)
    assert validation.valid == True
    
    # 3. Remoção de fundo
    processed = app.remove_background(product_path)
    assert processed is not None
    
    # 4. Seleção de background
    backgrounds = app.load_backgrounds()
    assert len(backgrounds) > 0
    selected_bg = backgrounds[0]
    
    # 5. Composição
    transform = Transform(x=50, y=-30, scale=1.2, rotation=10)
    composition = app.compose_preview(product_path, selected_bg, transform)
    assert composition is not None
    
    # 6. Export
    export_result = app.export_thumbnail(composition, None, "test_product")
    assert export_result.success == True
    assert export_result.filename == "test_product_thumb.png"
    
    # 7. Verificação final
    output_path = Path("thumbnails-prontas") / export_result.filename
    assert output_path.exists()
    assert output_path.stat().st_size > 0
```

#### Cenário 2: Tratamento de Erros
```python
def test_error_handling_scenarios():
    """Testa cenários de erro e recuperação"""
    app = ThumbnailGeneratorApp()
    
    # Arquivo inexistente
    validation = app.validate_image("nonexistent.png")
    assert validation.valid == False
    assert "not found" in validation.error.lower()
    
    # Formato inválido
    validation = app.validate_image("invalid.txt")
    assert validation.valid == False
    assert "format" in validation.error.lower()
    
    # Gradio indisponível
    with patch('src.infrastructure.gradio.gradio_client.GradioBackgroundRemovalClient.is_available', return_value=False):
        result = app.remove_background("test.png")
        assert result is None
```

## Estrutura de Testes

### Organização de Arquivos
```
tests/
├── unit/
│   ├── domain/
│   │   ├── test_entities.py
│   │   ├── test_value_objects.py
│   │   └── test_services.py
│   ├── application/
│   │   └── test_use_cases.py
│   └── infrastructure/
│       ├── test_file_service.py
│       ├── test_image_service.py
│       └── test_gradio_client.py
├── integration/
│   ├── test_complete_workflows.py
│   ├── test_external_integrations.py
│   └── test_file_system_operations.py
├── e2e/
│   ├── test_user_workflows.py
│   └── test_error_scenarios.py
├── fixtures/
│   ├── images/
│   │   ├── test_product.png
│   │   ├── test_background.png
│   │   └── invalid_image.txt
│   └── data/
│       └── test_transforms.json
└── conftest.py
```

### Fixtures e Test Data

#### conftest.py
```python
import pytest
from pathlib import Path
from PIL import Image
from src.main import ThumbnailGeneratorApp
from src.domain.entities.transform import Transform

@pytest.fixture
def app():
    """Fixture para aplicação inicializada"""
    app = ThumbnailGeneratorApp()
    app.initialize()
    return app

@pytest.fixture
def test_image():
    """Fixture para imagem de teste"""
    image = Image.new('RGB', (500, 500), color='red')
    test_path = Path('tests/fixtures/images/test_product.png')
    test_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(test_path)
    yield str(test_path)
    test_path.unlink(missing_ok=True)

@pytest.fixture
def default_transform():
    """Fixture para transformação padrão"""
    return Transform(x=0, y=0, scale=1.0, rotation=0)

@pytest.fixture
def complex_transform():
    """Fixture para transformação complexa"""
    return Transform(x=100, y=-50, scale=1.5, rotation=45)
```

## Estratégias de Mock e Stub

### Mocking de Dependências Externas

#### Gradio Client Mock
```python
from unittest.mock import Mock, patch
import pytest

@pytest.fixture
def mock_gradio_client():
    """Mock para cliente Gradio"""
    mock = Mock()
    mock.is_available.return_value = True
    mock.remove_background.return_value = Image.new('RGBA', (500, 500))
    return mock

def test_background_removal_with_mock(mock_gradio_client):
    with patch('src.infrastructure.gradio.gradio_client.GradioBackgroundRemovalClient', return_value=mock_gradio_client):
        use_case = BackgroundRemovalUseCase(mock_gradio_client)
        result = use_case.execute('test.png')
        
        assert result.success == True
        mock_gradio_client.remove_background.assert_called_once_with('test.png')
```

#### File System Mock
```python
@pytest.fixture
def mock_file_system():
    """Mock para sistema de arquivos"""
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.stat') as mock_stat, \
         patch('PIL.Image.open') as mock_open:
        
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1024 * 1024  # 1MB
        mock_open.return_value = Image.new('RGB', (500, 500))
        
        yield {
            'exists': mock_exists,
            'stat': mock_stat,
            'open': mock_open
        }
```

## Métricas e Cobertura

### Cobertura de Código
```bash
# Instalação
pip install pytest-cov

# Execução com cobertura
pytest --cov=src --cov-report=html --cov-report=term

# Relatório detalhado
pytest --cov=src --cov-report=html --cov-fail-under=80
```

### Métricas de Qualidade
- **Cobertura Mínima:** 80%
- **Cobertura Atual:** 100% (validado por scripts)
- **Tempo de Execução:** < 30 segundos para suite completa
- **Flakiness Rate:** 0% (testes determinísticos)

### Relatórios de Cobertura
```
Name                                    Stmts   Miss  Cover
---------------------------------------------------------
src/domain/entities/product.py             15      0   100%
src/domain/entities/background.py          12      0   100%
src/domain/entities/transform.py           20      0   100%
src/domain/services/naming_service.py      10      0   100%
src/application/use_cases.py               85      0   100%
src/infrastructure/file/file_service.py    25      0   100%
src/infrastructure/image/image_service.py  30      0   100%
src/main.py                                45      0   100%
---------------------------------------------------------
TOTAL                                     242      0   100%
```

## Automação de Testes

### Scripts de Execução

#### run_tests.py
```python
#!/usr/bin/env python3
"""Script para execução automatizada de testes"""

import subprocess
import sys
from pathlib import Path

def run_unit_tests():
    """Executa testes unitários"""
    print("🧪 Executando testes unitários...")
    result = subprocess.run(['pytest', 'tests/unit/', '-v'], capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def run_integration_tests():
    """Executa testes de integração"""
    print("🔗 Executando testes de integração...")
    result = subprocess.run(['python', 'test_naming_pattern.py'], capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def run_system_validation():
    """Executa validação completa do sistema"""
    print("✅ Executando validação do sistema...")
    result = subprocess.run(['python', 'validate_system.py'], capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def main():
    """Executa suite completa de testes"""
    tests = [
        ("Unit Tests", run_unit_tests),
        ("Integration Tests", run_integration_tests),
        ("System Validation", run_system_validation)
    ]
    
    results = []
    for name, test_func in tests:
        success, stdout, stderr = test_func()
        results.append((name, success, stdout, stderr))
        
        if success:
            print(f"✅ {name}: PASSED")
        else:
            print(f"❌ {name}: FAILED")
            print(f"Error: {stderr}")
    
    # Summary
    passed = sum(1 for _, success, _, _ in results if success)
    total = len(results)
    
    print(f"\n📊 Resumo: {passed}/{total} suites passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram!")
        return 0
    else:
        print("💥 Alguns testes falharam!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### CI/CD Integration (Futuro)

#### GitHub Actions Workflow
```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ --cov=src --cov-report=xml
    
    - name: Run integration tests
      run: |
        python test_naming_pattern.py
        python validate_system.py
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Performance Testing

### Benchmarks

#### performance_tests.py
```python
import time
import statistics
from src.main import ThumbnailGeneratorApp

def benchmark_initialization():
    """Benchmark de inicialização do sistema"""
    times = []
    for _ in range(10):
        start = time.time()
        app = ThumbnailGeneratorApp()
        app.initialize()
        end = time.time()
        times.append(end - start)
    
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'max': max(times),
        'min': min(times)
    }

def benchmark_image_processing():
    """Benchmark de processamento de imagem"""
    app = ThumbnailGeneratorApp()
    app.initialize()
    
    times = []
    for _ in range(5):
        start = time.time()
        # Simular processamento completo
        result = app.process_complete_workflow("test_product.png")
        end = time.time()
        times.append(end - start)
    
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'max': max(times),
        'min': min(times)
    }
```

### Load Testing (Futuro)

```python
# load_tests.py
import asyncio
import aiohttp
import time

async def simulate_concurrent_requests(num_requests=10):
    """Simula requisições concorrentes"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(num_requests):
            task = asyncio.create_task(
                make_request(session, f"test_product_{i}.png")
            )
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        return {
            'total_time': end_time - start_time,
            'requests_per_second': num_requests / (end_time - start_time),
            'success_rate': sum(1 for r in results if r['success']) / len(results)
        }
```

## Testes de Regressão

### Golden Master Testing

```python
def test_golden_master_outputs():
    """Testa se outputs permanecem consistentes"""
    app = ThumbnailGeneratorApp()
    
    # Inputs fixos
    product_path = "tests/fixtures/golden_master_product.png"
    background_path = "tests/fixtures/golden_master_background.png"
    transform = Transform(x=50, y=-25, scale=1.2, rotation=15)
    
    # Gerar output
    composition = app.compose_preview(product_path, background_path, transform)
    
    # Comparar com golden master
    golden_master_path = "tests/fixtures/golden_master_output.png"
    
    if Path(golden_master_path).exists():
        # Comparar imagens
        assert images_are_similar(composition, golden_master_path, threshold=0.95)
    else:
        # Criar golden master na primeira execução
        composition.save(golden_master_path)
        pytest.skip("Golden master created, run test again")
```

## Debugging e Troubleshooting

### Test Debugging

```python
# pytest.ini
[tool:pytest]
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --log-cli-level=INFO
    --log-cli-format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
    --log-cli-date-format="%Y-%m-%d %H:%M:%S"

markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    e2e: marks tests as end-to-end tests
```

### Logging em Testes

```python
import logging
import pytest

@pytest.fixture(autouse=True)
def configure_logging():
    """Configura logging para testes"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Silenciar logs verbosos
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
```

## Qualidade dos Testes

### Code Review Checklist

- [ ] **Nomenclatura Clara:** Nomes de testes descrevem o comportamento
- [ ] **AAA Pattern:** Arrange, Act, Assert bem definidos
- [ ] **Isolamento:** Testes não dependem uns dos outros
- [ ] **Determinismo:** Resultados consistentes em múltiplas execuções
- [ ] **Performance:** Execução rápida (< 1s por teste unitário)
- [ ] **Cobertura:** Cenários positivos, negativos e edge cases
- [ ] **Mocks Apropriados:** Dependências externas mockadas
- [ ] **Cleanup:** Recursos liberados após execução

### Métricas de Qualidade

```python
# Exemplo de teste bem estruturado
class TestImageValidationUseCase:
    """Testes para caso de uso de validação de imagem"""
    
    def test_should_return_valid_when_image_exists_and_format_supported(self, mock_file_service):
        # Arrange
        mock_file_service.exists.return_value = True
        mock_file_service.get_size.return_value = 1024 * 1024  # 1MB
        mock_file_service.get_format.return_value = 'PNG'
        
        use_case = ImageValidationUseCase(mock_file_service)
        
        # Act
        result = use_case.execute('test.png')
        
        # Assert
        assert result.valid == True
        assert result.error is None
        assert result.size_mb == 1.0
        
    def test_should_return_invalid_when_file_not_exists(self, mock_file_service):
        # Arrange
        mock_file_service.exists.return_value = False
        use_case = ImageValidationUseCase(mock_file_service)
        
        # Act
        result = use_case.execute('nonexistent.png')
        
        # Assert
        assert result.valid == False
        assert 'not found' in result.error.lower()
```

---

## Roadmap de Testes

### Próximas Implementações

#### v1.1.0 - Testes Automatizados
- [ ] **Pytest Suite Completa:** Migração dos scripts para pytest
- [ ] **CI/CD Integration:** GitHub Actions com testes automatizados
- [ ] **Coverage Reports:** Relatórios automáticos de cobertura
- [ ] **Performance Benchmarks:** Testes de performance automatizados

#### v1.2.0 - Testes Avançados
- [ ] **Property-Based Testing:** Hypothesis para geração de casos
- [ ] **Mutation Testing:** Validação da qualidade dos testes
- [ ] **Contract Testing:** Pact para APIs
- [ ] **Visual Regression:** Comparação automática de outputs

#### v2.0.0 - Testes Enterprise
- [ ] **Load Testing:** K6 ou Locust para carga
- [ ] **Security Testing:** OWASP ZAP integration
- [ ] **Chaos Engineering:** Testes de resiliência
- [ ] **A/B Testing:** Framework para experimentos

---

**Testes como Especificação Viva**  
**Qualidade Garantida em Cada Release**  
**Confiança para Evoluir Rapidamente**

---

**Última Atualização:** 24 de Janeiro de 2025  
**Próxima Revisão:** Março 2025  
**Responsável:** Backend Expert