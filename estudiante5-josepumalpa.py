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
