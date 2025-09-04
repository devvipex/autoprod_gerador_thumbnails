#!/usr/bin/env python3
"""
Script de inicialização do Frontend Streamlit
Thumbnail Generator MVP
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import streamlit
        import PIL
        print("✅ Dependências verificadas com sucesso")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return False

def check_directories():
    """Verifica se os diretórios necessários existem"""
    base_path = Path(__file__).parent
    
    required_dirs = [
        base_path / "backgrounds",
        base_path / "thumbnails-prontas",
        base_path / "src"
    ]
    
    for dir_path in required_dirs:
        if not dir_path.exists():
            print(f"📁 Criando diretório: {dir_path}")
            dir_path.mkdir(exist_ok=True)
        else:
            print(f"✅ Diretório existe: {dir_path}")
    
    return True

def run_streamlit():
    """Executa o aplicativo Streamlit"""
    print("🚀 Iniciando Thumbnail Generator MVP...")
    print("🌐 O aplicativo será aberto no navegador")
    print("⏹️  Para parar: Ctrl+C")
    print("-" * 50)
    
    try:
        # Executar streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Aplicativo encerrado pelo usuário")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar Streamlit: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print("🎨 Thumbnail Generator MVP - Frontend Streamlit")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        return 1
    
    # Verificar diretórios
    if not check_directories():
        return 1
    
    # Executar aplicativo
    if not run_streamlit():
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)