#!/usr/bin/env python3
"""
Script para testar o novo padrão de nomenclatura: nome_original_thumb.png
E validar todas as funcionalidades do sistema
"""

import os
import sys
import logging
from pathlib import Path
from PIL import Image

# Adicionar src ao path e configurar imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar usando caminho absoluto
from src.main import ThumbnailGeneratorApp
from src.domain.entities import Transform

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_naming_pattern():
    """Testa o padrão de nomenclatura nome_original_thumb.png"""
    logger.info("=== TESTE DO PADRÃO DE NOMENCLATURA ===")
    
    app = ThumbnailGeneratorApp()
    if not app.initialize():
        logger.error("Falha na inicialização da aplicação")
        return False
    
    # Listar produtos disponíveis
    produtos_dir = "produtos-sem-fundo"
    if not os.path.exists(produtos_dir):
        logger.error(f"Diretório {produtos_dir} não encontrado")
        return False
    
    produtos = [f for f in os.listdir(produtos_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    logger.info(f"Produtos encontrados: {len(produtos)}")
    
    # Listar backgrounds disponíveis
    backgrounds = app.load_backgrounds()
    logger.info(f"Backgrounds encontrados: {len(backgrounds)}")
    
    if not produtos or not backgrounds:
        logger.error("Não há produtos ou backgrounds suficientes para teste")
        return False
    
    success_count = 0
    total_tests = 0
    
    # Testar com cada produto
    for produto in produtos[:2]:  # Limitar a 2 produtos para teste
        produto_path = os.path.join(produtos_dir, produto)
        logger.info(f"\nTestando produto: {produto}")
        
        for background in backgrounds[:1]:  # 1 background por produto
            total_tests += 1
            logger.info(f"  Background: {background}")
            
            try:
                # Criar composição
                transform = Transform(x=0, y=0, scale=0.8, rotation=0)
                composition = app.compose_preview(produto_path, background, transform)
                
                if composition:
                    # Exportar com nomenclatura automática
                    original_name = Path(produto).name
                    result_path = app.export_thumbnail(composition, None, original_name)
                    
                    if result_path:
                        expected_name = f"{Path(produto).stem}_thumb.png"
                        actual_name = Path(result_path).name
                        
                        logger.info(f"    Esperado: {expected_name}")
                        logger.info(f"    Gerado: {actual_name}")
                        
                        if actual_name == expected_name:
                            logger.info("    ✅ Nomenclatura CORRETA")
                            success_count += 1
                        else:
                            logger.error("    ❌ Nomenclatura INCORRETA")
                    else:
                        logger.error("    ❌ Falha na exportação")
                else:
                    logger.error("    ❌ Falha na composição")
                    
            except Exception as e:
                logger.error(f"    ❌ Erro: {e}")
    
    logger.info(f"\n=== RESULTADO DO TESTE ===")
    logger.info(f"Sucessos: {success_count}/{total_tests}")
    logger.info(f"Taxa de sucesso: {(success_count/total_tests)*100:.1f}%")
    
    return success_count == total_tests

def test_all_functionalities():
    """Testa todas as funcionalidades do sistema"""
    logger.info("\n=== TESTE DE TODAS AS FUNCIONALIDADES ===")
    
    app = ThumbnailGeneratorApp()
    if not app.initialize():
        logger.error("Falha na inicialização")
        return False
    
    # 1. Teste de validação de imagem
    logger.info("\n1. Testando validação de imagem...")
    test_image = "produtos-sem-fundo/Biqueiras Reilly.png"
    if os.path.exists(test_image):
        if app.validate_image(test_image):
            logger.info("   ✅ Validação de imagem OK")
        else:
            logger.error("   ❌ Falha na validação")
            return False
    else:
        logger.warning("   ⚠️  Imagem de teste não encontrada")
    
    # 2. Teste de carregamento de backgrounds
    logger.info("\n2. Testando carregamento de backgrounds...")
    backgrounds = app.load_backgrounds()
    if backgrounds:
        logger.info(f"   ✅ {len(backgrounds)} backgrounds carregados")
        for bg in backgrounds:
            logger.info(f"      - {bg}")
    else:
        logger.error("   ❌ Nenhum background encontrado")
        return False
    
    # 3. Teste de composição
    logger.info("\n3. Testando composição de imagem...")
    if os.path.exists(test_image) and backgrounds:
        transform = Transform(x=50, y=50, scale=0.7, rotation=15)
        composition = app.compose_preview(test_image, backgrounds[0], transform)
        if composition:
            logger.info("   ✅ Composição OK")
            logger.info(f"      Tamanho: {composition.size}")
            logger.info(f"      Modo: {composition.mode}")
        else:
            logger.error("   ❌ Falha na composição")
            return False
    
    # 4. Teste de exportação
    logger.info("\n4. Testando exportação...")
    if 'composition' in locals():
        original_name = Path(test_image).name
        export_path = app.export_thumbnail(composition, None, original_name)
        if export_path and os.path.exists(export_path):
            file_size = os.path.getsize(export_path) / 1024  # KB
            logger.info(f"   ✅ Exportação OK: {export_path}")
            logger.info(f"      Tamanho: {file_size:.1f} KB")
        else:
            logger.error("   ❌ Falha na exportação")
            return False
    
    # 5. Teste de status
    logger.info("\n5. Testando status da aplicação...")
    status = app.get_status()
    logger.info("   ✅ Status obtido:")
    for key, value in status.items():
        logger.info(f"      {key}: {value}")
    
    logger.info("\n=== TODAS AS FUNCIONALIDADES TESTADAS COM SUCESSO! ===")
    return True

def list_generated_thumbnails():
    """Lista todas as thumbnails geradas"""
    logger.info("\n=== THUMBNAILS GERADAS ===")
    
    thumbnails_dir = "thumbnails-prontas"
    if not os.path.exists(thumbnails_dir):
        logger.info("Nenhuma thumbnail encontrada")
        return
    
    files = os.listdir(thumbnails_dir)
    png_files = [f for f in files if f.lower().endswith('.png')]
    
    if not png_files:
        logger.info("Nenhuma thumbnail PNG encontrada")
        return
    
    logger.info(f"Total de thumbnails: {len(png_files)}")
    
    for file in sorted(png_files):
        file_path = os.path.join(thumbnails_dir, file)
        size_kb = os.path.getsize(file_path) / 1024
        
        # Verificar se segue o padrão nome_thumb.png
        follows_pattern = file.endswith('_thumb.png')
        pattern_status = "✅" if follows_pattern else "❌"
        
        logger.info(f"  {pattern_status} {file} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    logger.info("Iniciando testes completos do sistema...")
    
    try:
        # Executar todos os testes
        naming_ok = test_naming_pattern()
        functionality_ok = test_all_functionalities()
        
        # Listar resultados
        list_generated_thumbnails()
        
        # Resultado final
        if naming_ok and functionality_ok:
            logger.info("\n🎉 TODOS OS TESTES PASSARAM! Sistema pronto para produção.")
        else:
            logger.error("\n❌ ALGUNS TESTES FALHARAM. Revisar implementação.")
            
    except Exception as e:
        logger.error(f"Erro durante os testes: {e}")
        sys.exit(1)