#!/usr/bin/env python3
"""Exemplo de uso do Thumbnail Generator MVP"""

import sys
import logging
from pathlib import Path
from PIL import Image

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import ThumbnailGeneratorApp
from src.domain.entities import Transform
from src.config import load_config


def setup_logging():
    """Configura logging para o exemplo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_sample_images():
    """Cria imagens de exemplo para teste"""
    print("Criando imagens de exemplo...")
    
    # Garantir que diretórios existem
    Path("produtos-sem-fundo").mkdir(exist_ok=True)
    Path("backgrounds").mkdir(exist_ok=True)
    
    # Criar produto de exemplo (com transparência)
    product = Image.new('RGBA', (400, 400), color=(0, 0, 0, 0))
    # Desenhar um círculo vermelho no centro
    from PIL import ImageDraw
    draw = ImageDraw.Draw(product)
    draw.ellipse([100, 100, 300, 300], fill=(255, 0, 0, 255))
    product.save("produtos-sem-fundo/produto_exemplo.png")
    print("  ✓ Produto de exemplo criado: produtos-sem-fundo/produto_exemplo.png")
    
    # Criar background de exemplo
    background = Image.new('RGB', (1080, 1080), color=(100, 150, 200))
    # Adicionar gradiente simples
    for y in range(1080):
        for x in range(1080):
            r = int(100 + (x / 1080) * 50)
            g = int(150 + (y / 1080) * 50)
            b = 200
            background.putpixel((x, y), (r, g, b))
    background.save("backgrounds/background_exemplo.png")
    print("  ✓ Background de exemplo criado: backgrounds/background_exemplo.png")


def example_basic_usage():
    """Exemplo básico de uso da aplicação"""
    print("\n=== Exemplo Básico de Uso ===")
    
    # Inicializar aplicação
    app = ThumbnailGeneratorApp()
    
    if not app.initialize():
        print("❌ Erro na inicialização da aplicação")
        return False
    
    print("✓ Aplicação inicializada com sucesso")
    
    # Verificar status
    status = app.get_status()
    print(f"Status: {status['current_step']}")
    print(f"API Gradio disponível: {status['gradio_available']}")
    print(f"Backgrounds encontrados: {status['backgrounds_count']}")
    
    return True


def example_image_validation():
    """Exemplo de validação de imagem"""
    print("\n=== Exemplo: Validação de Imagem ===")
    
    app = ThumbnailGeneratorApp()
    app.initialize()
    
    # Testar com imagem válida
    if Path("produtos-sem-fundo/produto_exemplo.png").exists():
        is_valid = app.validate_image("produtos-sem-fundo/produto_exemplo.png")
        print(f"Validação do produto exemplo: {'✓ Válida' if is_valid else '❌ Inválida'}")
    
    # Testar com arquivo inexistente
    is_valid = app.validate_image("arquivo_inexistente.png")
    print(f"Validação de arquivo inexistente: {'✓ Válida' if is_valid else '❌ Inválida (esperado)'}")


def example_background_loading():
    """Exemplo de carregamento de backgrounds"""
    print("\n=== Exemplo: Carregamento de Backgrounds ===")
    
    app = ThumbnailGeneratorApp()
    app.initialize()
    
    backgrounds = app.load_backgrounds()
    print(f"Backgrounds encontrados: {len(backgrounds)}")
    
    for i, bg in enumerate(backgrounds[:3], 1):
        print(f"  {i}. {Path(bg).name}")
    
    if len(backgrounds) > 3:
        print(f"  ... e mais {len(backgrounds) - 3} backgrounds")


def example_composition():
    """Exemplo de composição de imagem"""
    print("\n=== Exemplo: Composição de Imagem ===")
    
    app = ThumbnailGeneratorApp()
    app.initialize()
    
    product_path = "produtos-sem-fundo/produto_exemplo.png"
    background_path = "backgrounds/background_exemplo.png"
    
    if not Path(product_path).exists() or not Path(background_path).exists():
        print("❌ Imagens de exemplo não encontradas. Execute create_sample_images() primeiro.")
        return
    
    # Criar transformação personalizada
    transform = Transform(
        x=50,      # Deslocar 50px para direita
        y=-30,     # Deslocar 30px para cima
        scale=1.2, # Aumentar 20%
        rotation=5 # Rotacionar 5 graus
    )
    
    print(f"Compondo: {Path(product_path).name} + {Path(background_path).name}")
    print(f"Transform: x={transform.x}, y={transform.y}, scale={transform.scale}, rotation={transform.rotation}°")
    
    composition = app.compose_preview(product_path, background_path, transform)
    
    if composition:
        print("✓ Composição criada com sucesso")
        print(f"  Tamanho: {composition.size}")
        print(f"  Modo: {composition.mode}")
        return composition
    else:
        print("❌ Erro na composição")
        return None


def example_export():
    """Exemplo de exportação de thumbnail"""
    print("\n=== Exemplo: Exportação de Thumbnail ===")
    
    app = ThumbnailGeneratorApp()
    app.initialize()
    
    # Primeiro, criar uma composição
    composition = example_composition()
    
    if not composition:
        print("❌ Não foi possível criar composição para exportar")
        return
    
    # Exportar com nome personalizado
    output_path = app.export_thumbnail(composition, "exemplo_personalizado")
    
    if output_path:
        print(f"✓ Thumbnail exportada: {output_path}")
        
        # Verificar arquivo criado
        if Path(output_path).exists():
            file_size = Path(output_path).stat().st_size
            print(f"  Tamanho do arquivo: {file_size / 1024:.1f} KB")
        
        return output_path
    else:
        print("❌ Erro na exportação")
        return None


def example_complete_workflow():
    """Exemplo de workflow completo"""
    print("\n=== Exemplo: Workflow Completo ===")
    
    app = ThumbnailGeneratorApp()
    app.initialize()
    
    product_path = "produtos-sem-fundo/produto_exemplo.png"
    background_path = "backgrounds/background_exemplo.png"
    
    if not Path(product_path).exists() or not Path(background_path).exists():
        print("❌ Imagens de exemplo não encontradas")
        return
    
    # Transformação personalizada
    transform = Transform(x=0, y=0, scale=0.8, rotation=0)
    
    print("Executando workflow completo...")
    print(f"  Produto: {Path(product_path).name}")
    print(f"  Background: {Path(background_path).name}")
    
    # NOTA: Este exemplo pula a remoção de fundo via Gradio
    # pois requer conexão com a API externa
    
    final_path = app.process_complete_workflow(
        image_path=product_path,
        background_path=background_path,
        transform=transform,
        output_filename="workflow_completo"
    )
    
    if final_path:
        print(f"✓ Workflow completo finalizado: {final_path}")
    else:
        print("❌ Erro no workflow (provavelmente na API Gradio)")
        print("💡 Para testar remoção de fundo, certifique-se que a API Gradio está disponível")


def main():
    """Função principal do exemplo"""
    print("🎨 Thumbnail Generator MVP - Exemplos de Uso")
    print("=" * 50)
    
    setup_logging()
    
    try:
        # Carregar configuração
        config = load_config()
        print(f"✓ Configuração carregada (versão {config.version})")
        
        # Criar imagens de exemplo se não existirem
        if not Path("produtos-sem-fundo/produto_exemplo.png").exists():
            create_sample_images()
        
        # Executar exemplos
        example_basic_usage()
        example_image_validation()
        example_background_loading()
        example_composition()
        example_export()
        example_complete_workflow()
        
        print("\n" + "=" * 50)
        print("✅ Todos os exemplos executados!")
        print("\n💡 Dicas:")
        print("  - Verifique a pasta 'thumbnails-prontas/' para ver os resultados")
        print("  - Para usar a API Gradio, certifique-se que está disponível")
        print("  - Personalize as transformações no código para diferentes efeitos")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        logging.exception("Erro detalhado:")


if __name__ == "__main__":
    main()