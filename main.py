"""
main.py — Software FJ: Sistema Integral de Gestión
Este archivo ejecuta 10 operaciones completas para demostrar
que el sistema funciona correctamente con casos válidos e inválidos.
"""

# importamos todas las clases que necesitamos
from cliente import Cliente
from sala import ReservaSala
from equipo import AlquilerEquipo
from asesoria import AsesoriaEspecializada
from reserva import Reserva, GestorReservas
from excepciones import (
    SoftwareFJError, ClienteError, ValidacionError,
    ServicioError, ServicioNoDisponibleError,
    ReservaError, ReservaYaCanceladaError, DuracionInvalidaError
)
from logger import logger


def separador(titulo: str):
    """Imprime un separador visual para organizar la salida en consola."""
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print('='*60)


def imprimir_resultado(ok: bool, descripcion: str):
    """Imprime ✓ si la operación fue exitosa o ✗ si falló."""
    marca = "✓" if ok else "✗"
    print(f"  [{marca}] {descripcion}")


# ─────────────────────────────────────────────────────────────────
# Creamos el catálogo de servicios disponibles en el sistema
# ─────────────────────────────────────────────────────────────────

def crear_catalogo():
    """Inicializa todos los servicios disponibles en Software FJ."""
    servicios = {}
    try:
        # creamos dos salas con diferentes características
        servicios["S1"] = ReservaSala("S1", "Sala Ejecutiva A", 80_000, capacidad=10, tiene_proyector=True)
        servicios["S2"] = ReservaSala("S2", "Sala de Conferencias", 120_000, capacidad=30, tiene_proyector=True)
        # creamos dos equipos de tipos diferentes
        servicios["E1"] = AlquilerEquipo("E1", "Laptop HP ProBook", 25_000, "laptop", unidades_disponibles=5)
        servicios["E2"] = AlquilerEquipo("E2", "Servidor Dell", 150_000, "servidor", unidades_disponibles=2)
        # creamos dos asesorías especializadas
        servicios["A1"] = AsesoriaEspecializada("A1", "Asesoría en Ciberseguridad", 200_000, "seguridad", "Ing. García")
        servicios["A2"] = AsesoriaEspecializada("A2", "Asesoría en Datos", 180_000, "datos", "Ing. Rodríguez")
        logger.info("Catálogo de servicios cargado exitosamente.")
    except ServicioError as e:
        logger.error("Error al crear catálogo.", e)
    return servicios


# ─────────────────────────────────────────────────────────────────
# OPERACIÓN 1: Registro de clientes con datos válidos
# ─────────────────────────────────────────────────────────────────

def op1_registro_clientes_validos():
    separador("OP 1 — Registro de clientes válidos")
    clientes = {}
    # lista de clientes que deberían crearse sin problema
    datos = [
        ("C001", "Ana Torres",   "ana.torres@mail.com",   "+57 310 1234567"),
        ("C002", "Luis Gómez",   "lgomez@empresa.co",     "3209876543"),
        ("C003", "María Pérez",  "mperez@gmail.com",      "+57 321 9876543"),
    ]
    for id_, nombre, correo, tel in datos:
        try:
            c = Cliente(id_, nombre, correo, tel)
            clientes[id_] = c  # guardamos el cliente en el diccionario
            imprimir_resultado(True, f"Cliente registrado: {c}")
        except (ClienteError, ValidacionError) as e:
            imprimir_resultado(False, f"Error en {id_}: {e}")
    return clientes


# ─────────────────────────────────────────────────────────────────
# OPERACIÓN 2: Registro de clientes con datos inválidos
# Demostramos que el sistema rechaza datos incorrectos
# ─────────────────────────────────────────────────────────────────

def op2_registro_clientes_invalidos():
    separador("OP 2 — Registro de clientes con datos inválidos")
    casos_invalidos = [
        ("C004", "Pedro Ruiz",  "correo-invalido", "312abc"),    # correo y teléfono inválidos
        ("C005", "",            "vacio@mail.com",  "3001234567"), # nombre vacío
        ("C006", "Rosa Vargas", "rosa@mail.com",   "12"),         # teléfono muy corto
    ]
    for id_, nombre, correo, tel in casos_invalidos:
        try:
            c = Cliente(id_, nombre, correo, tel)
            imprimir_resultado(False, f"DEBIÓ FALLAR pero se creó: {c}")
        except ValidacionError as e:
            imprimir_resultado(True, f"Validación correcta: {e}")
        except (ClienteError, ValueError) as e:
            imprimir_resultado(True, f"Error capturado: {e}")


# ─────────────────────────────────────────────────────────────────
# OPERACIÓN 3: Descripción de servicios (polimorfismo)
# Cada servicio implementa describir() y calcular_costo() a su manera
# ─────────────────────────────────────────────────────────────────

def op3_describir_servicios(servicios: dict):
    separador("OP 3 — Descripción polimórfica de servicios")
    for srv in servicios.values():
        print(f"\n{srv.describir()}")
        # calculamos el costo con y sin descuento para ver la diferencia
        costo_2h = srv.calcular_costo(2, descuento=0, incluir_iva=True)
        costo_2h_desc = srv.calcular_costo(2, descuento=15, incluir_iva=True)
        print(f"  Costo 2h (sin desc.)  : ${costo_2h:>12,.2f}")
        print(f"  Costo 2h (desc. 15%) : ${costo_2h_desc:>12,.2f}")


# ─────────────────────────────────────────────────────────────────
# OPERACIÓN 4: Creación de servicios con parámetros inválidos
# Demostramos que el sistema valida bien los datos de los servicios
# ─────────────────────────────────────────────────────────────────

def op4_servicios_invalidos():
    separador("OP 4 — Creación de servicios con parámetros inválidos")

    # intentamos crear una sala con capacidad 0 (inválido)
    try:
        s = ReservaSala("S_ERR1", "Sala fantasma", 50_000, capacidad=0)
        imprimir_resultado(False, f"DEBIÓ FALLAR: {s}")
    except ServicioError as e:
        imprimir_resultado(True, f"Sala inválida detectada: {e}")

    # intentamos crear un equipo con tipo no reconocido
    try:
        e = AlquilerEquipo("E_ERR1", "Equipo raro", 10_000, "dron")
        imprimir_resultado(False, f"DEBIÓ FALLAR: {e}")
    except ServicioError as e:
        imprimir_resultado(True, f"Tipo equipo inválido detectado: {e}")

    # intentamos crear una asesoría con especialidad que no existe
    try:
        a = AsesoriaEspecializada("A_ERR1", "Asesoría mágica", 300_000, "magia", "Hechicero")
        imprimir_resultado(False, f"DEBIÓ FALLAR: {a}")
    except ServicioError as e:
        imprimir_resultado(True, f"Especialidad inválida detectada: {e}")

    # intentamos crear un servicio con precio negativo
    try:
        s2 = ReservaSala("S_ERR2", "Sala gratis", -1, capacidad=5)
        imprimir_resultado(False, f"DEBIÓ FALLAR: {s2}")
    except ServicioError as e:
        imprimir_resultado(True, f"Precio inválido detectado: {e}")


# ─────────────────────────────────────────────────────────────────
# OPERACIÓN 5: Creación y confirmación de reservas válidas
# ─────────────────────────────────────────────────────────────────

def op5_reservas_exitosas(clientes: dict, servicios: dict, gestor: GestorReservas):
    separador("OP 5 — Reservas exitosas")

    # cada tupla es: (id_reserva, id_cliente, id_servicio, horas, descuento, incluir_iva)
    casos = [
        ("R001", "C001", "S1", 3.0, 0.0,  True),   # sala con iva, sin descuento
        ("R002", "C002", "E1", 2.0, 10.0, True),   # equipo con 10% de descuento
        ("R003", "C003", "A1", 5.0, 0.0,  False),  # asesoría sin IVA
    ]

    reservas_ok = {}
    for id_r, id_c, id_s, horas, desc, iva in casos:
        try:
            r = Reserva(id_r, clientes[id_c], servicios[id_s], horas, desc, iva)
            r.confirmar()       # confirmamos la reserva y calculamos el costo
            gestor.agregar(r)   # la agregamos al gestor para llevar el registro
            reservas_ok[id_r] = r
            imprimir_resultado(True, f"{r} — Costo: ${r.costo_total:,.2f}")
        except SoftwareFJError as e:
            imprimir_resultado(False, f"Error en {id_r}: {e}")

    return reservas_ok


# ─────────────────────────────────────────────────────────────────
# OPERACIÓN 6: Reservas que deben fallar
# Demostramos el manejo de errores en casos inválidos
# ─────────────────────────────────────────────────────────────────

def op6_reservas_fallidas(clientes: dict, servicios: dict):
    separador("OP 6 — Reservas con errores")

    # caso 1: servicio deshabilitado
    try:
        servicios["S2"].deshabilitar()  # deshabilitamos el servicio temporalmente
        r = Reserva("R_ERR1", clientes["C001"], servicios["S2"], 2.0)
        imprimir_resultado(False, f"DEBIÓ FALLAR: {r}")
    except ServicioNoDisponibleError as e:
        imprimir_resultado(True, f"Servicio no disponible detectado: {e}")
    finally:
        servicios["S2"].habilitar()  # siempre lo volvemos a habilitar (finally garantiza esto)

    # caso 2: duración menor al mínimo permitido
    try:
        r = Reserva("R_ERR2", clientes["C002"], servicios["E1"], 0.1)
        r.confirmar()
        imprimir_resultado(False, "DEBIÓ FALLAR por duración")
    except DuracionInvalidaError as e:
        imprimir_resultado(True, f"Duración inválida detectada: {e}")
    except SoftwareFJError as e:
        imprimir_resultado(True, f"Error capturado: {e}")

    # caso 3: cliente inactivo no puede hacer reservas
    try:
        clientes["C003"].desactivar()  # desactivamos el cliente
        r = Reserva("R_ERR3", clientes["C003"], servicios["A1"], 2.0)
        imprimir_resultado(False, "DEBIÓ FALLAR por cliente inactivo")
    except ReservaError as e:
        imprimir_resultado(True, f"Cliente inactivo detectado: {e}")
    finally:
        clientes["C003"].activar()  # reactivamos el cliente para las siguientes operaciones


# ─────────────────────────────────────────────────────────────────
# OPERACIÓN 7: Cancelación de reservas y doble cancelación
# ─────────────────────────────────────────────────────────────────

def op7_cancelacion(clientes: dict, servicios: dict, gestor: GestorReservas):
    separador("OP 7 — Cancelación de reservas")

    # cancelación normal
    try:
        r = Reserva("R004", clientes["C001"], servicios["S2"], 1.5)
        r.confirmar()
        gestor.agregar(r)
        r.cancelar()  # cancelamos la reserva
        imprimir_resultado(True, f"Reserva cancelada correctamente: {r.id} → {r.estado}")
    except SoftwareFJError as e:
        imprimir_resultado(False, f"Error al cancelar: {e}")

    # intentamos cancelar la misma reserva dos veces (debe fallar)
    try:
        reserva = gestor.obtener("R004")
        reserva.cancelar()  # esto debe lanzar ReservaYaCanceladaError
        imprimir_resultado(False, "DEBIÓ FALLAR por doble cancelación")
    except ReservaYaCanceladaError as e:
        imprimir_resultado(True, f"Doble cancelación detectada: {e}")


# ─────────────────────────────────────────────────────────────────
# OPERACIÓN 8: Procesamiento completo (confirmar + completar en un paso)
# ─────────────────────────────────────────────────────────────────

def op8_procesamiento_completo(clientes: dict, servicios: dict, gestor: GestorReservas):
    separador("OP 8 — Procesamiento completo de reserva")
    try:
        srv_asesoria = servicios["A2"]
        srv_asesoria.nivel_urgencia = "urgente"  # cambiamos la urgencia para ver el cambio en el costo
        r = Reserva("R005", clientes["C002"], srv_asesoria, 3.0, descuento=5.0)
        r.procesar()       # confirma y completa en un solo paso
        gestor.agregar(r)
        imprimir_resultado(True, f"Reserva procesada: {r.id} | Estado: {r.estado} | ${r.costo_total:,.2f}")
        print(f"\n{r.describir()}")
    except SoftwareFJError as e:
        imprimir_resultado(False, f"Error en procesamiento: {e}")


# ─────────────────────────────────────────────────────────────────
# OPERACIÓN 9: Variantes de cálculo de costo (métodos sobrecargados)
# Demostramos que calcular_costo() funciona con diferentes combinaciones de parámetros
# ─────────────────────────────────────────────────────────────────

def op9_calculo_costos_variantes(servicios: dict):
    separador("OP 9 — Variantes de cálculo de costo")
    srv = servicios["A1"]
    print(f"\n  Servicio: {srv.nombre}")
    print(f"  {'Variante':<40} {'Costo':>15}")
    print(f"  {'-'*55}")

    # probamos todas las combinaciones posibles de parámetros opcionales
    variantes = [
        ("2h, sin desc., con IVA",     srv.calcular_costo(2)),                              # solo horas
        ("2h, sin desc., sin IVA",     srv.calcular_costo(2, incluir_iva=False)),            # sin IVA
        ("2h, desc. 20%, con IVA",     srv.calcular_costo(2, descuento=20)),                 # con descuento
        ("2h, desc. 20%, sin IVA",     srv.calcular_costo(2, descuento=20, incluir_iva=False)), # desc. + sin IVA
        ("5h, sin desc., con IVA",     srv.calcular_costo(5)),                              # más horas
        ("5h, desc. 10%, con IVA",     srv.calcular_costo(5, descuento=10)),
        ("0.5h (mínimo), con IVA",     srv.calcular_costo(0.5)),                            # duración mínima
    ]
    for etiqueta, costo in variantes:
        print(f"  {etiqueta:<40} ${costo:>14,.2f}")

    # probamos que la duración inválida es rechazada correctamente
    try:
        srv.calcular_costo(0.1)  # 0.1h está por debajo del mínimo de 0.5h
    except DuracionInvalidaError as e:
        imprimir_resultado(True, f"Duración inválida en cálculo: {e}")


# ─────────────────────────────────────────────────────────────────
# OPERACIÓN 10: Resumen final del sistema
# ─────────────────────────────────────────────────────────────────

def op10_resumen(gestor: GestorReservas):
    separador("OP 10 — Resumen del sistema")
    # obtenemos las reservas agrupadas por estado
    todas       = gestor.listar()
    confirmadas = gestor.listar("confirmada")
    completadas = gestor.listar("completada")
    canceladas  = gestor.listar("cancelada")

    print(f"\n  Total reservas       : {len(todas)}")
    print(f"  Confirmadas          : {len(confirmadas)}")
    print(f"  Completadas          : {len(completadas)}")
    print(f"  Canceladas           : {len(canceladas)}")
    print(f"  Ingresos totales     : ${gestor.total_ingresos():>14,.2f}")

    print("\n  Detalle de reservas:")
    for r in todas:
        costo = f"${r.costo_total:,.2f}" if r.costo_total else "—"
        print(f"    · {r.id:<8} {r.estado:<12} {costo:>14}")

    logger.separador("SIMULACIÓN COMPLETADA")


# ─────────────────────────────────────────────────────────────────
# Punto de entrada del programa
# ─────────────────────────────────────────────────────────────────

def main():
    logger.separador("INICIO SIMULACIÓN — SOFTWARE FJ")
    print("\n" + "="*60)
    print("   SOFTWARE FJ — Sistema Integral de Gestión")
    print("   Simulación de 10 operaciones completas")
    print("="*60)

    gestor = GestorReservas()       # creamos el gestor que administra todas las reservas
    servicios = crear_catalogo()    # cargamos el catálogo de servicios disponibles

    # ejecutamos las 10 operaciones en orden
    clientes = op1_registro_clientes_validos()
    op2_registro_clientes_invalidos()
    op3_describir_servicios(servicios)
    op4_servicios_invalidos()
    op5_reservas_exitosas(clientes, servicios, gestor)
    op6_reservas_fallidas(clientes, servicios)
    op7_cancelacion(clientes, servicios, gestor)
    op8_procesamiento_completo(clientes, servicios, gestor)
    op9_calculo_costos_variantes(servicios)
    op10_resumen(gestor)

    print("\n" + "="*60)
    print("  Simulación finalizada. Revisa logs/eventos.log")
    print("="*60 + "\n")


# esto garantiza que main() solo se ejecute cuando corremos este archivo directamente
# y no cuando lo importamos desde otro archivo
if __name__ == "__main__":
    main()
