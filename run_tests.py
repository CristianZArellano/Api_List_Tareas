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
            "test_api.py", 
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
            f"test_api.py::{test_name}", 
            "-v", 
            "--tb=short"
        ], capture_output=False, text=True)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error ejecutando test: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Ejecutar test específico
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Ejecutar todos los tests
        success = run_tests()
    
    sys.exit(0 if success else 1) 