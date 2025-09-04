#!/usr/bin/env python3
"""Teste direto de geração de thumbnails sem API Gradio"""

import sys
from pathlib import Path
from PIL import Image

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import ThumbnailGeneratorApp
from src.domain.entities import Transform

def test_direct_thumbnail_generation():
    """Testa geração direta de thumbnails usando imagens existentes"""
    print("🎨 Teste Direto de Geração de Thumbnails")
    print("=" * 50)
    
    app = ThumbnailGeneratorApp()
    app.initialize()
    
    # Verificar imagens disponíveis
    produtos_dir = Path("produtos-sem-fundo")
    backgrounds_dir = Path("backgrounds")
    
    if not produtos_dir.exists():
        print("❌ Pasta produtos-sem-fundo não encontrada")
        return
    
    if not backgrounds_dir.exists():
        print("❌ Pasta backgrounds não encontrada")
        return
    
    # Listar produtos disponíveis
    produtos = list(produtos_dir.glob("*.png"))
    backgrounds = list(backgrounds_dir.glob("*.png"))
    
    print(f"📦 Produtos encontrados: {len(produtos)}")
    for produto in produtos:
        print(f"  - {produto.name}")
    
    print(f"🖼️ Backgrounds encontrados: {len(backgrounds)}")
    for bg in backgrounds:
        print(f"  - {bg.name}")
    
    if not produtos or not backgrounds:
        print("❌ Não há produtos ou backgrounds suficientes para teste")
        return
    
    # Gerar thumbnails para cada produto
    thumbnails_geradas = 0
    
    for i, produto in enumerate(produtos[:3]):  # Limitar a 3 produtos
        for j, background in enumerate(backgrounds[:2]):  # Limitar a 2 backgrounds
            print(f"\n🔄 Gerando thumbnail {thumbnails_geradas + 1}...")
            print(f"   Produto: {produto.name}")
            print(f"   Background: {background.name}")
            
            # Criar transformação variada
            transform = Transform(
                x=(-50 + i * 25),  # Variar posição X
                y=(-30 + j * 20),  # Variar posição Y
                scale=(0.8 + i * 0.1),  # Variar escala
                rotation=(i * 5 - j * 3)  # Variar rotação
            )
            
            # Compor preview
            composition = app.compose_preview(
                str(produto), 
                str(background), 
                transform
            )
            
            if composition:
                # Exportar thumbnail
                filename = f"{produto.stem}_{background.stem}_{i}_{j}"
                output_path = app.export_thumbnail(composition, filename)
                
                if output_path:
                    print(f"   ✅ Salva em: {output_path}")
                    
                    # Verificar arquivo
                    if Path(output_path).exists():
                        file_size = Path(output_path).stat().st_size / 1024
                        print(f"   📊 Tamanho: {file_size:.1f} KB")
                        
                        # Verificar dimensões
                        with Image.open(output_path) as img:
                            print(f"   📐 Dimensões: {img.size[0]}x{img.size[1]}px")
                    
                    thumbnails_geradas += 1
                else:
                    print(f"   ❌ Erro ao salvar thumbnail")
            else:
                print(f"   ❌ Erro na composição")
    
    print(f"\n🎉 Processo concluído!")
    print(f"📈 Thumbnails geradas: {thumbnails_geradas}")
    print(f"📁 Verifique a pasta: thumbnails-prontas/")
    
    # Listar arquivos gerados
    thumbnails_dir = Path("thumbnails-prontas")
    if thumbnails_dir.exists():
        arquivos = list(thumbnails_dir.glob("*.png"))
        print(f"\n📋 Arquivos na pasta thumbnails-prontas: {len(arquivos)}")
        for arquivo in arquivos:
            file_size = arquivo.stat().st_size / 1024
            print(f"  - {arquivo.name} ({file_size:.1f} KB)")

if __name__ == "__main__":
    test_direct_thumbnail_generation()