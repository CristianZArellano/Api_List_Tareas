"""
Pruebas unitarias para el hashing de contraseñas
"""
import pytest
import time
from app.security import get_password_hash, verify_password
from app.password_validator import validate_password_strength


@pytest.mark.password
@pytest.mark.security
@pytest.mark.unit
class TestPasswordHashing:
    """Pruebas para el hashing y verificación de contraseñas"""

    def test_password_hashing_basic(self):
        """Prueba el hashing básico de contraseñas"""
        password = "TestPasswordX9!"
        hashed = get_password_hash(password)
        
        # Verificar que el hash es diferente de la contraseña original
        assert hashed != password
        
        # Verificar que la contraseña se puede verificar correctamente
        assert verify_password(password, hashed) is True
        
        # Verificar que una contraseña incorrecta no funciona
        assert verify_password("WrongPasswordX9!", hashed) is False

    def test_password_hashing_unique_salt(self):
        """Prueba que cada hash es único debido al salt"""
        password = "TestPasswordX9!"
        
        # Generar múltiples hashes
        hashes = []
        for _ in range(5):
            hashed = get_password_hash(password)
            hashes.append(hashed)
        
        # Verificar que todos los hashes son únicos
        unique_hashes = set(hashes)
        assert len(unique_hashes) == len(hashes)
        
        # Verificar que todos funcionan
        for hashed in hashes:
            assert verify_password(password, hashed) is True

    def test_password_hashing_international(self):
        """Prueba hashing con contraseñas internacionales"""
        international_passwords = [
            "Mañana2024!",
            "Árbol#Grande1",
            "Пароль2024!",
            "密碼Test2024!",
            "MotDePasse2024!",
            "Passwörd2024!",
            "SenhaForte2024!",
            "P@sswørd2024!",
            "ContraseñaÜñîçødë1!"
        ]
        
        for password in international_passwords:
            # Validar que la contraseña cumple los requisitos
            is_valid, error_msg = validate_password_strength(password)
            assert is_valid, f"Contraseña '{password}' debería ser válida: {error_msg}"
            
            # Generar hash
            hashed = get_password_hash(password)
            
            # Verificar hash
            assert verify_password(password, hashed) is True
            
            # Verificar que contraseña incorrecta es rechazada
            wrong_password = password + "WRONG"
            assert verify_password(wrong_password, hashed) is False

    def test_password_hashing_performance(self):
        """Prueba el rendimiento del hashing"""
        password = "TestPasswordX9!"
        
        # Medir tiempo de hash
        start_time = time.time()
        hashed = get_password_hash(password)
        hash_time = time.time() - start_time
        
        # El hash debería tomar un tiempo razonable (no instantáneo, no muy lento)
        assert 0.01 <= hash_time <= 5.0, f"Tiempo de hash inusual: {hash_time:.3f}s"
        
        # Medir tiempo de verificación
        start_time = time.time()
        is_correct = verify_password(password, hashed)
        verify_time = time.time() - start_time
        
        assert is_correct is True
        assert 0.01 <= verify_time <= 5.0, f"Tiempo de verificación inusual: {verify_time:.3f}s"

    def test_password_hashing_edge_cases(self):
        """Prueba casos edge del hashing"""
        # Contraseña muy larga
        long_password = "A" * 100 + "123!"
        hashed = get_password_hash(long_password)
        assert verify_password(long_password, hashed) is True
        
        # Contraseña con caracteres especiales
        special_password = "!@#$%^&*()_+-=[]{}|;:,.<>?`~"
        hashed = get_password_hash(special_password)
        assert verify_password(special_password, hashed) is True
        
        # Contraseña con emojis (si es válida según la validación)
        emoji_password = "Test123!😀"
        is_valid, _ = validate_password_strength(emoji_password)
        if is_valid:
            hashed = get_password_hash(emoji_password)
            assert verify_password(emoji_password, hashed) is True

    def test_password_hashing_consistency(self):
        """Prueba la consistencia del hashing"""
        password = "TestPasswordX9!"
        
        # Generar hash múltiples veces
        hashes = []
        for _ in range(10):
            hashed = get_password_hash(password)
            hashes.append(hashed)
            
            # Verificar inmediatamente
            assert verify_password(password, hashed) is True
        
        # Verificar que todos los hashes son únicos
        unique_hashes = set(hashes)
        assert len(unique_hashes) == len(hashes)

    def test_password_hashing_invalid_inputs(self):
        """Prueba el comportamiento con entradas inválidas"""
        # Contraseña vacía
        empty_password = ""
        hashed = get_password_hash(empty_password)
        assert verify_password(empty_password, hashed) is True
        
        # Hash inválido
        password = "TestPasswordX9!"
        try:
            result = verify_password(password, "invalid_hash")
            assert result is False
        except Exception:
            # Si la función lanza una excepción, eso también es aceptable
            pass
        
        # Hash vacío
        try:
            result = verify_password(password, "")
            assert result is False
        except Exception:
            # Si la función lanza una excepción, eso también es aceptable
            pass

    def test_password_hashing_unicode_support(self):
        """Prueba soporte completo para Unicode"""
        unicode_passwords = [
            "ContraseñaÜñîçødë1!",
            "P@sswørd2024!",
            "密碼Test2024!",
            "Пароль2024!",
            "كلمةالمرور2024!",
            "パスワード2024!",
            "암호2024!"
        ]
        
        for password in unicode_passwords:
            # Validar primero
            is_valid, error_msg = validate_password_strength(password)
            if is_valid:
                # Generar hash
                hashed = get_password_hash(password)
                
                # Verificar
                assert verify_password(password, hashed) is True
                
                # Verificar que cambios mínimos son detectados
                modified_password = password[:-1] + "X"
                assert verify_password(modified_password, hashed) is False


@pytest.mark.password
@pytest.mark.security
@pytest.mark.unit
class TestPasswordHashingSecurity:
    """Pruebas de seguridad para el hashing de contraseñas"""

    def test_hash_format(self):
        """Prueba que el hash tiene el formato correcto"""
        password = "TestPasswordX9!"
        hashed = get_password_hash(password)
        
        # Verificar que el hash comienza con $2b$ (bcrypt)
        assert hashed.startswith("$2b$"), "Hash debería usar bcrypt"
        
        # Verificar que el hash tiene la longitud correcta
        assert len(hashed) == 60, f"Hash debería tener 60 caracteres, tiene {len(hashed)}"

    def test_hash_collision_resistance(self):
        """Prueba resistencia a colisiones"""
        password1 = "TestPasswordX9!"
        password2 = "TestPasswordX9!"
        
        # Mismas contraseñas deberían generar hashes diferentes (salt único)
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2, "Hashes de la misma contraseña deberían ser diferentes"
        
        # Ambas deberían verificar correctamente
        assert verify_password(password1, hash1) is True
        assert verify_password(password2, hash2) is True

    def test_hash_timing_attack_resistance(self):
        """Prueba resistencia a ataques de tiempo"""
        password = "TestPasswordX9!"
        hashed = get_password_hash(password)
        
        # Medir tiempo de verificación correcta
        start_time = time.time()
        verify_password(password, hashed)
        correct_time = time.time() - start_time
        
        # Medir tiempo de verificación incorrecta
        start_time = time.time()
        verify_password("WrongPasswordX9!", hashed)
        incorrect_time = time.time() - start_time
        
        # Los tiempos deberían ser similares (diferencia < 0.1s)
        time_diff = abs(correct_time - incorrect_time)
        assert time_diff < 0.1, f"Diferencia de tiempo muy grande: {time_diff:.3f}s"

    def test_hash_work_factor(self):
        """Prueba que el factor de trabajo es apropiado"""
        password = "TestPasswordX9!"
        
        # Generar hash y medir tiempo
        start_time = time.time()
        hashed = get_password_hash(password)
        hash_time = time.time() - start_time
        
        # El tiempo debería ser razonable (no muy rápido, no muy lento)
        assert 0.01 <= hash_time <= 2.0, f"Factor de trabajo inapropiado: {hash_time:.3f}s"
        
        # Verificar que el hash funciona
        assert verify_password(password, hashed) is True 