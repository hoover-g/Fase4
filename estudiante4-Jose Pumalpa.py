
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
