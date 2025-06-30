#!/usr/bin/env python3
"""
Script para ejecutar los tests de la aplicación
"""
import subprocess
import sys
import os

def run_tests():
    """Ejecuta los tests usando pytest"""
    print("🚀 Ejecutando tests de la aplicación...")
    print("=" * 50)
    
    # Verificar que pytest esté instalado
    try:
        import pytest
    except ImportError:
        print("❌ Error: pytest no está instalado.")
        print("Instala las dependencias con: pip install -r requirements.txt")
        return False
    
    # Ejecutar tests
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short"
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ Todos los tests pasaron exitosamente!")
            return True
        else:
            print("\n❌ Algunos tests fallaron.")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")
        return False

def run_specific_test(test_name):
    """Ejecuta un test específico"""
    print(f"🚀 Ejecutando test: {test_name}")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            f"tests/{test_name}", 
            "-v", 
            "--tb=short"
        ], capture_output=False, text=True)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error ejecutando test: {e}")
        return False

def run_test_category(category):
    """Ejecuta una categoría específica de tests"""
    print(f"🚀 Ejecutando tests de categoría: {category}")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-m", category,
            "-v", 
            "--tb=short"
        ], capture_output=False, text=True)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error ejecutando tests de categoría {category}: {e}")
        return False

def run_unit_tests():
    """Ejecuta solo los tests unitarios"""
    return run_test_category("unit")

def run_integration_tests():
    """Ejecuta solo los tests de integración"""
    return run_test_category("integration")

def run_password_tests():
    """Ejecuta solo los tests de contraseñas"""
    return run_test_category("password")

def run_api_tests():
    """Ejecuta solo los tests de API"""
    return run_test_category("api")

def run_security_tests():
    """Ejecuta solo los tests de seguridad"""
    return run_test_category("security")

def show_help():
    """Muestra la ayuda del script"""
    print("🔧 Script de Ejecución de Tests")
    print("=" * 50)
    print("Uso:")
    print("  python run_tests.py                    # Ejecutar todos los tests")
    print("  python run_tests.py unit               # Ejecutar tests unitarios")
    print("  python run_tests.py integration        # Ejecutar tests de integración")
    print("  python run_tests.py password           # Ejecutar tests de contraseñas")
    print("  python run_tests.py api                # Ejecutar tests de API")
    print("  python run_tests.py security           # Ejecutar tests de seguridad")
    print("  python run_tests.py test_file.py       # Ejecutar archivo específico")
    print("  python run_tests.py help               # Mostrar esta ayuda")
    print("\nCategorías disponibles:")
    print("  - unit: Tests unitarios")
    print("  - integration: Tests de integración")
    print("  - password: Tests de validación y hashing de contraseñas")
    print("  - api: Tests de endpoints de la API")
    print("  - security: Tests de características de seguridad")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "help":
            show_help()
            sys.exit(0)
        elif command == "unit":
            success = run_unit_tests()
        elif command == "integration":
            success = run_integration_tests()
        elif command == "password":
            success = run_password_tests()
        elif command == "api":
            success = run_api_tests()
        elif command == "security":
            success = run_security_tests()
        else:
            # Ejecutar archivo específico
            success = run_specific_test(command)
    else:
        # Ejecutar todos los tests
        success = run_tests()
    
    sys.exit(0 if success else 1) 