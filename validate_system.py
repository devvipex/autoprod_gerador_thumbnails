#!/usr/bin/env python3
"""
Script completo para validar todas as funcionalidades do sistema
"""

import os
import sys
from pathlib import Path
from PIL import Image

# Configurar path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import ThumbnailGeneratorApp
from src.domain.entities import Transform

def validate_initialization():
    """Valida inicialização da aplicação"""
    print("1. VALIDANDO INICIALIZACAO...")
    
    app = ThumbnailGeneratorApp()
    success = app.initialize()
    
    if success:
        print("   OK: Aplicacao inicializada")
        return app
    else:
        print("   ERRO: Falha na inicializacao")
        return None

def validate_image_validation(app):
    """Valida funcionalidade de validação de imagens"""
    print("\n2. VALIDANDO VALIDACAO DE IMAGENS...")
    
    # Testar com imagem válida
    test_image = "produtos-sem-fundo/Biqueiras Reilly.png"
    if os.path.exists(test_image):
        if app.validate_image(test_image):
            print("   OK: Validacao de imagem valida")
        else:
            print("   ERRO: Falha na validacao de imagem valida")
            return False
    else:
        print("   AVISO: Imagem de teste nao encontrada")
    
    # Testar com arquivo inexistente
    if not app.validate_image("arquivo_inexistente.png"):
        print("   OK: Rejeicao de arquivo inexistente")
    else:
        print("   ERRO: Aceitou arquivo inexistente")
        return False
    
    return True

def validate_background_loading(app):
    """Valida carregamento de backgrounds"""
    print("\n3. VALIDANDO CARREGAMENTO DE BACKGROUNDS...")
    
    backgrounds = app.load_backgrounds()
    
    if not backgrounds:
        print("   ERRO: Nenhum background carregado")
        return False, []
    
    print(f"   OK: {len(backgrounds)} backgrounds carregados")
    
    # Verificar se arquivos existem
    for bg in backgrounds:
        if os.path.exists(bg):
            print(f"      - {Path(bg).name}: OK")
        else:
            print(f"      - {Path(bg).name}: ERRO - arquivo nao existe")
            return False, []
    
    return True, backgrounds

def validate_composition(app, backgrounds):
    """Valida composição de imagens"""
    print("\n4. VALIDANDO COMPOSICAO DE IMAGENS...")
    
    test_image = "produtos-sem-fundo/Biqueiras Reilly.png"
    if not os.path.exists(test_image) or not backgrounds:
        print("   ERRO: Arquivos necessarios nao encontrados")
        return False, None
    
    # Teste 1: Composição básica
    print("   Teste 1: Composicao basica...")
    transform = Transform(x=0, y=0, scale=1.0, rotation=0)
    composition = app.compose_preview(test_image, backgrounds[0], transform)
    
    if not composition:
        print("      ERRO: Falha na composicao basica")
        return False, None
    
    print(f"      OK: Composicao criada ({composition.size}, {composition.mode})")
    
    # Teste 2: Composição com transformações
    print("   Teste 2: Composicao com transformacoes...")
    transform = Transform(x=50, y=50, scale=0.8, rotation=15)
    composition_transformed = app.compose_preview(test_image, backgrounds[0], transform)
    
    if not composition_transformed:
        print("      ERRO: Falha na composicao com transformacoes")
        return False, None
    
    print("      OK: Composicao com transformacoes")
    
    # Teste 3: Diferentes backgrounds
    if len(backgrounds) > 1:
        print("   Teste 3: Diferentes backgrounds...")
        composition_bg2 = app.compose_preview(test_image, backgrounds[1], transform)
        
        if composition_bg2:
            print("      OK: Composicao com background alternativo")
        else:
            print("      ERRO: Falha com background alternativo")
            return False, None
    
    return True, composition

def validate_export(app, composition):
    """Valida exportação de thumbnails"""
    print("\n5. VALIDANDO EXPORTACAO DE THUMBNAILS...")
    
    if not composition:
        print("   ERRO: Nenhuma composicao para exportar")
        return False
    
    # Teste 1: Exportação com nomenclatura automática
    print("   Teste 1: Exportacao com nomenclatura automatica...")
    original_name = "Produto Teste.png"
    export_path = app.export_thumbnail(composition, None, original_name)
    
    if not export_path or not os.path.exists(export_path):
        print("      ERRO: Falha na exportacao automatica")
        return False
    
    expected_name = "Produto Teste_thumb.png"
    actual_name = Path(export_path).name
    
    if actual_name == expected_name:
        print(f"      OK: Nomenclatura correta ({actual_name})")
    else:
        print(f"      ERRO: Nomenclatura incorreta (esperado: {expected_name}, obtido: {actual_name})")
        return False
    
    # Verificar tamanho e formato
    with Image.open(export_path) as img:
        if img.size == (1080, 1080) and img.format == 'PNG':
            print(f"      OK: Formato correto (1080x1080 PNG)")
        else:
            print(f"      ERRO: Formato incorreto ({img.size}, {img.format})")
            return False
    
    # Teste 2: Exportação com nome customizado
    print("   Teste 2: Exportacao com nome customizado...")
    custom_export = app.export_thumbnail(composition, "custom_name", original_name)
    
    if custom_export and os.path.exists(custom_export):
        custom_name = Path(custom_export).name
        if custom_name == "custom_name_thumb.png":
            print(f"      OK: Nome customizado correto ({custom_name})")
        else:
            print(f"      ERRO: Nome customizado incorreto ({custom_name})")
            return False
    else:
        print("      ERRO: Falha na exportacao customizada")
        return False
    
    return True

def validate_complete_workflow(app):
    """Valida workflow completo"""
    print("\n6. VALIDANDO WORKFLOW COMPLETO...")
    
    test_image = "produtos-sem-fundo/Biqueiras Reilly.png"
    backgrounds = app.load_backgrounds()
    
    if not os.path.exists(test_image) or not backgrounds:
        print("   ERRO: Arquivos necessarios nao encontrados")
        return False
    
    transform = Transform(x=25, y=25, scale=0.9, rotation=5)
    
    # Executar workflow completo (sem remoção de fundo pois Gradio pode não estar disponível)
    print("   Executando workflow de composicao e export...")
    
    try:
        # Compor
        composition = app.compose_preview(test_image, backgrounds[0], transform)
        if not composition:
            print("      ERRO: Falha na composicao do workflow")
            return False
        
        # Exportar
        original_name = Path(test_image).name
        result = app.export_thumbnail(composition, None, original_name)
        
        if result and os.path.exists(result):
            print(f"      OK: Workflow completo executado ({Path(result).name})")
            return True
        else:
            print("      ERRO: Falha no export do workflow")
            return False
            
    except Exception as e:
        print(f"      ERRO: Excecao no workflow: {e}")
        return False

def validate_status_reporting(app):
    """Valida relatório de status"""
    print("\n7. VALIDANDO RELATORIO DE STATUS...")
    
    try:
        status = app.get_status()
        
        required_keys = ['current_step', 'original_image', 'processed_image', 'gradio_available', 'backgrounds_count']
        
        for key in required_keys:
            if key in status:
                print(f"      {key}: {status[key]}")
            else:
                print(f"      ERRO: Chave '{key}' ausente no status")
                return False
        
        print("   OK: Status completo reportado")
        return True
        
    except Exception as e:
        print(f"   ERRO: Falha no relatorio de status: {e}")
        return False

def list_final_results():
    """Lista resultados finais"""
    print("\n=== RESULTADOS FINAIS ===")
    
    thumbnails_dir = "thumbnails-prontas"
    if not os.path.exists(thumbnails_dir):
        print("Pasta thumbnails-prontas nao existe")
        return
    
    files = [f for f in os.listdir(thumbnails_dir) if f.lower().endswith('.png')]
    
    if not files:
        print("Nenhuma thumbnail encontrada")
        return
    
    print(f"Total de thumbnails geradas: {len(files)}")
    
    total_size = 0
    pattern_ok = 0
    
    for file in sorted(files):
        file_path = os.path.join(thumbnails_dir, file)
        size_kb = os.path.getsize(file_path) / 1024
        total_size += size_kb
        
        # Verificar padrão
        follows_pattern = file.endswith('_thumb.png')
        if follows_pattern:
            pattern_ok += 1
        
        status = "OK" if follows_pattern else "ERRO"
        print(f"  {status}: {file} ({size_kb:.1f} KB)")
    
    print(f"\nResumo:")
    print(f"  Arquivos com padrao correto: {pattern_ok}/{len(files)}")
    print(f"  Tamanho total: {total_size:.1f} KB")
    print(f"  Tamanho medio: {total_size/len(files):.1f} KB")

def main():
    """Função principal de validação"""
    print("=== VALIDACAO COMPLETA DO SISTEMA ===")
    print("Testando todas as funcionalidades...\n")
    
    tests_passed = 0
    total_tests = 7
    
    try:
        # 1. Inicialização
        app = validate_initialization()
        if app:
            tests_passed += 1
        else:
            print("\nFALHA CRITICA: Nao foi possivel inicializar a aplicacao")
            return False
        
        # 2. Validação de imagens
        if validate_image_validation(app):
            tests_passed += 1
        
        # 3. Carregamento de backgrounds
        bg_ok, backgrounds = validate_background_loading(app)
        if bg_ok:
            tests_passed += 1
        
        # 4. Composição
        comp_ok, composition = validate_composition(app, backgrounds)
        if comp_ok:
            tests_passed += 1
        
        # 5. Exportação
        if validate_export(app, composition):
            tests_passed += 1
        
        # 6. Workflow completo
        if validate_complete_workflow(app):
            tests_passed += 1
        
        # 7. Status reporting
        if validate_status_reporting(app):
            tests_passed += 1
        
        # Resultados finais
        list_final_results()
        
        # Resumo
        print(f"\n=== RESUMO DA VALIDACAO ===")
        print(f"Testes passaram: {tests_passed}/{total_tests}")
        print(f"Taxa de sucesso: {(tests_passed/total_tests)*100:.1f}%")
        
        if tests_passed == total_tests:
            print("\nSUCESSO: Todas as funcionalidades estao operacionais!")
            print("Sistema pronto para integracao com frontend.")
            return True
        else:
            print("\nFALHA: Algumas funcionalidades precisam de correcao.")
            return False
            
    except Exception as e:
        print(f"\nERRO GERAL: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)