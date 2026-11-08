import logging
import os
from abc import ABC, abstractmethod

# Configuración del archivo de registros (logs)
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/sistema_fj.log",
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def registrar_evento(mensaje):
    """Registra eventos exitosos en el archivo de log."""
    logging.info(mensaje)

def registrar_error(mensaje, excepcion=None):
    """Registra errores controlados en el archivo de log."""
    if excepcion:
        logging.error(f"{mensaje} | Detalle: {excepcion}")
    else:
        logging.error(mensaje)


# Clases de Excepciones Personalizadas
class FJBaseException(Exception):
    """Excepción base del sistema Software FJ."""
    pass

class DatosInvalidosError(FJBaseException):
    def __init__(self, mensaje="Los datos proporcionados no cumplen con el formato requerido."):
        super().__init__(mensaje)

class ServicioNoDisponibleError(FJBaseException):
    def __init__(self, mensaje="El servicio solicitado se encuentra inactivo o no disponible."):
        super().__init__(mensaje)

class OperacionNoPermitidaError(FJBaseException):
    def __init__(self, mensaje="La acción intentada no está permitida para el estado actual."):
        super().__init__(mensaje)

class CalculoInconsistenteError(FJBaseException):
    def __init__(self, mensaje="Error lógico o matemático en el cálculo de costos."):
        super().__init__(mensaje)


# Clases Base del Sistema (POO)
class EntidadBase(ABC):
    """Clase abstracta base para entidades del sistema."""
    
    @abstractmethod
    def obtener_detalles(self):
        pass

class Cliente(EntidadBase):
    """Clase que gestiona la información y validaciones del cliente."""
    
    def __init__(self, cedula, nombre, correo, telefono):
        self.cedula = cedula
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def cedula(self):
        return self._cedula

    @cedula.setter
    def cedula(self, valor):
        if not str(valor).isdigit() or len(str(valor)) < 6:
            raise DatosInvalidosError(f"Cédula inválida o formato incorrecto: {valor}")
        self._cedula = valor

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if "@" not in valor or "." not in valor:
            raise DatosInvalidosError(f"Correo electrónico inválido: {valor}")
        self._correo = valor

    def obtener_detalles(self):
        return f"Cliente [Cédula: {self.cedula}, Nombre: {self.nombre}, Correo: {self.correo}]"


# Bloque de prueba inicial para verificar que todo funciona bien
if __name__ == "__main__":
    print("--- Iniciando pruebas de Estudiante 1 ---")
    try:
        # Prueba 1: Cliente válido
        c1 = Cliente("11223344", "Hoover García", "hoover@mail.com", "3504919193")
        print(c1.obtener_detalles())
        registrar_evento(f"Cliente creado exitosamente: {c1.nombre}")
        
        # Prueba 2: Error controlado (cédula corta o con letras)
        c_malo = Cliente("123", "Prueba Error", "error@mail.com", "3000000000")
    except DatosInvalidosError as e:
        print(f"[EXCEPCIÓN CAPTURADA EXITOSAMENTE]: {e}")
        registrar_error("Fallo al registrar cliente", e)
      
