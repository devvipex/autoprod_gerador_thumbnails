# Deployment Guide - Thumbnail Generator MVP

**Versão:** 1.0.0 | **Data:** Janeiro 2025 | **Status:** Implementado

## Visão Geral de Deployment

O Thumbnail Generator MVP foi projetado para deployment flexível, suportando desde desenvolvimento local até produção escalável. Este guia cobre todas as estratégias de deployment disponíveis.

## Arquitetura de Deployment

### Componentes do Sistema
```
┌─────────────────────────────────────────────────────────────┐
│                    Thumbnail Generator                      │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Streamlit)     │  Backend (Python)              │
│  ├─ UI Components         │  ├─ Application Layer          │
│  ├─ File Upload           │  ├─ Domain Logic               │
│  └─ Preview System        │  └─ Infrastructure Services    │
├─────────────────────────────────────────────────────────────┤
│                    External Dependencies                    │
│  ├─ Gradio API (Background Removal)                        │
│  ├─ File System (Local Storage)                            │
│  └─ Image Processing Libraries                              │
└─────────────────────────────────────────────────────────────┘
```

## Estratégias de Deployment

### 1. Desenvolvimento Local

**Objetivo:** Desenvolvimento e testes rápidos

#### Pré-requisitos
```bash
# Python 3.9+
python --version

# Dependências do sistema
pip install -r requirements.txt

# Estrutura de diretórios
mkdir -p produtos backgrounds thumbnails-prontas
```

#### Execução Local
```bash
# Método 1: Streamlit direto
streamlit run app.py

# Método 2: Script Python
python main.py

# Método 3: Modo desenvolvimento
python -m streamlit run app.py --server.runOnSave true
```

#### Configuração de Desenvolvimento
```python
# config/development.py
DEVELOPMENT_CONFIG = {
    'DEBUG': True,
    'LOG_LEVEL': 'DEBUG',
    'GRADIO_TIMEOUT': 30,
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB
    'ALLOWED_FORMATS': ['PNG', 'JPG', 'JPEG'],
    'CACHE_ENABLED': False,
    'AUTO_RELOAD': True
}
```

### 2. Containerização com Docker

**Objetivo:** Ambiente consistente e portável

#### Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p produtos backgrounds thumbnails-prontas

# Configurar usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando de inicialização
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  thumbnail-generator:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./produtos:/app/produtos
      - ./backgrounds:/app/backgrounds
      - ./thumbnails-prontas:/app/thumbnails-prontas
      - ./logs:/app/logs
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - GRADIO_TIMEOUT=60
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Opcional: Nginx para proxy reverso
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - thumbnail-generator
    restart: unless-stopped
```

#### Comandos Docker
```bash
# Build da imagem
docker build -t thumbnail-generator:latest .

# Executar container
docker run -p 8501:8501 \
  -v $(pwd)/produtos:/app/produtos \
  -v $(pwd)/backgrounds:/app/backgrounds \
  -v $(pwd)/thumbnails-prontas:/app/thumbnails-prontas \
  thumbnail-generator:latest

# Docker Compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### 3. Cloud Deployment

#### 3.1 Streamlit Cloud

**Configuração:**
```toml
# .streamlit/config.toml
[server]
port = 8501
address = "0.0.0.0"
runOnSave = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

**Secrets Management:**
```toml
# .streamlit/secrets.toml
[general]
GRADIO_API_URL = "https://api.gradio.app"
MAX_FILE_SIZE = 10485760
LOG_LEVEL = "INFO"

[storage]
BASE_PATH = "/app"
UPLOAD_PATH = "produtos"
BACKGROUND_PATH = "backgrounds"
OUTPUT_PATH = "thumbnails-prontas"
```

#### 3.2 Heroku Deployment

**Procfile:**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**runtime.txt:**
```
python-3.11.0
```

**Heroku Config:**
```bash
# Configurar variáveis de ambiente
heroku config:set ENVIRONMENT=production
heroku config:set LOG_LEVEL=INFO
heroku config:set GRADIO_TIMEOUT=60

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### 3.3 AWS Deployment

**ECS Task Definition:**
```json
{
  "family": "thumbnail-generator",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "thumbnail-generator",
      "image": "your-account.dkr.ecr.region.amazonaws.com/thumbnail-generator:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/thumbnail-generator",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**CloudFormation Template:**
```yaml
# cloudformation.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Thumbnail Generator Infrastructure'

Parameters:
  ImageUri:
    Type: String
    Description: 'ECR Image URI'

Resources:
  # VPC, Subnets, Security Groups
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true

  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: thumbnail-generator-cluster

  # ECS Service
  ECSService:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 2
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          SecurityGroups:
            - !Ref SecurityGroup
          Subnets:
            - !Ref PrivateSubnet1
            - !Ref PrivateSubnet2

  # Application Load Balancer
  LoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: thumbnail-generator-alb
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      SecurityGroups:
        - !Ref ALBSecurityGroup
```

## Configuração de Ambiente

### Variáveis de Ambiente

```bash
# .env
# Ambiente
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Aplicação
APP_NAME="Thumbnail Generator"
APP_VERSION="1.0.0"
MAX_FILE_SIZE=10485760
ALLOWED_FORMATS=PNG,JPG,JPEG

# Gradio
GRADIO_API_URL=https://api.gradio.app
GRADIO_TIMEOUT=60
GRADIO_RETRY_ATTEMPTS=3

# Paths
BASE_PATH=/app
UPLOAD_PATH=produtos
BACKGROUND_PATH=backgrounds
OUTPUT_PATH=thumbnails-prontas
LOG_PATH=logs

# Performance
CACHE_ENABLED=true
CACHE_TTL=3600
MAX_CONCURRENT_REQUESTS=10

# Monitoring
METRICS_ENABLED=true
HEALTH_CHECK_ENABLED=true
LOG_REQUESTS=true
```

### Configuração por Ambiente

```python
# config/settings.py
import os
from dataclasses import dataclass
from typing import List

@dataclass
class Settings:
    # Ambiente
    environment: str = os.getenv('ENVIRONMENT', 'development')
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Aplicação
    app_name: str = os.getenv('APP_NAME', 'Thumbnail Generator')
    app_version: str = os.getenv('APP_VERSION', '1.0.0')
    max_file_size: int = int(os.getenv('MAX_FILE_SIZE', 10485760))
    allowed_formats: List[str] = os.getenv('ALLOWED_FORMATS', 'PNG,JPG,JPEG').split(',')
    
    # Gradio
    gradio_api_url: str = os.getenv('GRADIO_API_URL', 'https://api.gradio.app')
    gradio_timeout: int = int(os.getenv('GRADIO_TIMEOUT', 60))
    gradio_retry_attempts: int = int(os.getenv('GRADIO_RETRY_ATTEMPTS', 3))
    
    # Paths
    base_path: str = os.getenv('BASE_PATH', '.')
    upload_path: str = os.getenv('UPLOAD_PATH', 'produtos')
    background_path: str = os.getenv('BACKGROUND_PATH', 'backgrounds')
    output_path: str = os.getenv('OUTPUT_PATH', 'thumbnails-prontas')
    log_path: str = os.getenv('LOG_PATH', 'logs')
    
    # Performance
    cache_enabled: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    cache_ttl: int = int(os.getenv('CACHE_TTL', 3600))
    max_concurrent_requests: int = int(os.getenv('MAX_CONCURRENT_REQUESTS', 10))
    
    # Monitoring
    metrics_enabled: bool = os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
    health_check_enabled: bool = os.getenv('HEALTH_CHECK_ENABLED', 'true').lower() == 'true'
    log_requests: bool = os.getenv('LOG_REQUESTS', 'true').lower() == 'true'

# Factory function
def get_settings() -> Settings:
    return Settings()
```

## Monitoramento e Observabilidade

### Health Checks

```python
# src/infrastructure/monitoring/health_check.py
from dataclasses import dataclass
from typing import Dict, Any
import time
import psutil
from pathlib import Path

@dataclass
class HealthStatus:
    status: str  # 'healthy', 'degraded', 'unhealthy'
    timestamp: float
    checks: Dict[str, Any]
    uptime: float

class HealthChecker:
    def __init__(self, app):
        self.app = app
        self.start_time = time.time()
    
    def check_health(self) -> HealthStatus:
        """Executa verificações de saúde do sistema"""
        checks = {
            'application': self._check_application(),
            'dependencies': self._check_dependencies(),
            'storage': self._check_storage(),
            'resources': self._check_resources()
        }
        
        # Determinar status geral
        if all(check['status'] == 'ok' for check in checks.values()):
            status = 'healthy'
        elif any(check['status'] == 'critical' for check in checks.values()):
            status = 'unhealthy'
        else:
            status = 'degraded'
        
        return HealthStatus(
            status=status,
            timestamp=time.time(),
            checks=checks,
            uptime=time.time() - self.start_time
        )
    
    def _check_application(self) -> Dict[str, Any]:
        """Verifica se a aplicação está funcionando"""
        try:
            # Testar inicialização básica
            test_result = self.app.initialize()
            return {
                'status': 'ok' if test_result else 'error',
                'message': 'Application initialized successfully' if test_result else 'Initialization failed'
            }
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Application error: {str(e)}'
            }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Verifica dependências externas"""
        try:
            # Verificar Gradio API
            gradio_available = self.app.gradio_client.is_available()
            return {
                'status': 'ok' if gradio_available else 'warning',
                'gradio_api': 'available' if gradio_available else 'unavailable',
                'message': 'All dependencies available' if gradio_available else 'Gradio API unavailable'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Dependency check failed: {str(e)}'
            }
    
    def _check_storage(self) -> Dict[str, Any]:
        """Verifica sistema de arquivos"""
        try:
            required_dirs = ['produtos', 'backgrounds', 'thumbnails-prontas']
            missing_dirs = []
            
            for dir_name in required_dirs:
                if not Path(dir_name).exists():
                    missing_dirs.append(dir_name)
            
            # Verificar espaço em disco
            disk_usage = psutil.disk_usage('.')
            free_space_gb = disk_usage.free / (1024**3)
            
            if missing_dirs:
                return {
                    'status': 'error',
                    'missing_directories': missing_dirs,
                    'free_space_gb': round(free_space_gb, 2)
                }
            elif free_space_gb < 1.0:  # Menos de 1GB livre
                return {
                    'status': 'warning',
                    'message': 'Low disk space',
                    'free_space_gb': round(free_space_gb, 2)
                }
            else:
                return {
                    'status': 'ok',
                    'message': 'Storage healthy',
                    'free_space_gb': round(free_space_gb, 2)
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Storage check failed: {str(e)}'
            }
    
    def _check_resources(self) -> Dict[str, Any]:
        """Verifica recursos do sistema"""
        try:
            # CPU e Memória
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            status = 'ok'
            warnings = []
            
            if cpu_percent > 80:
                status = 'warning'
                warnings.append('High CPU usage')
            
            if memory.percent > 80:
                status = 'warning'
                warnings.append('High memory usage')
            
            return {
                'status': status,
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'warnings': warnings
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Resource check failed: {str(e)}'
            }
```

### Logging

```python
# src/infrastructure/logging/logger.py
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class StructuredLogger:
    def __init__(self, name: str, log_level: str = 'INFO', log_path: str = 'logs'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Criar diretório de logs
        Path(log_path).mkdir(exist_ok=True)
        
        # Handler para arquivo
        file_handler = logging.FileHandler(f'{log_path}/app.log')
        file_handler.setFormatter(self._get_json_formatter())
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_console_formatter())
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _get_json_formatter(self):
        """Formatter para logs estruturados em JSON"""
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                # Adicionar contexto extra se disponível
                if hasattr(record, 'extra'):
                    log_entry.update(record.extra)
                
                return json.dumps(log_entry)
        
        return JsonFormatter()
    
    def _get_console_formatter(self):
        """Formatter para console legível"""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def log_request(self, method: str, path: str, duration: float, status: str):
        """Log estruturado para requisições"""
        self.logger.info(
            f"Request processed: {method} {path}",
            extra={
                'request_method': method,
                'request_path': path,
                'duration_ms': round(duration * 1000, 2),
                'status': status,
                'type': 'request'
            }
        )
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log estruturado para erros"""
        self.logger.error(
            f"Error occurred: {str(error)}",
            extra={
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context or {},
                'type': 'error'
            },
            exc_info=True
        )
```

### Métricas

```python
# src/infrastructure/monitoring/metrics.py
from dataclasses import dataclass, field
from typing import Dict, List
from collections import defaultdict, deque
import time
import threading

@dataclass
class Metrics:
    # Contadores
    requests_total: int = 0
    requests_success: int = 0
    requests_error: int = 0
    
    # Processamento
    images_processed: int = 0
    thumbnails_generated: int = 0
    backgrounds_loaded: int = 0
    
    # Performance
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    processing_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    # Recursos
    peak_memory_mb: float = 0.0
    peak_cpu_percent: float = 0.0
    
    # Erros por tipo
    errors_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

class MetricsCollector:
    def __init__(self):
        self.metrics = Metrics()
        self._lock = threading.Lock()
    
    def increment_requests(self, success: bool = True):
        """Incrementa contadores de requisições"""
        with self._lock:
            self.metrics.requests_total += 1
            if success:
                self.metrics.requests_success += 1
            else:
                self.metrics.requests_error += 1
    
    def record_response_time(self, duration: float):
        """Registra tempo de resposta"""
        with self._lock:
            self.metrics.response_times.append(duration)
    
    def record_processing_time(self, duration: float):
        """Registra tempo de processamento"""
        with self._lock:
            self.metrics.processing_times.append(duration)
    
    def increment_images_processed(self):
        """Incrementa contador de imagens processadas"""
        with self._lock:
            self.metrics.images_processed += 1
    
    def increment_thumbnails_generated(self):
        """Incrementa contador de thumbnails geradas"""
        with self._lock:
            self.metrics.thumbnails_generated += 1
    
    def record_error(self, error_type: str):
        """Registra erro por tipo"""
        with self._lock:
            self.metrics.errors_by_type[error_type] += 1
    
    def get_summary(self) -> Dict:
        """Retorna resumo das métricas"""
        with self._lock:
            response_times = list(self.metrics.response_times)
            processing_times = list(self.metrics.processing_times)
            
            return {
                'requests': {
                    'total': self.metrics.requests_total,
                    'success': self.metrics.requests_success,
                    'error': self.metrics.requests_error,
                    'success_rate': (self.metrics.requests_success / max(self.metrics.requests_total, 1)) * 100
                },
                'processing': {
                    'images_processed': self.metrics.images_processed,
                    'thumbnails_generated': self.metrics.thumbnails_generated,
                    'backgrounds_loaded': self.metrics.backgrounds_loaded
                },
                'performance': {
                    'avg_response_time_ms': sum(response_times) / len(response_times) * 1000 if response_times else 0,
                    'avg_processing_time_ms': sum(processing_times) / len(processing_times) * 1000 if processing_times else 0,
                    'peak_memory_mb': self.metrics.peak_memory_mb,
                    'peak_cpu_percent': self.metrics.peak_cpu_percent
                },
                'errors': dict(self.metrics.errors_by_type)
            }
```

## Segurança

### Configurações de Segurança

```python
# src/infrastructure/security/security_config.py
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SecurityConfig:
    # Upload restrictions
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = None
    allowed_mime_types: List[str] = None
    
    # Path restrictions
    allowed_upload_paths: List[str] = None
    blocked_file_patterns: List[str] = None
    
    # Rate limiting
    rate_limit_enabled: bool = True
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    
    # Headers de segurança
    security_headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = ['.png', '.jpg', '.jpeg']
        
        if self.allowed_mime_types is None:
            self.allowed_mime_types = ['image/png', 'image/jpeg']
        
        if self.allowed_upload_paths is None:
            self.allowed_upload_paths = ['produtos']
        
        if self.blocked_file_patterns is None:
            self.blocked_file_patterns = ['../', '.env', 'config']
        
        if self.security_headers is None:
            self.security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Content-Security-Policy': "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'"
            }

class SecurityValidator:
    def __init__(self, config: SecurityConfig):
        self.config = config
    
    def validate_file_upload(self, filename: str, file_size: int, mime_type: str) -> tuple[bool, str]:
        """Valida upload de arquivo"""
        # Verificar tamanho
        if file_size > self.config.max_file_size:
            return False, f"File size exceeds limit of {self.config.max_file_size} bytes"
        
        # Verificar extensão
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.config.allowed_extensions:
            return False, f"File extension {file_ext} not allowed"
        
        # Verificar MIME type
        if mime_type not in self.config.allowed_mime_types:
            return False, f"MIME type {mime_type} not allowed"
        
        # Verificar padrões bloqueados
        for pattern in self.config.blocked_file_patterns:
            if pattern in filename:
                return False, f"Filename contains blocked pattern: {pattern}"
        
        return True, "File validation passed"
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitiza nome do arquivo"""
        import re
        # Remove caracteres perigosos
        sanitized = re.sub(r'[^\w\s.-]', '', filename)
        # Remove múltiplos espaços
        sanitized = re.sub(r'\s+', ' ', sanitized)
        # Remove espaços no início e fim
        sanitized = sanitized.strip()
        return sanitized
```

## Backup e Recuperação

### Estratégia de Backup

```bash
#!/bin/bash
# scripts/backup.sh

set -e

# Configurações
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/app"
RETENTION_DAYS=30

# Criar diretório de backup
mkdir -p "$BACKUP_DIR"

# Backup de dados
echo "Starting backup at $(date)"

# Backup de produtos
tar -czf "$BACKUP_DIR/produtos_$DATE.tar.gz" -C "$APP_DIR" produtos/
echo "✅ Produtos backed up"

# Backup de backgrounds
tar -czf "$BACKUP_DIR/backgrounds_$DATE.tar.gz" -C "$APP_DIR" backgrounds/
echo "✅ Backgrounds backed up"

# Backup de thumbnails
tar -czf "$BACKUP_DIR/thumbnails_$DATE.tar.gz" -C "$APP_DIR" thumbnails-prontas/
echo "✅ Thumbnails backed up"

# Backup de configurações
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" -C "$APP_DIR" config/ .env
echo "✅ Configuration backed up"

# Backup de logs
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" -C "$APP_DIR" logs/
echo "✅ Logs backed up"

# Limpeza de backups antigos
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
echo "✅ Old backups cleaned up"

echo "Backup completed at $(date)"
```

### Script de Recuperação

```bash
#!/bin/bash
# scripts/restore.sh

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 <backup_date> <component>"
    echo "Components: produtos, backgrounds, thumbnails, config, logs, all"
    exit 1
fi

BACKUP_DATE=$1
COMPONENT=$2
BACKUP_DIR="/backups"
APP_DIR="/app"

restore_component() {
    local comp=$1
    local backup_file="$BACKUP_DIR/${comp}_${BACKUP_DATE}.tar.gz"
    
    if [ ! -f "$backup_file" ]; then
        echo "❌ Backup file not found: $backup_file"
        return 1
    fi
    
    echo "Restoring $comp from $backup_file"
    tar -xzf "$backup_file" -C "$APP_DIR"
    echo "✅ $comp restored"
}

case $COMPONENT in
    "produtos")
        restore_component "produtos"
        ;;
    "backgrounds")
        restore_component "backgrounds"
        ;;
    "thumbnails")
        restore_component "thumbnails"
        ;;
    "config")
        restore_component "config"
        ;;
    "logs")
        restore_component "logs"
        ;;
    "all")
        restore_component "produtos"
        restore_component "backgrounds"
        restore_component "thumbnails"
        restore_component "config"
        restore_component "logs"
        ;;
    *)
        echo "❌ Invalid component: $COMPONENT"
        exit 1
        ;;
esac

echo "Restore completed at $(date)"
```

## Troubleshooting

### Problemas Comuns

#### 1. Erro de Inicialização
```bash
# Verificar logs
docker logs thumbnail-generator

# Verificar health check
curl http://localhost:8501/_stcore/health

# Verificar variáveis de ambiente
docker exec thumbnail-generator env | grep -E "(ENVIRONMENT|LOG_LEVEL|GRADIO)"
```

#### 2. Problemas de Performance
```bash
# Monitorar recursos
docker stats thumbnail-generator

# Verificar métricas da aplicação
curl http://localhost:8501/metrics

# Analisar logs de performance
grep "duration_ms" logs/app.log | tail -100
```

#### 3. Erros de Gradio
```bash
# Testar conectividade
curl -I https://api.gradio.app

# Verificar timeout
grep "gradio_timeout" logs/app.log

# Modo fallback
export GRADIO_FALLBACK_ENABLED=true
```

### Scripts de Diagnóstico

```bash
#!/bin/bash
# scripts/diagnose.sh

echo "🔍 Thumbnail Generator Diagnostics"
echo "================================="

# Verificar container
echo "📦 Container Status:"
docker ps | grep thumbnail-generator

# Verificar saúde
echo "\n❤️ Health Check:"
curl -s http://localhost:8501/_stcore/health | jq .

# Verificar recursos
echo "\n💻 Resource Usage:"
docker stats --no-stream thumbnail-generator

# Verificar logs recentes
echo "\n📋 Recent Logs:"
docker logs --tail 20 thumbnail-generator

# Verificar diretórios
echo "\n📁 Directory Structure:"
docker exec thumbnail-generator ls -la

# Verificar conectividade
echo "\n🌐 Network Connectivity:"
docker exec thumbnail-generator curl -I https://api.gradio.app

echo "\n✅ Diagnostics completed"
```

---

## Roadmap de Deployment

### Próximas Implementações

#### v1.1.0 - Melhorias de Produção
- [ ] **CI/CD Pipeline:** GitHub Actions para deploy automatizado
- [ ] **Monitoring Avançado:** Prometheus + Grafana
- [ ] **Load Balancing:** Nginx com múltiplas instâncias
- [ ] **SSL/TLS:** Certificados automáticos com Let's Encrypt

#### v1.2.0 - Escalabilidade
- [ ] **Kubernetes:** Deployment em cluster K8s
- [ ] **Auto-scaling:** HPA baseado em CPU/memória
- [ ] **Service Mesh:** Istio para comunicação segura
- [ ] **Distributed Storage:** S3/MinIO para arquivos

#### v2.0.0 - Enterprise
- [ ] **Multi-tenancy:** Isolamento por cliente
- [ ] **API Gateway:** Kong/Ambassador
- [ ] **Disaster Recovery:** Backup automático e failover
- [ ] **Compliance:** SOC2, GDPR, LGPD

---

**Deploy com Confiança**  
**Monitoramento Contínuo**  
**Escalabilidade Garantida**

---

**Última Atualização:** 24 de Janeiro de 2025  
**Próxima Revisão:** Março 2025  
**Responsável:** Backend Expert