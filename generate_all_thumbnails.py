#!/usr/bin/env python3
"""Script para gerar thumbnails de todos os produtos disponíveis"""

import sys
from pathlib import Path
from PIL import Image

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import ThumbnailGeneratorApp
from src.domain.entities import Transform

def generate_all_thumbnails():
    """Gera thumbnails para todos os produtos disponíveis"""
    print("🎨 Gerador de Thumbnails - Processamento Completo")
    print("=" * 60)
    
    app = ThumbnailGeneratorApp()
    app.initialize()
    
    # Verificar diretórios
    produtos_dir = Path("produtos-sem-fundo")
    backgrounds_dir = Path("backgrounds")
    
    if not produtos_dir.exists():
        print("❌ Pasta produtos-sem-fundo não encontrada")
        return
    
    if not backgrounds_dir.exists():
        print("❌ Pasta backgrounds não encontrada")
        return
    
    # Listar todos os arquivos
    produtos = list(produtos_dir.glob("*.png"))
    backgrounds = list(backgrounds_dir.glob("*.png"))
    
    print(f"📦 Produtos encontrados: {len(produtos)}")
    print(f"🖼️ Backgrounds encontrados: {len(backgrounds)}")
    print(f"🎯 Total de combinações possíveis: {len(produtos) * len(backgrounds)}")
    print()
    
    if not produtos or not backgrounds:
        print("❌ Não há produtos ou backgrounds suficientes")
        return
    
    # Configurações de transformação para variedade
    transforms_configs = [
        Transform(x=0, y=0, scale=0.8, rotation=0),      # Padrão centrado
        Transform(x=0, y=-50, scale=0.9, rotation=0),    # Ligeiramente acima
        Transform(x=0, y=0, scale=1.0, rotation=0),      # Tamanho original
        Transform(x=0, y=30, scale=0.85, rotation=0),    # Ligeiramente abaixo
    ]
    
    thumbnails_geradas = 0
    erros = 0
    
    # Processar cada produto com cada background
    for i, produto in enumerate(produtos):
        print(f"\n📦 Processando produto {i+1}/{len(produtos)}: {produto.name}")
        
        for j, background in enumerate(backgrounds):
            print(f"  🖼️ Background {j+1}/{len(backgrounds)}: {background.name}")
            
            # Usar diferentes configurações de transformação
            transform_idx = (i + j) % len(transforms_configs)
            transform = transforms_configs[transform_idx]
            
            try:
                # Compor preview
                composition = app.compose_preview(
                    str(produto), 
                    str(background), 
                    transform
                )
                
                if composition:
                    # Gerar nome único e descritivo
                    produto_clean = produto.stem.replace(" ", "_")
                    background_clean = background.stem.replace(" ", "_")
                    filename = f"{produto_clean}_com_{background_clean}"
                    
                    # Exportar thumbnail
                    output_path = app.export_thumbnail(composition, filename)
                    
                    if output_path and Path(output_path).exists():
                        file_size = Path(output_path).stat().st_size / 1024
                        print(f"    ✅ Salva: {Path(output_path).name} ({file_size:.1f} KB)")
                        thumbnails_geradas += 1
                    else:
                        print(f"    ❌ Erro ao salvar")
                        erros += 1
                else:
                    print(f"    ❌ Erro na composição")
                    erros += 1
                    
            except Exception as e:
                print(f"    ❌ Erro: {str(e)[:50]}...")
                erros += 1
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    print(f"✅ Thumbnails geradas com sucesso: {thumbnails_geradas}")
    print(f"❌ Erros encontrados: {erros}")
    print(f"📈 Taxa de sucesso: {(thumbnails_geradas/(thumbnails_geradas+erros)*100):.1f}%")
    
    # Listar todos os arquivos gerados
    thumbnails_dir = Path("thumbnails-prontas")
    if thumbnails_dir.exists():
        arquivos = list(thumbnails_dir.glob("*.png"))
        total_size = sum(arquivo.stat().st_size for arquivo in arquivos) / (1024 * 1024)
        
        print(f"\n📁 Pasta thumbnails-prontas:")
        print(f"   📄 Total de arquivos: {len(arquivos)}")
        print(f"   💾 Tamanho total: {total_size:.2f} MB")
        print(f"   📐 Todas as thumbnails são 1080x1080px")
        
        print(f"\n📋 Arquivos gerados:")
        for arquivo in sorted(arquivos):
            file_size = arquivo.stat().st_size / 1024
            print(f"   - {arquivo.name} ({file_size:.1f} KB)")
    
    print(f"\n🎉 Processamento concluído!")
    print(f"💡 As thumbnails estão prontas para uso em e-commerce")

if __name__ == "__main__":
    generate_all_thumbnails()