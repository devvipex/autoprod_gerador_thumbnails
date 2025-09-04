#!/usr/bin/env python3
"""
Script simples para testar o padrão de nomenclatura: nome_original_thumb.png
"""

import os
import sys
from pathlib import Path

# Configurar path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import ThumbnailGeneratorApp
from src.domain.entities import Transform

def test_naming_simple():
    """Teste simples de nomenclatura"""
    print("=== TESTE SIMPLES DE NOMENCLATURA ===")
    
    app = ThumbnailGeneratorApp()
    if not app.initialize():
        print("ERRO: Falha na inicializacao")
        return False
    
    # Verificar produtos
    produtos_dir = "produtos-sem-fundo"
    produtos = [f for f in os.listdir(produtos_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Produtos encontrados: {len(produtos)}")
    
    # Verificar backgrounds
    backgrounds_dir = "backgrounds"
    backgrounds = [f for f in os.listdir(backgrounds_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Backgrounds encontrados: {len(backgrounds)}")
    
    if not produtos or not backgrounds:
        print("ERRO: Produtos ou backgrounds insuficientes")
        return False
    
    # Testar com primeiro produto e primeiro background
    produto = produtos[0]
    background = backgrounds[0]
    
    produto_path = os.path.join(produtos_dir, produto)
    background_path = os.path.join(backgrounds_dir, background)
    
    print(f"\nTestando:")
    print(f"  Produto: {produto}")
    print(f"  Background: {background}")
    
    try:
        # Criar composição
        transform = Transform(x=0, y=0, scale=0.8, rotation=0)
        composition = app.compose_preview(produto_path, background_path, transform)
        
        if not composition:
            print("ERRO: Falha na composicao")
            return False
        
        print("  Composicao: OK")
        
        # Testar exportação com nomenclatura
        original_name = Path(produto).name
        result_path = app.export_thumbnail(composition, None, original_name)
        
        if not result_path:
            print("ERRO: Falha na exportacao")
            return False
        
        # Verificar nomenclatura
        expected_name = f"{Path(produto).stem}_thumb.png"
        actual_name = Path(result_path).name
        
        print(f"  Esperado: {expected_name}")
        print(f"  Gerado: {actual_name}")
        
        if actual_name == expected_name:
            print("  SUCESSO: Nomenclatura correta!")
            
            # Verificar arquivo
            if os.path.exists(result_path):
                size_kb = os.path.getsize(result_path) / 1024
                print(f"  Arquivo: {size_kb:.1f} KB")
                return True
            else:
                print("ERRO: Arquivo nao foi criado")
                return False
        else:
            print("ERRO: Nomenclatura incorreta")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def list_thumbnails():
    """Lista thumbnails geradas"""
    print("\n=== THUMBNAILS GERADAS ===")
    
    thumbnails_dir = "thumbnails-prontas"
    if not os.path.exists(thumbnails_dir):
        print("Pasta thumbnails-prontas nao existe")
        return
    
    files = [f for f in os.listdir(thumbnails_dir) if f.lower().endswith('.png')]
    
    if not files:
        print("Nenhuma thumbnail encontrada")
        return
    
    print(f"Total: {len(files)} thumbnails")
    
    for file in sorted(files):
        file_path = os.path.join(thumbnails_dir, file)
        size_kb = os.path.getsize(file_path) / 1024
        
        # Verificar padrão
        follows_pattern = file.endswith('_thumb.png')
        status = "OK" if follows_pattern else "ERRO"
        
        print(f"  {status}: {file} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    print("Testando padrao de nomenclatura...")
    
    try:
        success = test_naming_simple()
        list_thumbnails()
        
        if success:
            print("\nSUCESSO: Teste passou!")
        else:
            print("\nFALHA: Teste falhou!")
            
    except Exception as e:
        print(f"ERRO GERAL: {e}")
        sys.exit(1)