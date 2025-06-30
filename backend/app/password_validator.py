# app/password_validator.py
from password_validator import PasswordValidator
from typing import Tuple, List
from app.config import settings

# Crear el validador de contraseñas con estándares modernos
def create_password_validator() -> PasswordValidator:
    """
    Crea un validador de contraseñas siguiendo estándares de seguridad modernos.
    
    Basado en recomendaciones de:
    - OWASP Password Guidelines
    - NIST Digital Identity Guidelines
    - ISO/IEC 27001
    """
    schema = PasswordValidator()
    
    # Longitud mínima y máxima
    schema.min(settings.MIN_PASSWORD_LENGTH).max(settings.MAX_PASSWORD_LENGTH)
    
    # Requisitos de caracteres
    schema.has().uppercase()  # Al menos una mayúscula
    schema.has().lowercase()  # Al menos una minúscula
    schema.has().digits()     # Al menos un dígito
    schema.has().symbols()    # Al menos un símbolo
    
    # Evitar espacios
    schema.no().spaces()
    
    return schema

# Instancia global del validador
_password_validator = create_password_validator()

def validate_custom_rules(password: str) -> List[str]:
    """
    Valida reglas adicionales de seguridad que no están en password-validator.
    
    Args:
        password: La contraseña a validar
        
    Returns:
        List[str]: Lista de errores encontrados
    """
    errors = []
    
    # Verificar que no sea una contraseña común
    if password.lower() in settings.COMMON_PASSWORDS:
        errors.append("La contraseña es demasiado común")
    
    # Verificar caracteres repetidos consecutivos (más de 3)
    for i in range(len(password) - 2):
        if password[i] == password[i+1] == password[i+2]:
            errors.append("La contraseña no puede tener caracteres repetidos consecutivos")
            break
    
    # Verificar secuencias comunes
    sequences = ['123', '234', '345', '456', '567', '678', '789', '890',
                 'abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi', 'hij',
                 'ijk', 'jkl', 'klm', 'lmn', 'mno', 'nop', 'opq', 'pqr',
                 'qrs', 'rst', 'stu', 'tuv', 'uvw', 'vwx', 'wxy', 'xyz',
                 'qwe', 'wer', 'ert', 'rty', 'tyu', 'yui', 'uio', 'iop',
                 'asd', 'sdf', 'dfg', 'fgh', 'ghj', 'hjk', 'jkl', 'klz',
                 'zxc', 'xcv', 'cvb', 'vbn', 'bnm', 'nmq', 'mqw', 'qwe']
    
    password_lower = password.lower()
    for seq in sequences:
        if seq in password_lower:
            errors.append("La contraseña no puede contener secuencias de caracteres")
            break
    
    return errors

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Valida que la contraseña cumpla con todos los requisitos de seguridad.
    
    Args:
        password: La contraseña a validar
        
    Returns:
        Tuple[bool, str]: (es_válida, mensaje_error)
    """
    try:
        # Validar usando password-validator
        is_valid = _password_validator.validate(password)
        
        if not is_valid:
            # Crear mensajes de error específicos
            error_messages = []
            
            if len(password) < settings.MIN_PASSWORD_LENGTH:
                error_messages.append(f"La contraseña debe tener al menos {settings.MIN_PASSWORD_LENGTH} caracteres")
            elif len(password) > settings.MAX_PASSWORD_LENGTH:
                error_messages.append(f"La contraseña no puede tener más de {settings.MAX_PASSWORD_LENGTH} caracteres")
            
            if not any(c.isupper() for c in password):
                error_messages.append("La contraseña debe contener al menos una letra mayúscula")
            
            if not any(c.islower() for c in password):
                error_messages.append("La contraseña debe contener al menos una letra minúscula")
            
            if not any(c.isdigit() for c in password):
                error_messages.append("La contraseña debe contener al menos un número")
            
            if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
                error_messages.append("La contraseña debe contener al menos un carácter especial")
            
            if ' ' in password:
                error_messages.append("La contraseña no puede contener espacios")
            
            return False, "; ".join(error_messages)
        
        # Validar reglas adicionales
        custom_errors = validate_custom_rules(password)
        if custom_errors:
            return False, "; ".join(custom_errors)
        
        return True, ""
        
    except Exception as e:
        return False, f"Error en la validación: {str(e)}"

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Valida que la contraseña cumpla con los requisitos mínimos (compatibilidad).
    
    Args:
        password: La contraseña a validar
        
    Returns:
        Tuple[bool, str]: (es_válida, mensaje_error)
    """
    return validate_password_strength(password)

def get_password_requirements() -> dict:
    """
    Retorna los requisitos de contraseña para mostrar al usuario.
    
    Returns:
        dict: Diccionario con los requisitos de contraseña
    """
    return {
        "min_length": settings.MIN_PASSWORD_LENGTH,
        "max_length": settings.MAX_PASSWORD_LENGTH,
        "requirements": [
            "Al menos una letra mayúscula (de cualquier idioma)",
            "Al menos una letra minúscula (de cualquier idioma)",
            "Al menos un número",
            "Al menos un carácter especial (!@#$%^&*()_+-=[]{}|;:,.<>?)",
            "No puede contener espacios",
            "No puede tener caracteres repetidos consecutivos",
            "No puede contener secuencias de caracteres",
            "No puede ser una contraseña común"
        ]
    }

def check_password_strength(password: str) -> dict:
    """
    Evalúa la fortaleza de una contraseña y retorna un análisis detallado.
    
    Args:
        password: La contraseña a evaluar
        
    Returns:
        dict: Análisis detallado de la fortaleza de la contraseña
    """
    analysis = {
        "length": len(password),
        "has_uppercase": any(c.isupper() for c in password),
        "has_lowercase": any(c.islower() for c in password),
        "has_digit": any(c.isdigit() for c in password),
        "has_symbol": any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password),
        "has_spaces": ' ' in password,
        "has_repeating_chars": any(password[i] == password[i+1] == password[i+2] 
                                  for i in range(len(password)-2)),
        "is_common": password.lower() in settings.COMMON_PASSWORDS,
        "score": 0,
        "strength": "muy_débil"
    }
    
    # Calcular puntuación de fortaleza
    score = 0
    
    # Longitud
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    
    # Complejidad
    if analysis["has_uppercase"]:
        score += 1
    if analysis["has_lowercase"]:
        score += 1
    if analysis["has_digit"]:
        score += 1
    if analysis["has_symbol"]:
        score += 1
    
    # Penalizaciones
    if analysis["has_spaces"]:
        score -= 1
    if analysis["has_repeating_chars"]:
        score -= 1
    if analysis["is_common"]:
        score -= 2
    
    analysis["score"] = max(0, score)
    
    # Determinar nivel de fortaleza
    if analysis["score"] <= 2:
        analysis["strength"] = "muy_débil"
    elif analysis["score"] <= 4:
        analysis["strength"] = "débil"
    elif analysis["score"] <= 6:
        analysis["strength"] = "moderada"
    elif analysis["score"] <= 8:
        analysis["strength"] = "fuerte"
    else:
        analysis["strength"] = "muy_fuerte"
    
    return analysis 