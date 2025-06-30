"""
Pruebas unitarias para la validación de contraseñas
"""
import pytest
from app.password_validator import (
    validate_password_strength,
    validate_password,
    get_password_requirements,
    check_password_strength
)
from app.config import settings


@pytest.mark.password
@pytest.mark.unit
class TestPasswordValidation:
    """Pruebas para la validación de contraseñas"""

    def test_valid_passwords(self):
        """Prueba contraseñas válidas con caracteres internacionales"""
        valid_passwords = [
            "Mañana2024!",
            "Árbol#Grande1",
            "Пароль2024!",
            "密碼Test2024!",
            "MotDePasse2024!",
            "Passwörd2024!",
            "SenhaForte2024!",
            "P@sswørd2024!",
            "ContraseñaÜñîçødë1!",
            "SecurePassX9!"
        ]
        
        for password in valid_passwords:
            is_valid, error_message = validate_password_strength(password)
            assert is_valid, f"Contraseña '{password}' debería ser válida: {error_message}"

    def test_invalid_passwords_too_short(self):
        """Prueba contraseñas demasiado cortas"""
        short_passwords = ["Short1!", "A", "123", "abc"]
        
        for password in short_passwords:
            is_valid, error_message = validate_password_strength(password)
            assert not is_valid, f"Contraseña '{password}' debería ser inválida"
            error_lower = error_message.lower()
            assert "corta" in error_lower or "8 caracteres" in error_message

    def test_invalid_passwords_too_long(self):
        """Prueba contraseñas demasiado largas"""
        long_password = "A" * 129
        is_valid, error_message = validate_password_strength(long_password)
        assert not is_valid
        error_lower = error_message.lower()
        assert "larga" in error_lower or "128 caracteres" in error_message

    def test_invalid_passwords_no_lowercase(self):
        """Prueba contraseñas sin minúsculas"""
        passwords = ["PASSWORD123!", "TEST123!", "UPPER123!"]
        
        for password in passwords:
            is_valid, error_message = validate_password_strength(password)
            assert not is_valid, f"Contraseña '{password}' debería ser inválida"
            error_lower = error_message.lower()
            assert "minúscula" in error_lower

    def test_invalid_passwords_no_uppercase(self):
        """Prueba contraseñas sin mayúsculas"""
        passwords = ["password123!", "lower123!", "test123!"]
        
        for password in passwords:
            is_valid, error_message = validate_password_strength(password)
            assert not is_valid, f"Contraseña '{password}' debería ser inválida"
            error_lower = error_message.lower()
            assert "mayúscula" in error_lower

    def test_invalid_passwords_no_digits(self):
        """Prueba contraseñas sin números"""
        passwords = ["Password!", "TestPass!", "SecurePass!"]
        
        for password in passwords:
            is_valid, error_message = validate_password_strength(password)
            assert not is_valid, f"Contraseña '{password}' debería ser inválida"
            error_lower = error_message.lower()
            assert "número" in error_lower or "dígito" in error_lower

    def test_invalid_passwords_no_special_chars(self):
        """Prueba contraseñas sin caracteres especiales"""
        passwords = ["Password123", "TestPass123", "SecurePass123"]
        
        for password in passwords:
            is_valid, error_message = validate_password_strength(password)
            assert not is_valid, f"Contraseña '{password}' debería ser inválida"
            error_lower = error_message.lower()
            assert "especial" in error_lower

    def test_common_passwords(self):
        """Prueba contraseñas comunes que no deberían ser permitidas"""
        common_passwords = [
            "Password123!",  # Cumple requisitos pero es común
            "Admin123!",     # Cumple requisitos pero es común
            "Test123!",      # Cumple requisitos pero es común
            "User123!",      # Cumple requisitos pero es común
            "Login123!"      # Cumple requisitos pero es común
        ]
        
        for password in common_passwords:
            is_valid, error_message = validate_password_strength(password)
            assert not is_valid, f"Contraseña común '{password}' debería ser rechazada"
            error_lower = error_message.lower()
            assert "común" in error_lower or "secuencia" in error_lower

    def test_passwords_with_spaces(self):
        """Prueba contraseñas con espacios"""
        passwords_with_spaces = [
            "Password 123!",
            "Test Pass 123!",
            "Secure Pass 123!"
        ]
        
        for password in passwords_with_spaces:
            is_valid, error_message = validate_password_strength(password)
            assert not is_valid, f"Contraseña con espacios '{password}' debería ser rechazada"
            error_lower = error_message.lower()
            assert "espacio" in error_lower

    def test_passwords_with_repeated_chars(self):
        """Prueba contraseñas con caracteres repetidos"""
        passwords_with_repeats = [
            "Password111!",
            "TestPass222!",
            "SecurePass333!"
        ]
        
        for password in passwords_with_repeats:
            is_valid, error_message = validate_password_strength(password)
            assert not is_valid, f"Contraseña con repeticiones '{password}' debería ser rechazada"
            error_lower = error_message.lower()
            assert "repetido" in error_lower

    def test_empty_password(self):
        """Prueba contraseña vacía"""
        is_valid, error_message = validate_password_strength("")
        assert not is_valid
        error_lower = error_message.lower()
        assert "corta" in error_lower or "8 caracteres" in error_message

    def test_unicode_passwords(self):
        """Prueba contraseñas con caracteres Unicode complejos"""
        unicode_passwords = [
            "ContraseñaÜñîçødë1!",
            "P@sswørd2024!",
            "密碼Test2024!",
            "Пароль2024!"
        ]
        
        for password in unicode_passwords:
            is_valid, error_message = validate_password_strength(password)
            assert is_valid, f"Contraseña Unicode '{password}' debería ser válida: {error_message}"


@pytest.mark.password
@pytest.mark.unit
class TestPasswordStrengthAnalysis:
    """Pruebas para el análisis de fortaleza de contraseñas"""

    def test_strength_analysis_valid_password(self):
        """Prueba análisis de fortaleza para contraseña válida"""
        password = "SecurePass123!"
        analysis = check_password_strength(password)
        
        assert analysis["length"] == len(password)
        assert analysis["has_uppercase"] is True
        assert analysis["has_lowercase"] is True
        assert analysis["has_digit"] is True
        assert analysis["has_symbol"] is True
        assert analysis["has_spaces"] is False
        assert analysis["has_repeating_chars"] is False
        assert analysis["is_common"] is False
        assert analysis["score"] >= 6
        assert analysis["strength"] in ["moderada", "fuerte", "muy_fuerte"]

    def test_strength_analysis_weak_password(self):
        """Prueba análisis de fortaleza para contraseña débil"""
        password = "weak"
        analysis = check_password_strength(password)
        
        assert analysis["length"] == len(password)
        assert analysis["has_uppercase"] is False
        assert analysis["has_lowercase"] is True
        assert analysis["has_digit"] is False
        assert analysis["has_symbol"] is False
        assert analysis["score"] <= 2
        assert analysis["strength"] in ["muy_débil", "débil"]

    def test_strength_analysis_common_password(self):
        """Prueba análisis de fortaleza para contraseña común"""
        password = "password"
        analysis = check_password_strength(password)
        
        assert analysis["is_common"] is True
        assert analysis["score"] <= 3

    def test_strength_analysis_with_repeats(self):
        """Prueba análisis de fortaleza para contraseña con repeticiones"""
        password = "Password111!"
        analysis = check_password_strength(password)
        
        assert analysis["has_repeating_chars"] is True
        assert analysis["score"] <= 5


@pytest.mark.password
@pytest.mark.unit
class TestPasswordRequirements:
    """Pruebas para los requisitos de contraseña"""

    def test_get_password_requirements(self):
        """Prueba la función que obtiene los requisitos"""
        requirements = get_password_requirements()
        
        assert "min_length" in requirements
        assert "max_length" in requirements
        assert "requirements" in requirements
        assert isinstance(requirements["requirements"], list)
        assert len(requirements["requirements"]) > 0
        
        # Verificar que los valores coinciden con la configuración
        assert requirements["min_length"] == settings.MIN_PASSWORD_LENGTH
        assert requirements["max_length"] == settings.MAX_PASSWORD_LENGTH

    def test_requirements_content(self):
        """Prueba el contenido de los requisitos"""
        requirements = get_password_requirements()
        
        # Verificar que los requisitos contienen información útil
        requirements_text = " ".join(requirements["requirements"]).lower()
        assert "mayúscula" in requirements_text
        assert "minúscula" in requirements_text
        assert "número" in requirements_text or "dígito" in requirements_text
        assert "especial" in requirements_text


@pytest.mark.password
@pytest.mark.unit
class TestPasswordValidationIntegration:
    """Pruebas de integración para la validación de contraseñas"""

    def test_validate_password_function(self):
        """Prueba la función validate_password (alias)"""
        # Contraseña válida
        is_valid, error_message = validate_password("SecurePassX9!")
        assert is_valid
        
        # Contraseña inválida
        is_valid, error_message = validate_password("weak")
        assert not is_valid
        assert error_message is not None

    def test_validation_with_config_settings(self):
        """Prueba que la validación respeta la configuración"""
        # Verificar que la regex de configuración se usa
        assert hasattr(settings, 'PASSWORD_REGEX')
        assert hasattr(settings, 'MIN_PASSWORD_LENGTH')
        assert hasattr(settings, 'MAX_PASSWORD_LENGTH')
        assert hasattr(settings, 'COMMON_PASSWORDS')

    def test_error_messages_consistency(self):
        """Prueba que los mensajes de error son consistentes"""
        error_messages = settings.PASSWORD_ERROR_MESSAGES
        
        # Verificar que todos los tipos de error tienen mensajes
        expected_errors = [
            "too_short", "too_long", "no_lowercase", "no_uppercase",
            "no_digit", "no_special", "invalid_chars", "common_password",
            "sequential_chars", "repeated_chars"
        ]
        
        for error_type in expected_errors:
            assert error_type in error_messages, f"Falta mensaje para error: {error_type}"
            assert len(error_messages[error_type]) > 0, f"Mensaje vacío para error: {error_type}" 