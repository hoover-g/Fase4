import logging
import os
from abc import ABC, abstractmethod
import math

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
