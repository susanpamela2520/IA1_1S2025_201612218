class AuthService:
    def __init__(self):
      
      #Aqui se realiza la utenticacion para ingresar como administrador
        self.admin_user = "admin"
        self.admin_password = "1234"

    def authenticate(self, username: str, password: str) -> bool:
        return username == self.admin_user and password == self.admin_password