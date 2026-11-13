
import logging
import os
from abc import ABC, abstractmethod
import math

# Configuración del archivo de registros (logs)
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/sistema_fj.log",
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    force=True
)

def registrar_evento(mensaje):
    """Registra eventos exitosos en el archivo de log."""
    logging.info(mensaje)

def registrar_error(mensaje, excepcion=None):
    """Registra errores controlados en el archivo de log."""
    if excepcion is not None:
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
        if not isinstance(valor, str) or "@" not in valor or "." not in valor:
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


# ------------------------------------------------------------------------
# ESTUDIANTE 2: CLASE ABSTRACTA SERVICIO Y SERVICIOS DERIVADOS
# Desarrollado por : Estudiante 2 (JOSE DAVID PUMALPA REYES)
# ----------------------------------------------------------------------

# ---------------------------------------------------------------------
# FUNCIÓN AUXILIAR PARA REGISTRAR ERRORES
# Aqui se utiliza la función registrar_error() desarrollada por el Estudiante 1.
# ---------------------------------------------------------------------

def crear_error_servicio(tipo_error, mensaje):
    """Registra el error y devuelve la excepción correspondiente."""
    registrar_error(mensaje)
    return tipo_error(mensaje)


# ---------------------------------------------------------------------
# CLASE ABSTRACTA SERVICIO
#
# Representa la estructura general de los servicios de Software FJ.
# Hereda de EntidadBase y obliga a las clases derivadas a implementar
# sus propios métodos para calcular costos, describir y validar.
# ---------------------------------------------------------------------

class Servicio(EntidadBase, ABC):

    def __init__(self, codigo, nombre, tarifa_base, disponible=True):

        # Se utilizan las propiedades para validar los atributos.
        self.codigo = codigo
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self.disponible = disponible

        # Contador interno de reservas activas del servicio.
        self._reservas_activas = 0

    # ----------------------------------------------------------------
    # ENCAPSULAMIENTO DE: PROPIEDAD CODIGO
    # ---------------------------------------------------------------

    @property
    def codigo(self):
        return self._codigo

    @codigo.setter
    def codigo(self, valor):

        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise crear_error_servicio(
                DatosInvalidosError,
                f"Código inválido: '{valor}'. Mínimo 3 caracteres."
            )

        self._codigo = valor.strip().upper()

    # ---------------------------------------------------------------------
    # ENCAPSULAMIENTO DE: PROPIEDAD NOMBRE
    # -----------------------------------------------------------------------

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):

        if not isinstance(valor, str) or not valor.strip():
            raise crear_error_servicio(
                DatosInvalidosError,
                "El nombre del servicio no puede estar vacío."
            )

        self._nombre = valor.strip()

    # --------------------------------------------------------------------
    # ENCAPSULAMIENTO DE: PROPIEDAD TARIFA_BASE
    # --------------------------------------------------------------------

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor):

        # Evita que se  acepten valores booleanos como números.
        if isinstance(valor, bool):
            raise crear_error_servicio(
                DatosInvalidosError,
                "La tarifa debe ser un número válido."
            )

        try:
            valor = float(valor)

        except (TypeError, ValueError) as e:
            raise crear_error_servicio(
                DatosInvalidosError,
                f"Tarifa inválida: '{valor}'."
            ) from e

        # Rechaza valores negativos, cero, infinitos.
        if not math.isfinite(valor) or valor <= 0:
            raise crear_error_servicio(
                DatosInvalidosError,
                "La tarifa debe ser un número positivo y finito."
            )

        self._tarifa_base = valor

    # ----------------------------------------------------------------
    # ENCAPSULAMIENTO DE: PROPIEDAD DISPONIBLE
    # -----------------------------------------------------------------

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):

        # Solo permite valores booleanos.
        if not isinstance(valor, bool):
            raise crear_error_servicio(
                DatosInvalidosError,
                "El atributo disponible debe ser True o False."
            )

        self._disponible = valor

    # -----------------------------------------------------------------
    # MÉTODOS ABSTRACTOS
    #
    # Las clases derivadas deben implementar estos tres métodos.
    # Esto permite aplicar polimorfismo y sobrescritura.
    # -----------------------------------------------------------------

    @abstractmethod
    def calcular_costo(self, duracion, **kwargs):
        """Calcula el costo según el tipo de servicio."""
        pass

    @abstractmethod
    def describir(self):
        """Devuelve una descripción específica del servicio."""
        pass

    @abstractmethod
    def validar_parametros(self, **kwargs):
        """Valida los parámetros necesarios para cada servicio."""
        pass

    # -----------------------------------------------------------------
    # MÉTODOS CONCRETOS COMPARTIDOS
    # -----------------------------------------------------------------

    def verificar_disponibilidad(self):
        """Comprueba si el servicio puede ser utilizado."""

        if not self.disponible:
            raise crear_error_servicio(
                ServicioNoDisponibleError,
                f"El servicio '{self.nombre}' ({self.codigo}) no está disponible."
            )

        return True

    def registrar_uso(self):
        """Incrementa el contador de reservas activas."""

        self._reservas_activas += 1

        registrar_evento(
            f"Uso registrado para el servicio {self.codigo}. "
            f"Reservas activas: {self._reservas_activas}"
        )

    def liberar_uso(self):
        """Disminuye el contador cuando se cancela una reserva."""

        # Evita que el contador tenga valores negativos.
        if self._reservas_activas <= 0:
            raise crear_error_servicio(
                OperacionNoPermitidaError,
                f"No existen reservas activas para liberar en {self.codigo}."
            )

        self._reservas_activas -= 1

        registrar_evento(
            f"Uso liberado para el servicio {self.codigo}. "
            f"Reservas activas: {self._reservas_activas}"
        )

    @property
    def reservas_activas(self):
        """Permite consultar las reservas sin modificar el contador."""
        return self._reservas_activas

    def obtener_detalles(self):
        """Implementa el método abstracto de EntidadBase."""

        estado = "Disponible" if self.disponible else "No disponible"

        return (
            f"[{self.codigo}] {self.nombre} | "
            f"${self.tarifa_base:,.2f}/h | "
            f"{estado} | "
            f"Reservas activas: {self._reservas_activas}"
        )

    def __str__(self):
        """Permite mostrar los detalles al utilizar print()."""
        return self.obtener_detalles()


# ---------------------------------------------------------------------
# SERVICIO 1: RESERVA DE SALAS
# Hereda de Servicio.
# REGLA DE NEGOCIO:
# * Capacidad entre 1 y 500 personas.
# * Duración máxima de 12 horas.
# * Recargo del 10 % cuando supera las 5 horas.
# --------------------------------------------------------------------

class ReservaSalas(Servicio):

    def __init__(self, codigo, nombre, tarifa_base, capacidad, disponible=True):

        super().__init__(codigo, nombre, tarifa_base, disponible)

        self.capacidad = capacidad

    # ---------------------------------------------------------------
    # PROPIEDAD CAPACIDAD
    # ---------------------------------------------------------------

    @property
    def capacidad(self):
        return self._capacidad

    @capacidad.setter
    def capacidad(self, valor):

        # No permite booleanos ni números decimales.
        if isinstance(valor, bool):
            raise crear_error_servicio(
                DatosInvalidosError,
                "La capacidad debe ser un número entero."
            )

        try:
            if isinstance(valor, str):
                if not valor.strip().isdigit():
                    raise ValueError("La capacidad debe ser un entero.")

                valor = int(valor.strip())

            elif not isinstance(valor, int):
                raise ValueError("La capacidad debe ser un entero.")

        except (TypeError, ValueError) as e:
            raise crear_error_servicio(
                DatosInvalidosError,
                f"Capacidad inválida: '{valor}'."
            ) from e

        if not 1 <= valor <= 500:
            raise crear_error_servicio(
                DatosInvalidosError,
                "La capacidad debe estar entre 1 y 500 personas."
            )

        self._capacidad = valor

    # ---------------------------------------------------------------
    # VALIDACIÓN DE PARÁMETROS
    # ---------------------------------------------------------------

    def validar_parametros(self, **kwargs):
        """Valida la duración permitida para reservar una sala."""

        duracion = kwargs.get("duracion")

        if isinstance(duracion, bool) or duracion is None:
            raise crear_error_servicio(
                DatosInvalidosError,
                "La duración de la reserva es obligatoria."
            )

        try:
            duracion = float(duracion)

        except (TypeError, ValueError) as e:
            raise crear_error_servicio(
                DatosInvalidosError,
                f"Duración inválida: '{duracion}'."
            ) from e

        if not math.isfinite(duracion) or duracion <= 0:
            raise crear_error_servicio(
                DatosInvalidosError,
                "La duración debe ser un número positivo y finito."
            )

        if duracion > 12:
            raise crear_error_servicio(
                OperacionNoPermitidaError,
                "Una sala no se puede reservar por más de 12 horas."
            )

        return True

    # ---------------------------------------------------------------
    # CÁLCULO DE COSTO
    # ---------------------------------------------------------------

    def calcular_costo(self, duracion, **kwargs):
        """Calcula el costo de la reserva de una sala."""

        self.validar_parametros(duracion=duracion)

        costo = self.tarifa_base * float(duracion)

        # Aplica un recargo del 10 % si supera las 5 horas.
        if float(duracion) > 5:
            costo *= 1.10

        return round(costo, 2)

    # ---------------------------------------------------------------
    # DESCRIPCIÓN DEL SERVICIO
    # ---------------------------------------------------------------

    def describir(self):
        """Devuelve información específica de la sala."""

        return (
            f"[SALA] '{self.nombre}' ({self.codigo}) | "
            f"Capacidad: {self.capacidad} personas | "
            f"Tarifa: ${self.tarifa_base:,.2f}/h"
        )


# ---------------------------------------------------------------------
# SERVICIO 2: ALQUILER DE EQUIPOS
#
# Hereda de Servicio.
# REGLA DE NEGOCIO:
# * Solo permite equipos registrados en la lista.
# * Duración máxima de 48 horas.
# * Recargo del 15 % para servidores y cámaras.
# ---------------------------------------------------------------------

class AlquilerEquipos(Servicio):

    # Conjunto de equipos permitidos por el sistema.
    TIPOS_VALIDOS = {
        "portatil",
        "proyector",
        "servidor",
        "camara",
        "impresora"
    }

    def __init__(self, codigo, nombre, tarifa_base, tipo_equipo, disponible=True):

        super().__init__(codigo, nombre, tarifa_base, disponible)

        self.tipo_equipo = tipo_equipo

    # ---------------------------------------------------------------
    # PROPIEDAD TIPO_EQUIPO
    # ---------------------------------------------------------------

    @property
    def tipo_equipo(self):
        return self._tipo_equipo

    @tipo_equipo.setter
    def tipo_equipo(self, valor):

        if not isinstance(valor, str) or valor.strip().lower() not in self.TIPOS_VALIDOS:
            raise crear_error_servicio(
                DatosInvalidosError,
                f"Tipo de equipo inválido: '{valor}'. "
                f"Permitidos: {sorted(self.TIPOS_VALIDOS)}"
            )

        self._tipo_equipo = valor.strip().lower()

    # ---------------------------------------------------------------
    # VALIDACIÓN DE PARÁMETROS
    # ---------------------------------------------------------------

    def validar_parametros(self, **kwargs):
        """Valida la duración permitida para alquilar equipos."""

        duracion = kwargs.get("duracion")

        if isinstance(duracion, bool) or duracion is None:
            raise crear_error_servicio(
                DatosInvalidosError,
                "La duración del alquiler es obligatoria."
            )

        try:
            duracion = float(duracion)

        except (TypeError, ValueError) as e:
            raise crear_error_servicio(
                DatosInvalidosError,
                f"Duración inválida: '{duracion}'."
            ) from e

        if not math.isfinite(duracion) or duracion <= 0:
            raise crear_error_servicio(
                DatosInvalidosError,
                "La duración debe ser un número positivo y finito."
            )

        if duracion > 48:
            raise crear_error_servicio(
                OperacionNoPermitidaError,
                "El alquiler no puede superar las 48 horas."
            )

        return True

    # ---------------------------------------------------------------
    # CÁLCULO DE COSTO
    # ---------------------------------------------------------------

    def calcular_costo(self, duracion, **kwargs):
        """Calcula el costo del alquiler de equipos."""

        self.validar_parametros(duracion=duracion)

        costo = self.tarifa_base * float(duracion)

        # Servidores y cámaras tienen un recargo del 15 %.
        if self.tipo_equipo in {"servidor", "camara"}:
            costo *= 1.15

        return round(costo, 2)

    # ---------------------------------------------------------------
    # DESCRIPCIÓN DEL SERVICIO
    # ---------------------------------------------------------------

    def describir(self):
        """Devuelve información específica del equipo."""

        return (
            f"[EQUIPO] '{self.nombre}' ({self.codigo}) | "
            f"Tipo: {self.tipo_equipo.capitalize()} | "
            f"Tarifa: ${self.tarifa_base:,.2f}/h"
        )


# --------------------------------------------------------------------
# SERVICIO 3: ASESORÍA ESPECIALIZADA
#
# Hereda de Servicio.
# REGLA DE NEGOCIO:
# * Solo permite áreas registradas.
# * Duración máxima de 8 horas.
# * Recargo del 20 % para asesorías de seguridad.
# ---------------------------------------------------------------------

class AsesoriaEspecializada(Servicio):

    # Áreas de asesoría permitidas.
    AREAS_VALIDAS = {
        "software",
        "redes",
        "seguridad",
        "datos",
        "gestion"
    }

    def __init__(self, codigo, nombre, tarifa_base, area, disponible=True):

        super().__init__(codigo, nombre, tarifa_base, disponible)

        self.area = area

    # ---------------------------------------------------------------
    # PROPIEDAD AREA
    # ---------------------------------------------------------------

    @property
    def area(self):
        return self._area

    @area.setter
    def area(self, valor):

        if not isinstance(valor, str) or valor.strip().lower() not in self.AREAS_VALIDAS:
            raise crear_error_servicio(
                DatosInvalidosError,
                f"Área inválida: '{valor}'. "
                f"Permitidas: {sorted(self.AREAS_VALIDAS)}"
            )

        self._area = valor.strip().lower()

    # ---------------------------------------------------------------
    # VALIDACIÓN DE PARÁMETROS
    # ---------------------------------------------------------------

    def validar_parametros(self, **kwargs):
        """Valida la duración permitida para una asesoría."""

        duracion = kwargs.get("duracion")

        if isinstance(duracion, bool) or duracion is None:
            raise crear_error_servicio(
                DatosInvalidosError,
                "La duración de la asesoría es obligatoria."
            )

        try:
            duracion = float(duracion)

        except (TypeError, ValueError) as e:
            raise crear_error_servicio(
                DatosInvalidosError,
                f"Duración inválida: '{duracion}'."
            ) from e

        if not math.isfinite(duracion) or duracion <= 0:
            raise crear_error_servicio(
                DatosInvalidosError,
                "La duración debe ser un número positivo y finito."
            )

        if duracion > 8:
            raise crear_error_servicio(
                OperacionNoPermitidaError,
                "La asesoría no puede superar las 8 horas."
            )

        return True

    # ---------------------------------------------------------------
    # CÁLCULO DE COSTO
    # ---------------------------------------------------------------

    def calcular_costo(self, duracion, **kwargs):
        """Calcula el costo de una asesoría especializada."""

        self.validar_parametros(duracion=duracion)

        costo = self.tarifa_base * float(duracion)

        # Las asesorías del área de seguridad tienen un recargo del 20 %.
        if self.area == "seguridad":
            costo *= 1.20

        return round(costo, 2)

    # ---------------------------------------------------------------
    # DESCRIPCIÓN DEL SERVICIO
    # ---------------------------------------------------------------

    def describir(self):
        """Devuelve información específica de la asesoría."""

        return (
            f"[ASESORÍA] '{self.nombre}' ({self.codigo}) | "
            f"Área: {self.area.capitalize()} | "
            f"Tarifa: ${self.tarifa_base:,.2f}/h"
        )


# ---------------------------------------------------------------------
# FIN DEL APORTE DEL ESTUDIANTE 2 JOSE DAVID PUMALPA REYES 
# ---------------------------------------------------------------------

import math


# ESTUDIANTE 3: Clase Reserva y gestión de pagos

# Excepción para los errores relacionados con las reservas
class ReservaInvalidaError(FJBaseException):
    """Se utiliza cuando una reserva no cumple las condiciones necesarias."""

    def __init__(
        self,
        mensaje="La reserva no cumple con las condiciones requeridas."
    ):
        super().__init__(mensaje)


# Clase Reserva
class Reserva(EntidadBase):

    ESTADOS_VALIDOS = {"Pendiente", "Confirmada", "Cancelada"}

    def __init__(self, codigo_reserva, cliente, servicio, duracion):

        # Comprobar que se haya recibido un cliente válido.
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError(
                "La reserva necesita un cliente válido."
            )

        # Comprobar que se haya recibido un servicio válido.
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError(
                "La reserva necesita un servicio válido."
            )

        self.codigo_reserva = codigo_reserva
        self.cliente = cliente
        self.servicio = servicio

        # La duración se valida mediante su propiedad.
        self._duracion = None
        self.duracion = duracion

        # Toda reserva comienza en estado pendiente.
        self.estado = "Pendiente"

        # El servicio también verifica que la duración sea válida.
        self.servicio.validar_parametros(
            duracion=self.duracion
        )

        registrar_evento(
            f"Reserva creada | Código: {self.codigo_reserva} | "
            f"Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | "
            f"Duración: {self.duracion} horas"
        )

    # VALIDACIÓN DEL CÓDIGO DE RESERVA

    @property
    def codigo_reserva(self):
        return self._codigo_reserva

    @codigo_reserva.setter
    def codigo_reserva(self, valor):

        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ReservaInvalidaError(
                f"Código de reserva inválido: '{valor}'. "
                "Debe tener mínimo 3 caracteres."
            )

        self._codigo_reserva = valor.strip().upper()

    # VALIDACIÓN DE LA DURACIÓN

    @property
    def duracion(self):
        return self._duracion

    @duracion.setter
    def duracion(self, valor):

        # Evita que True y False sean aceptados como números.
        if isinstance(valor, bool):
            raise ReservaInvalidaError(
                "La duración debe ser un número mayor que cero."
            )

        try:
            valor = float(valor)

        except (TypeError, ValueError, OverflowError) as error:
            raise ReservaInvalidaError(
                f"Duración inválida: '{valor}'. Se esperaba un número."
            ) from error

        # Comprueba que el número sea válido y finito.
        if not math.isfinite(valor) or valor <= 0:
            raise ReservaInvalidaError(
                "La duración debe ser un número mayor que cero."
            )

        self._duracion = valor

    # VALIDACIÓN DEL ESTADO

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, nuevo):

        if not isinstance(nuevo, str) or nuevo not in self.ESTADOS_VALIDOS:
            raise ReservaInvalidaError(
                f"Estado de reserva no válido: '{nuevo}'."
            )

        self._estado = nuevo

    # CONFIRMAR RESERVA

    def confirmar_reserva(self):
        """Confirma una reserva cuando el servicio está disponible."""

        try:
            if self.estado == "Confirmada":
                raise OperacionNoPermitidaError(
                    "Esta reserva ya se encuentra confirmada."
                )

            if self.estado == "Cancelada":
                raise OperacionNoPermitidaError(
                    "No se puede confirmar una reserva cancelada."
                )

            # Verificar que el servicio pueda utilizarse.
            self.servicio.verificar_disponibilidad()

            # Registrar el uso del servicio.
            self.servicio.registrar_uso()

            # Cambiar el estado después de completar las operaciones.
            self.estado = "Confirmada"

        except FJBaseException as error:
            registrar_error(
                f"No se pudo confirmar la reserva {self.codigo_reserva}",
                error
            )
            raise

        except Exception as error:
            registrar_error(
                f"Error inesperado al confirmar la reserva "
                f"{self.codigo_reserva}",
                error
            )
            raise

        else:
            registrar_evento(
                f"Reserva {self.codigo_reserva} confirmada correctamente."
            )
            return True

        finally:
            registrar_evento(
                f"Finalizó el intento de confirmación | "
                f"Reserva: {self.codigo_reserva} | "
                f"Estado: {self.estado}"
            )

    # CANCELAR RESERVA

    def cancelar_reserva(self):
        """Cancela la reserva y libera el servicio si estaba confirmado."""

        try:
            if self.estado == "Cancelada":
                raise OperacionNoPermitidaError(
                    "Esta reserva ya se encuentra cancelada."
                )

            # Si estaba confirmada, se libera el servicio.
            if self.estado == "Confirmada":
                self.servicio.liberar_uso()

            self.estado = "Cancelada"

        except FJBaseException as error:
            registrar_error(
                f"No se pudo cancelar la reserva {self.codigo_reserva}",
                error
            )
            raise

        except Exception as error:
            registrar_error(
                f"Error inesperado al cancelar la reserva "
                f"{self.codigo_reserva}",
                error
            )
            raise

        else:
            registrar_evento(
                f"Reserva {self.codigo_reserva} cancelada correctamente."
            )
            return True

        finally:
            registrar_evento(
                f"Finalizó el intento de cancelación | "
                f"Reserva: {self.codigo_reserva} | "
                f"Estado: {self.estado}"
            )

    # PROCESAR PAGO

    def procesar_pago(self, descuento=0.0, aplicar_impuesto=True):
        """
        Calcula el valor de una reserva.

        Ejemplos:
        procesar_pago()
        procesar_pago(descuento=0.10)
        procesar_pago(aplicar_impuesto=False)
        procesar_pago(0.10, False)

        El descuento se expresa como decimal:
        0.10 equivale al 10 %.
        """

        try:
            # Solo se permite pagar una reserva confirmada.
            if self.estado != "Confirmada":
                raise OperacionNoPermitidaError(
                    "Solo se pueden procesar pagos de reservas confirmadas."
                )

            # Validar el descuento.
            if isinstance(descuento, bool):
                raise DatosInvalidosError(
                    "El descuento debe ser un número entre 0 y 1."
                )

            if not isinstance(descuento, (int, float)):
                raise DatosInvalidosError(
                    "El descuento debe ser un valor numérico."
                )

            descuento = float(descuento)

            if not math.isfinite(descuento) or not 0 <= descuento <= 1:
                raise DatosInvalidosError(
                    "El descuento debe estar entre 0.0 y 1.0."
                )

            # Validar la opción de impuesto.
            if not isinstance(aplicar_impuesto, bool):
                raise DatosInvalidosError(
                    "La opción de aplicar impuesto debe ser True o False."
                )

            # Obtener el costo calculado por el servicio.
            costo_base = self.servicio.calcular_costo(
                duracion=self.duracion
            )

            if (
                isinstance(costo_base, bool)
                or not isinstance(costo_base, (int, float))
                or not math.isfinite(float(costo_base))
                or costo_base < 0
            ):
                raise CalculoInconsistenteError(
                    "El servicio devolvió un costo base inválido."
                )

            costo_base = float(costo_base)

            # Aplicar el descuento.
            costo_con_descuento = costo_base * (1 - descuento)

            # Aplicar IVA del 19 % cuando corresponda.
            impuestos = 0.0

            if aplicar_impuesto:
                impuestos = costo_con_descuento * 0.19

            total_final = round(
                costo_con_descuento + impuestos,
                2
            )

        except FJBaseException as error:
            registrar_error(
                f"Error al procesar el pago de la reserva "
                f"{self.codigo_reserva}",
                error
            )
            raise

        except Exception as error:
            registrar_error(
                f"Error inesperado al procesar el pago de la reserva "
                f"{self.codigo_reserva}",
                error
            )

            raise CalculoInconsistenteError(
                "No fue posible completar el cálculo del pago."
            ) from error

        else:
            registrar_evento(
                f"Pago calculado | Reserva: {self.codigo_reserva} | "
                f"Total: ${total_final:,.2f}"
            )

            return total_final

        finally:
            registrar_evento(
                f"Finalizó el intento de pago | "
                f"Reserva: {self.codigo_reserva} | "
                f"Estado: {self.estado}"
            )

    # DETALLES DE LA RESERVA

    def obtener_detalles(self):
        """Muestra la información principal de la reserva."""

        return (
            f"Reserva [Código: {self.codigo_reserva} | "
            f"Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | "
            f"Duración: {self.duracion} horas | "
            f"Estado: {self.estado}]"
        )

    def __str__(self):
        return self.obtener_detalles()



# FIN DEL APORTE DEL ESTUDIANTE 3


# ---------------------------------------------------------------------
#   ESTUDIANTE 4: JOSE DAVID PUMALPA REYES
#   Metodos sobrecargados para el calculo de costos
#   - Simula sobrecarga con parametros opcionales, *args y **kwargs.
#   - Variantes: costo base, con impuesto, con descuento y costo total.
#   - Se integra con el polimorfismo del Estudiante 2 y la Reserva del 3.
# ---------------------------------------------------------------------
# EXCEPCION PERSONALIZADA
# ---------------------------------------------------------------------
class ParametroCostoInvalidoError(FJBaseException):
    """Se lanza cuando un parámetro de costo es inválido."""

    def __init__(self, mensaje="Parámetro de costo inválido."):
        super().__init__(mensaje)
# ---------------------------------------------------------------------
# CLASE UTILITARIA: CalculadoraCostos
# Métodos SOBRECARGADOS simulados.
# ---------------------------------------------------------------------
class CalculadoraCostos:
    """
    Calculadora de costos con métodos sobrecargados simulados.

    En Python no existe sobrecarga tradicional de métodos.
    Por eso se utilizan:
      - Parámetros con valores por defecto.
      - *args para recibir argumentos posicionales.
      - **kwargs para recibir argumentos nombrados.
      - Métodos complementarios con diferentes funcionalidades.
    """

    # IVA por defecto en Colombia
    IVA_DEFAULT = 0.19

    # ---------- MÉTODO SOBRECARGADO PRINCIPAL ----------
    @staticmethod
    def calcular(duracion, tarifa_base, *args, **kwargs):
        """
        Permite diferentes variantes de cálculo:

        Variante 1:
            calcular(duracion, tarifa_base)

        Variante 2:
            calcular(duracion, tarifa_base, impuesto)

        Variante 3:
            calcular(duracion, tarifa_base, impuesto, descuento)

        Variante 4:
            calcular(duracion, tarifa_base,
                     impuesto=0.19, descuento=0.10, recargo=0.05)
        """

        # --- Validación de duración y tarifa ---
        try:
            duracion = float(duracion)
            tarifa_base = float(tarifa_base)
        except (TypeError, ValueError) as e:
            raise ParametroCostoInvalidoError(
                "La duración y la tarifa base deben ser numéricas."
            ) from e

        if not math.isfinite(duracion) or duracion <= 0:
            raise ParametroCostoInvalidoError(
                "La duración debe ser un número válido mayor a cero."
            )

        if not math.isfinite(tarifa_base) or tarifa_base <= 0:
            raise ParametroCostoInvalidoError(
                "La tarifa base debe ser un número válido mayor a cero."
            )

        # --- Validación de argumentos posicionales ---
        nombres = ("impuesto", "descuento", "recargo")

        if len(args) > 3:
            raise ParametroCostoInvalidoError(
                "Se recibieron demasiados argumentos posicionales."
            )

        # Verificar que no existan parámetros desconocidos
        for nombre in kwargs:
            if nombre not in nombres:
                raise ParametroCostoInvalidoError(
                    f"Parámetro desconocido: '{nombre}'."
                )

        # Evitar que un parámetro se envíe dos veces
        for i, nombre in enumerate(nombres[:len(args)]):
            if nombre in kwargs:
                raise ParametroCostoInvalidoError(
                    f"El parámetro '{nombre}' fue enviado dos veces."
                )

        # --- Resolución de parámetros ---
        impuesto = kwargs.get(
            "impuesto", args[0] if len(args) >= 1 else 0.0
        )

        descuento = kwargs.get(
            "descuento", args[1] if len(args) >= 2 else 0.0
        )

        recargo = kwargs.get(
            "recargo", args[2] if len(args) >= 3 else 0.0
        )

        # --- Conversión y validación de porcentajes ---
        try:
            impuesto = float(impuesto)
            descuento = float(descuento)
            recargo = float(recargo)
        except (TypeError, ValueError) as e:
            raise ParametroCostoInvalidoError(
                "Los porcentajes deben ser valores numéricos."
            ) from e

        for nombre, valor in (
            ("impuesto", impuesto),
            ("descuento", descuento),
            ("recargo", recargo)
        ):
            if not math.isfinite(valor) or not 0 <= valor <= 1:
                raise ParametroCostoInvalidoError(
                    f"El {nombre} debe estar entre 0 y 1 "
                    f"(ejemplo: 0.19 = 19 %). Recibido: {valor}"
                )

        # --- Cálculo final ---
        costo_base = duracion * tarifa_base

        costo_con_recargo = costo_base * (1 + recargo)

        costo_con_impuesto = costo_con_recargo * (1 + impuesto)

        costo_final = costo_con_impuesto * (1 - descuento)

        if not math.isfinite(costo_final) or costo_final < 0:
            raise CalculoInconsistenteError(
                f"El costo final resultó inválido: {costo_final}"
            )

        return round(costo_final, 2)

    # -----------------------------------------------------------------
    # MÉTODOS COMPLEMENTARIOS
    # -----------------------------------------------------------------

    @staticmethod
    def calcular_base(duracion, tarifa_base):
        """Calcula únicamente duración por tarifa."""

        return CalculadoraCostos.calcular(
            duracion, tarifa_base
        )

    @staticmethod
    def calcular_con_impuesto(duracion, tarifa_base, impuesto=None):
        """Calcula el costo aplicando un impuesto."""

        if impuesto is None:
            impuesto = CalculadoraCostos.IVA_DEFAULT

        return CalculadoraCostos.calcular(
            duracion, tarifa_base, impuesto=impuesto
        )

    @staticmethod
    def calcular_con_descuento(duracion, tarifa_base, descuento):
        """Calcula el costo aplicando únicamente un descuento."""

        return CalculadoraCostos.calcular(
            duracion, tarifa_base, descuento=descuento
        )

    @staticmethod
    def calcular_total(
        duracion, tarifa_base, impuesto=None,
        descuento=0.0, recargo=0.0
    ):
        """
        Calcula el costo completo aplicando impuesto,
        descuento y recargo.
        """

        if impuesto is None:
            impuesto = CalculadoraCostos.IVA_DEFAULT

        return CalculadoraCostos.calcular(
            duracion,
            tarifa_base,
            impuesto=impuesto,
            descuento=descuento,
            recargo=recargo
        )

    # -----------------------------------------------------------------
    # VARIANTE PARA SERVICIOS (POLIMORFISMO)
    # -----------------------------------------------------------------

    @staticmethod
    def calcular_para_servicio(
        servicio, duracion, impuesto=None,
        descuento=0.0, recargo=0.0
    ):
        """
        Recibe un objeto Servicio y utiliza su método polimórfico
        calcular_costo() para obtener el costo base.

        Después aplica los impuestos, descuentos y recargos.

        Ejemplos:

            calcular_para_servicio(sala, 4)

            calcular_para_servicio(
                sala, 4, impuesto=0.19
            )

            calcular_para_servicio(
                sala, 4, impuesto=0.19,
                descuento=0.05, recargo=0.10
            )
        """

        if not isinstance(servicio, Servicio):
            raise ParametroCostoInvalidoError(
                "Se requiere un objeto Servicio válido."
            )

        # Validar duracion antes de utilizarla
        try:
            duracion = float(duracion)
        except (TypeError, ValueError) as e:
            raise ParametroCostoInvalidoError(
                "La duracion debe ser numerica."
            ) from e

        if not math.isfinite(duracion) or duracion <= 0:
            raise ParametroCostoInvalidoError(
                "La duracion debe ser mayor a cero."
            )

        # Obtener el costo base mediante polimorfismo
        costo_base = servicio.calcular_costo(
            duracion=duracion
        )

        try:
            costo_base = float(costo_base)
        except (TypeError, ValueError) as e:
            raise CalculoInconsistenteError(
                "El servicio devolvió un costo base invalido."
            ) from e

        if not math.isfinite(costo_base) or costo_base <= 0:
            raise CalculoInconsistenteError(
                "El costo base del servicio debe ser valido y mayor a cero."
            )

        # Obtener la tarifa efectiva del servicio
        tarifa_efectiva = costo_base / duracion

        # Aplicar IVA predeterminado cuando no se especifica
        if impuesto is None:
            impuesto = CalculadoraCostos.IVA_DEFAULT

        # Reutilizar el método principal de cálculo
        return CalculadoraCostos.calcular(
            duracion,
            tarifa_efectiva,
            impuesto=impuesto,
            descuento=descuento,
            recargo=recargo
        )


# ---------------------------------------------------------------------
# EXTENSION DE RESERVA CON CALCULO DE COSTOS EXTRA
# Se agrega un metodo adicional sin modificar la clase original.
# ---------------------------------------------------------------------

def procesar_pago_con_costos_extra(
    self, impuesto=None, descuento=0.0, recargo=0.0
):
    """
    Procesa el calculo de pago de una reserva utilizando
    la CalculadoraCostos.

    - Aplica IVA del 19 % por defecto.
    - Permite aplicar descuentos.
    - Permite aplicar recargos.
    - Solo funciona con reservas Confirmadas.

    Ejemplos:

        reserva.procesar_pago_con_costos_extra()

        reserva.procesar_pago_con_costos_extra(
            impuesto=0.16
        )

        reserva.procesar_pago_con_costos_extra(
            descuento=0.10
        )

        reserva.procesar_pago_con_costos_extra(
            impuesto=0.19,
            descuento=0.05,
            recargo=0.10
        )
    """

    try:
        # Verificar que la reserva este confirmada
        if self.estado != "Confirmada":
            raise OperacionNoPermitidaError(
                "Solo se procesan pagos de reservas Confirmadas. "
                f"Estado actual: '{self.estado}'."
            )

        # La reserva ya fue verificada y el servicio registrado
        # durante confirmar_reserva() del Estudiante 3.
        # Por eso no se vuelve a verificar disponibilidad aqui.

        # Calcular el costo utilizando la calculadora
        total = CalculadoraCostos.calcular_para_servicio(
            self.servicio,
            self.duracion,
            impuesto=impuesto,
            descuento=descuento,
            recargo=recargo
        )

    except Exception as e:
        registrar_error(
            f"Fallo al procesar pago con extras de reserva "
            f"{self.codigo_reserva}",
            e
        )
        raise

    else:
        registrar_evento(
            f"Pago con extras procesado | "
            f"Reserva: {self.codigo_reserva} | "
            f"Cliente: {self.cliente.nombre} | "
            f"Total: ${total:,.2f}"
        )

        return total

    finally:
        registrar_evento(
            f"Intento de pago con extras finalizado | "
            f"Reserva: {self.codigo_reserva} | "
            f"Estado: {self.estado}"
        )


# ---------------------------------------------------------------------
# INCORPORACION DEL MOTODO A LA CLASE RESERVA
# Se conserva la implementacion original del Estudiante 3.
# ---------------------------------------------------------------------

Reserva.procesar_pago_con_costos_extra = (
    procesar_pago_con_costos_extra
)


# ---------------------------------------------------------------------
# FIN DE LA PARTE DEL ESTUDIANTE 4: JOSE DAVID PUMALPA REYES
# ---------------------------------------------------------------------
# ----------------------------------------------------------------
# ESTUDIANTE 5:JOSE DAVID PUMALPA REYES
#Simulación y pruebas de integración
# -----------------------------------------------------------------------


# ---------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------

def banner(titulo, numero=None):
    """Muestra el título de cada operación."""
    linea = "=" * 70
    prefijo = f"[OPERACIÓN {numero:02d}] " if numero is not None else ""

    print(f"\n{linea}")
    print(f"{prefijo}{titulo}")
    print(linea)


def resumen_operacion(resultado, exito):
    """Muestra el resultado de una operación."""
    marca = "ÉXITO" if exito else "FALLO CONTROLADO"

    print(f"  Resultado: {marca}")
    print(f"  Detalle: {resultado}")


def registrar_error_simulacion(mensaje, error=None):
    """
    Registra un error sin detener la simulación.

    Se intenta utilizar la función de registro del sistema.
    """
    try:
        if error is not None:
            registrar_error(mensaje, error)
        else:
            registrar_error(mensaje)

    except TypeError:
        # Compatibilidad si registrar_error solo recibe un argumento.
        try:
            registrar_error(mensaje)
        except Exception:
            print(f"  No fue posible registrar el error: {mensaje}")

    except Exception:
        print(f"  No fue posible registrar el error: {mensaje}")


def verificar_logs():
    """Lee el archivo de registros y muestra un pequeño resumen."""

    print("\n" + "=" * 70)
    print("VERIFICACIÓN DEL ARCHIVO DE LOGS")
    print("=" * 70)

    ruta_log = "logs/sistema_fj.log"

    try:
        with open(ruta_log, "r", encoding="utf-8", errors="replace") as archivo:
            lineas = archivo.readlines()

        total = len(lineas)
        errores = sum(1 for linea in lineas if "[ERROR]" in linea)
        infos = sum(1 for linea in lineas if "[INFO]" in linea)

        print(f"  Archivo: {ruta_log}")
        print(f"  Total de líneas: {total}")
        print(f"  Eventos INFO: {infos}")
        print(f"  Eventos ERROR: {errores}")

        print("\n  Últimas 5 líneas del archivo:")
        print("  " + "-" * 60)

        for linea in lineas[-5:]:
            print(f"  {linea.rstrip()}")

        print("  " + "-" * 60)

        return True

    except FileNotFoundError:
        print(f"  No se encontró el archivo: {ruta_log}")
        print("  Comprueba que el sistema haya generado los registros.")
        return False

    except OSError as error:
        print(f"  No se pudo leer el archivo de logs: {error}")
        return False


# ---------------------------------------------------------------------
# Función para ejecutar y controlar cada operación
# ---------------------------------------------------------------------

def ejecutar_operacion(numero, titulo, accion, resultados,
                       debe_fallar=False, excepciones_esperadas=()):
    """
    Ejecuta una operación de forma independiente.

    Si una prueba falla, las demás pueden continuar.
    También permite comprobar que las operaciones inválidas
    generen las excepciones correspondientes.
    """

    banner(titulo, numero)

    try:
        detalle = accion()

    except excepciones_esperadas as error:
        if debe_fallar:
            resumen_operacion(str(error), False)
            resultados["controlados"] += 1
            registrar_error_simulacion(
                f"Operación {numero}: error esperado", error
            )
        else:
            resumen_operacion(
                f"Se presentó un error inesperado: {error}", False
            )
            resultados["fallidos"] += 1
            registrar_error_simulacion(
                f"Operación {numero}: error inesperado", error
            )

    except Exception as error:
        resumen_operacion(
            f"Error durante la operación: {error}", False
        )
        resultados["fallidos"] += 1
        registrar_error_simulacion(
            f"Operación {numero}: error no previsto", error
        )

    else:
        if debe_fallar:
            resumen_operacion(
                "La operación fue aceptada, pero debía generar un error.",
                False
            )
            resultados["fallidos"] += 1
            registrar_error_simulacion(
                f"Operación {numero}: no se rechazaron los datos inválidos"
            )
        else:
            resumen_operacion(detalle, True)
            resultados["exitosos"] += 1

    finally:
        # Se ejecuta al terminar cada operación, haya salido bien o mal.
        print("-" * 70)


# ---------------------------------------------------------------------
# SIMULACIÓN PRINCIPAL
# ---------------------------------------------------------------------

def ejecutar_simulacion():

    print("\n" + "#" * 70)
    print("#       SOFTWARE FJ - SIMULACIÓN DEL SISTEMA")
    print("#" * 70)

    resultados = {
        "exitosos": 0,
        "controlados": 0,
        "fallidos": 0
    }

    # Estas listas representan los registros que se van creando.
    clientes_registrados = []
    servicios_registrados = []
    reservas_registradas = []

    # Variables para conservar los objetos creados.
    cliente1 = None
    sala1 = None
    asesoria1 = None

    # ---------------------------------------------------------------
    # Funciones de las operaciones
    # ---------------------------------------------------------------

    def obtener_cliente():
        if cliente1 is None:
            raise RuntimeError(
                "No hay un cliente válido para realizar la reserva."
            )
        return cliente1

    def obtener_sala():
        if sala1 is None:
            raise RuntimeError(
                "No se pudo crear la sala para realizar la reserva."
            )
        return sala1

    def obtener_asesoria():
        if asesoria1 is None:
            raise RuntimeError(
                "No se pudo crear la asesoría especializada."
            )
        return asesoria1

    # OP 01: Registrar cliente válido.
    def op_01():
        nonlocal cliente1

        cliente1 = Cliente(
            "11223344",
            "Hoover García",
            "hoover@mail.com",
            "3504919193"
        )

        clientes_registrados.append(cliente1)

        registrar_evento(
            f"Cliente registrado: {cliente1.nombre}"
        )

        return cliente1.obtener_detalles()

    # OP 02: Registrar cliente con cédula inválida.
    def op_02():
        cliente_malo = Cliente(
            "123",
            "Prueba Error",
            "error@mail.com",
            "3000000000"
        )

        clientes_registrados.append(cliente_malo)

        return "El cliente inválido fue registrado."

    # OP 03: Registrar cliente con correo inválido.
    def op_03():
        cliente_malo = Cliente(
            "99887766",
            "Correo Malo",
            "correo-invalido",
            "3001112233"
        )

        clientes_registrados.append(cliente_malo)

        return "El cliente con correo inválido fue registrado."

    # OP 04: Crear una sala válida.
    def op_04():
        nonlocal sala1

        sala1 = ReservaSalas(
            "SAL-01",
            "Sala Ejecutiva",
            50000,
            12
        )

        servicios_registrados.append(sala1)

        registrar_evento(
            f"Servicio creado: {sala1.nombre}"
        )

        return sala1.describir()

    # OP 05: Crear un equipo válido.
    def op_05():
        proyector = AlquilerEquipos(
            "EQP-01",
            "Proyector 4K",
            20000,
            "proyector"
        )

        servicios_registrados.append(proyector)

        registrar_evento(
            f"Servicio creado: {proyector.nombre}"
        )

        return proyector.describir()

    # OP 06: Crear un servicio con tarifa negativa.
    def op_06():
        servicio_malo = ReservaSalas(
            "SAL-99",
            "Sala Fantasma",
            -1000,
            10
        )

        servicios_registrados.append(servicio_malo)

        return "El servicio con tarifa negativa fue creado."

    # OP 07: Crear una asesoría especializada válida.
    def op_07():
        nonlocal asesoria1

        asesoria1 = AsesoriaEspecializada(
            "ASE-01",
            "Auditoría de seguridad",
            80000,
            "seguridad"
        )

        servicios_registrados.append(asesoria1)

        registrar_evento(
            f"Servicio creado: {asesoria1.nombre}"
        )

        return asesoria1.describir()

    # OP 08: Crear, confirmar y pagar una reserva.
    def op_08():
        reserva_ok = Reserva(
            "R-001",
            obtener_cliente(),
            obtener_sala(),
            4
        )

        reserva_ok.confirmar_reserva()

        total = reserva_ok.procesar_pago(
            descuento=0.0,
            aplicar_impuesto=True
        )

        reservas_registradas.append(reserva_ok)

        return (
            f"Estado: {reserva_ok.estado} | "
            f"Total: ${total:,.2f}"
        )

    # OP 09: Intentar reservar un servicio no disponible.
    def op_09():
        sala_off = ReservaSalas(
            "SAL-02",
            "Sala Cerrada",
            40000,
            10,
            disponible=False
        )

        reserva_fallida = Reserva(
            "R-002",
            obtener_cliente(),
            sala_off,
            2
        )

        reserva_fallida.confirmar_reserva()

        return "La reserva fue confirmada aunque el servicio no estaba disponible."

    # OP 10: Procesar una reserva con costos adicionales.
    def op_10():
        reserva_extra = Reserva(
            "R-003",
            obtener_cliente(),
            obtener_asesoria(),
            3
        )

        reserva_extra.confirmar_reserva()

        if not callable(
            getattr(reserva_extra, "procesar_pago_con_costos_extra", None)
        ):
            raise RuntimeError(
                "No está disponible el método de costos adicionales "
                "del Estudiante 4."
            )

        total = reserva_extra.procesar_pago_con_costos_extra(
            impuesto=0.19,
            descuento=0.05
        )

        reservas_registradas.append(reserva_extra)

        return (
            f"Estado: {reserva_extra.estado} | "
            f"Total con IVA y descuento: ${total:,.2f}"
        )

    # OP 11: Intentar crear una reserva con duración inválida.
    def op_11():
        reserva_mala = Reserva(
            "R-004",
            obtener_cliente(),
            obtener_sala(),
            -5
        )

        return "La reserva con duración negativa fue creada."

    # OP 12: Confirmar y cancelar una reserva.
    def op_12():
        reserva_cancel = Reserva(
            "R-005",
            obtener_cliente(),
            obtener_sala(),
            2
        )

        reserva_cancel.confirmar_reserva()
        reserva_cancel.cancelar_reserva()

        return f"Estado final de la reserva: {reserva_cancel.estado}"

    # OP 13: Intentar crear una reserva con código inválido.
    def op_13():
        reserva_cod_malo = Reserva(
            "AB",
            obtener_cliente(),
            obtener_sala(),
            2
        )

        return "La reserva con código inválido fue creada."

    # ---------------------------------------------------------------
    # Ejecución de las operaciones
    # ---------------------------------------------------------------

    ejecutar_operacion(
        1, "Registrar cliente válido",
        op_01, resultados
    )

    ejecutar_operacion(
        2, "Registrar cliente con cédula inválida",
        op_02, resultados,
        debe_fallar=True,
        excepciones_esperadas=(DatosInvalidosError,)
    )

    ejecutar_operacion(
        3, "Registrar cliente con correo inválido",
        op_03, resultados,
        debe_fallar=True,
        excepciones_esperadas=(DatosInvalidosError,)
    )

    ejecutar_operacion(
        4, "Crear servicio de sala válido",
        op_04, resultados
    )

    ejecutar_operacion(
        5, "Crear servicio de equipo válido",
        op_05, resultados
    )

    ejecutar_operacion(
        6, "Crear servicio con tarifa negativa",
        op_06, resultados,
        debe_fallar=True,
        excepciones_esperadas=(DatosInvalidosError,)
    )

    ejecutar_operacion(
        7, "Crear asesoría especializada válida",
        op_07, resultados
    )

    ejecutar_operacion(
        8, "Crear, confirmar y pagar una reserva",
        op_08, resultados
    )

    ejecutar_operacion(
        9, "Intentar reservar un servicio no disponible",
        op_09, resultados,
        debe_fallar=True,
        excepciones_esperadas=(ServicioNoDisponibleError,)
    )

    ejecutar_operacion(
        10, "Procesar una reserva con IVA y descuento",
        op_10, resultados
    )

    ejecutar_operacion(
        11, "Intentar crear una reserva con duración inválida",
        op_11, resultados,
        debe_fallar=True,
        excepciones_esperadas=(ReservaInvalidaError,)
    )

    ejecutar_operacion(
        12, "Confirmar y cancelar una reserva",
        op_12, resultados
    )

    ejecutar_operacion(
        13, "Intentar crear una reserva con código inválido",
        op_13, resultados,
        debe_fallar=True,
        excepciones_esperadas=(ReservaInvalidaError,)
    )

    # ---------------------------------------------------------------
    # Reporte final
    # ---------------------------------------------------------------

    total_operaciones = (
        resultados["exitosos"]
        + resultados["controlados"]
        + resultados["fallidos"]
    )

    print("\n" + "#" * 70)
    print("#             REPORTE FINAL DE LA SIMULACIÓN")
    print("#" * 70)

    print(f"  Clientes registrados:  {len(clientes_registrados)}")
    print(f"  Servicios registrados: {len(servicios_registrados)}")
    print(f"  Reservas registradas:  {len(reservas_registradas)}")

    print(f"  Operaciones exitosas:  {resultados['exitosos']}")
    print(f"  Errores controlados:   {resultados['controlados']}")
    print(f"  Fallos inesperados:    {resultados['fallidos']}")
    print(f"  Total de operaciones:  {total_operaciones}")

    if resultados["fallidos"] == 0:
        print("\n  La simulación terminó sin fallos inesperados.")
    else:
        print("\n  Se presentaron fallos que deben revisarse.")

    # Revisar el archivo de registros.
    verificar_logs()

    print("\n" + "#" * 70)
    print("#             FIN DE LA SIMULACIÓN")
    print("#" * 70 + "\n")


# ---------------------------------------------------------------------
# PUNTO DE ENTRADA
# ---------------------------------------------------------------------

if __name__ == "__main__":

    try:
        ejecutar_simulacion()

    except Exception as error:
        # Última protección para evitar que un error general
        # pase desapercibido.
        registrar_error_simulacion(
            "Error crítico durante la simulación", error
        )

        print("\nSe presentó un error general en la simulación.")
        print(f"Detalle: {error}")
        print("Revisa el archivo de registros para encontrar más información.")


# ---------------------------------------------------------------------
# FIN DE LA PARTE DEL ESTUDIANTE 5
# ---------------------------------------------------------------------
