class AuthService:
    # Credenciales hardcodeadas para el prototipo académico
    _USUARIOS = {
        "admin": "1234",
        "doctor": "medic2026",
    }

    def authenticate(self, usuario: str, contrasena: str) -> bool:
        """Retorna True si las credenciales son válidas."""
        return self._USUARIOS.get(usuario.lower()) == contrasena
