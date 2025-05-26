"""
Bot de Telegram para gestión de monedero personal.
Permite ingresar, extraer, consultar saldo y ver historial de transacciones.
"""
import traceback, csv, io, matplotlib, matplotlib.pyplot as plt
matplotlib.use('Agg')
from datetime import datetime
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from bot import bot

from database import db

from conf import tasa_mlc, tasa_usd, commands, logger

moneda = None
valor = None

db.connect()

#funciones
def guardar_usuario(msg):
    """Guarda o actualiza la información del usuario en la base de datos."""
    dataUser = {
        "id": msg.from_user.id,
        "username": msg.from_user.username,
        "first_name": msg.from_user.first_name,
        "last_name": msg.from_user.last_name
    }
    db.create_model(dataUser, db.users)

def guardar_transaccion(msg, operation, current_balance, deposited, extracted, previous_balance, tipo):
    """Guarda una transacción en la base de datos."""
    dataIngreso = {
        "user_id": msg.from_user.id,
        "operation": operation,
        "current_balance": current_balance,
        "money_deposited": deposited,
        "money_extracted": extracted,
        "previous_balance": previous_balance,
        "type": tipo,
        "date": datetime.now()
    }
    db.create_model(dataIngreso, db.tramites)

def pedir_moneda(msg):
    """
    Solicita al usuario el tipo de moneda después de ingresar un monto.
    
    Args:
        msg: Mensaje de Telegram con el monto ingresado por el usuario.
    """
    #Limpiando el emoji y espacios
    texto = msg.text.strip()
    monto_limpio = ''.join(c for c in texto if c.isdigit() or c == '.')
    
    try:
        monto = float(monto_limpio.replace(",", "."))
        if monto <= 0:
            raise ValueError
    except ValueError:
        bot.send_message(msg.chat.id, "⚠️ Por favor, ingresa un monto valido y positivo.")
        return
    
    global valor
    valor = monto
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("💲CUP"), KeyboardButton("💲USD"), KeyboardButton("💲MLC"))
    
    bot.send_message(msg.chat.id, "Especifique el tipo de moneda (CUP, USD, MLC):", reply_markup=markup)
    bot.register_next_step_handler(msg, procesar_ingreso, monto)
    
def procesar_ingreso(msg, monto):
    """
    Procesa el ingreso de dinero para un usuario.

    Args:
        msg: Mensaje de Telegram con la información del usuario.
        monto (float): Monto a ingresar.

    Guarda la transacción en la base de datos y actualiza el saldo.
    """
    monedas = ("CUP", "USD", "MLC")

    # Limpiar emoji y espacios
    texto = msg.text.strip()
    # Extraer solo letras mayúsculas (eliminando emojis y espacios)
    moneda_limpia = ''.join(c for c in texto if c.isalpha()).upper()

    if moneda_limpia not in monedas:
        bot.send_message(msg.chat.id, "❌ Moneda invalida!")
        return

    global moneda
    moneda = moneda_limpia

    user_id = msg.from_user.id
    last_id = db.get_last_id(user_id)
    saldo_anterior = db.get_current_balance(last_id) if last_id is not None else 0.0
    saldo_anterior_type = db.get_coin_type(last_id, "type") if last_id is not None else "CUP"

    if moneda_limpia != saldo_anterior_type:
        bot.send_message(
            msg.chat.id,
            f"⚠️ El tipo de moneda no coincide con el tipo de moneda por defecto ({saldo_anterior_type}).\nPuede convertir la moneda deseada con /convertir",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    saldo_actual = saldo_anterior + monto

    guardar_usuario(msg)
    guardar_transaccion(msg, "ingreso", saldo_actual, monto, 0.0, saldo_anterior, saldo_anterior_type)

    bot.send_message(msg.chat.id, f"✅ Ingreso realizado!\nSaldo actual: {saldo_actual} {saldo_anterior_type}")

def procesar_extraccion(msg):
    """
    Procesa la extracción de dinero para un usuario.

    Args:
        msg: Mensaje de Telegram con la información del usuario.

    Guarda la transacción en la base de datos y actualiza el saldo.
    """
    try:
        monto = float(msg.text.replace(",", "."))
        if monto <= 0:
            raise ValueError
    except ValueError:
        bot.send_message(msg.chat.id, "⚠️ Por favor, ingresa un monto valido y positivo.")
        return

    user_id = msg.from_user.id
    last_id = db.get_last_id(user_id)
    saldo_anterior = db.get_current_balance(last_id) if last_id is not None else 0.0
    saldo_anterior_type = db.get_coin_type(last_id, "type") if last_id is not None else msg.text.upper()


    if monto > saldo_anterior:
        bot.send_message(msg.chat.id, f"❌ No puedes extraer mas de tu saldo actual ({saldo_anterior} {saldo_anterior_type}).")
        return

    saldo_actual = saldo_anterior - monto

    guardar_usuario(msg)
    guardar_transaccion(msg, "extraccion", saldo_actual, 0.0, monto, saldo_anterior, saldo_anterior_type)
    
    bot.send_message(msg.chat.id, f"💸 Extraccion realizada!\nSaldo actual: {saldo_actual} {saldo_anterior_type}")
    
def procesar_conversion(msg, saldo_anterior, moneda, valor):
    """
    Procesa la conversion de dinero para un usuario.

    Args:
        msg: Mensaje de Telegram con la información del usuario.
        saldo_anterior: Saldo anterior del usuario.
        moneda: Tipo de moneda a convertir (CUP, USD, MLC).
        valor: Monto a convertir.

    Guarda la transacción en la base de datos y actualiza el saldo.
    """         
    if moneda == "USD":
        monto_convertido = valor * tasa_usd
    else:
        monto_convertido = valor * tasa_mlc

    saldo_actual = saldo_anterior + monto_convertido

    guardar_usuario(msg)
    guardar_transaccion(msg, "ingreso", saldo_actual, 0.0, 0.0, saldo_anterior, "CUP")
        
    bot.send_message(msg.chat.id,f"✅ Conversión realizada: {valor} {moneda} = {monto_convertido} CUP\nSaldo actual: {saldo_actual} CUP", reply_markup = ReplyKeyboardRemove())
        
    moneda = None
    valor = None
        
    
#handlers
@bot.message_handler(commands=["start"])
def cmd_start(msg):
    """
    Handler para el comando /start.
    Muestra las principales opciones del bot.
    """
    logger.info("/start")
    
    ans = (
        f"👋 Hola {msg.from_user.first_name}!\n\n"
        "💰 Mostrar saldo actual /balance\n"
        "➕ Ingresar un monto determinado /ingresar\n"
        "➖ Extraer un monto determinado /extraer\n"
        "📜 Ver historial /historial"
    )
    
    bot.send_message(msg.chat.id, ans)
    
@bot.message_handler(commands=["balance"])
def cmd_balance(msg):
    """
    Handler para el comando /balance.
    Muestra el monto total.
    """
    logger.info("/balance")

    query = db.tramites.select().where(db.tramites.c.user_id == msg.from_user.id).order_by(db.tramites.c.id.desc()).limit(1)
    result = db.session.execute(query).fetchone()
    if result:
        saldo_actual = result.current_balance
        saldo_anterior_type = result.type
        bot.send_message(msg.chat.id, f"💰 Tu saldo actual es: {saldo_actual} {saldo_anterior_type}")
    else:
        bot.send_message(msg.chat.id, "⚠️ No hay saldo registrado aun.")

@bot.message_handler(commands=["ingresar"])
def cmd_ingresar(msg):
    """
    Handler para el comando /ingresar.
    Muestra opciones de monto y solicita el monto a ingresar.
    """
    
    logger.info("/ingresar")
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(
        KeyboardButton("💵100"), KeyboardButton("💵500"), KeyboardButton("💵1000"),
        KeyboardButton("💵2000"), KeyboardButton("💵5000"), KeyboardButton("💵10000")
    )
    
    bot.send_message(msg.chat.id, "Cuanto deseas ingresar? Elige una opción o escribe un monto:", reply_markup=markup)
    bot.register_next_step_handler(msg, pedir_moneda)
    
@bot.message_handler(commands=["extraer"])
def cmd_extraer(msg):
    """
    Handler para el comando /extraer.
    Permite extraer una parte del monto total.
    """
    logger.info("/extraer")
    
    bot.send_message(msg.chat.id, "Cuanto deseas extraer?")
    bot.register_next_step_handler(msg, procesar_extraccion)

@bot.message_handler(commands=["historial"])
def cmd_historial(msg):
    """
    Handler para el comando /historial.
    Permite visualizar todas las transacciones realizadas hasta el momento.
    """
    logger.info("/historial")
    
    query = db.tramites.select().where(db.tramites.c.user_id == msg.from_user.id).order_by(db.tramites.c.date.desc())
    result = db.session.execute(query).fetchall()

    if not result:
        bot.send_message(msg.chat.id, "No hay transacciones registradas aun.")
        return

    historial = []
    for row in result:
        fecha = row.date.strftime("%Y-%m-%d %H:%M:%S")
        if row.operation == "ingreso":
            linea = f"➕Ingreso: +{row.money_deposited} | Saldo: {row.current_balance} | {fecha}"
        else:
            linea = f"➖Extraccion: -{row.money_extracted} | Saldo: {row.current_balance} | {fecha}"
        historial.append(linea)

    bloque = ""
    for i, linea in enumerate(historial, 1):
        bloque += linea + "\n"
        if i % 10 == 0 or i == len(historial):
            bot.send_message(msg.chat.id, bloque)
            bloque = ""

@bot.message_handler(commands=["convertir"])
def cmd_convertir(msg):
    """
    Handler para el comando /convertir.
    Permite convertir la moneda a CUP en caso de no ser este.
    """
    logger.info("/convertir")
    
    if valor == None or moneda == None:
        bot.send_message(msg.chat.id, "Opcion /convertir no disponible")
        return
    
    user_id = msg.from_user.id
    last_id = db.get_last_id(user_id)
    if last_id is None:
        saldo_anterior = 0.0
    else:
        saldo_anterior = db.get_current_balance(last_id)

    procesar_conversion(msg, saldo_anterior, moneda, valor)
    
@bot.message_handler(commands=["grafica"])
def cmd_grafica(msg):
    """
    Handler para el comando /grafica.
    Envía una gráfica de la evolución del saldo del usuario.
    """
    logger.info("/grafica")

    #Obtener historial de transacciones
    query = db.tramites.select().where(
        db.tramites.c.user_id == msg.from_user.id
    ).order_by(db.tramites.c.date.asc())
    result = db.session.execute(query).fetchall()

    if not result or len(result) < 2:
        bot.send_message(msg.chat.id, "📉 No hay suficientes transacciones para mostrar la gráfica.")
        return

    fechas = [row.date.strftime("%Y-%m-%d %H:%M:%S") for row in result]
    saldos = [float(row.current_balance) for row in result]

    plt.figure(figsize=(10, 5))
    plt.plot(fechas, saldos, marker='o', color='blue')
    plt.title("Evolución del saldo")
    plt.xlabel("Fecha")
    plt.ylabel("Saldo")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(rotation=45)

    #Mostrar solo algunas fechas si hay muchas
    if len(fechas) > 10:
        step = max(1, len(fechas) // 10)
        plt.xticks([fechas[i] for i in range(0, len(fechas), step)])

    #Agregar valores sobre los puntos
    for x, y in zip(fechas, saldos):
        plt.text(x, y, f"{y:.2f}", fontsize=8, ha='center', va='bottom')

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    bot.send_photo(msg.chat.id, buf, caption="📊 Evolución de tu saldo")
    buf.close()
    
@bot.message_handler(commands=["exportar"])
def cmd_exportar(msg):
    """
    Handler para el comando /exportar.
    Envía el historial de transacciones del usuario como archivo CSV.
    """
    logger.info("/exportar")

    # Obtener historial de transacciones
    query = db.tramites.select().where(db.tramites.c.user_id == msg.from_user.id).order_by(db.tramites.c.date.asc())
    result = db.session.execute(query).fetchall()

    if not result:
        bot.send_message(msg.chat.id, "📭 No hay transacciones para exportar.")
        return

    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fecha", "Operación", "Monto Ingresado", "Monto Extraído", "Saldo", "Tipo de Moneda"])

    for row in result:
        writer.writerow([
            row.date.strftime("%Y-%m-%d %H:%M:%S"),
            row.operation,
            row.money_deposited,
            row.money_extracted,
            row.current_balance,
            row.type
        ])

    output.seek(0)
    # Convertir a bytes para enviar como archivo
    csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
    output.close()

    bot.send_document(msg.chat.id, csv_bytes, caption="📄 Historial de transacciones (CSV)")
    csv_bytes.close()
    
@bot.message_handler(commands=["help"])
def cmd_help(msg):
    bot.send_message(msg.chat.id,
        "ℹ️ Comandos disponibles:\n"
        "/balance - Ver tu saldo actual\n"
        "/ingresar - Ingresar dinero\n"
        "/extraer - Extraer dinero\n"
        "/historial - Ver historial\n"
        "/convertir - Convertir moneda\n"
        "/grafica - Ver gráfica de tu saldo\n"
        "/exportar - Exportar historial a CSV\n"
        "/start - Menú principal"
    )    


#para comandos no validos
@bot.message_handler(func = lambda msg: True)
def mensaje_no_valido(msg):
    """
    Maneja mensajes que no corresponden a comandos válidos del bot.
    """
    try:
        mensaje = msg.text
        if not mensaje.startswith("/") or mensaje not in commands:
            bot.send_message(msg.chat.id, "🚫 Comando no válido. Usa /start para ver las opciones.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}\n{traceback.format_exc()}")
        bot.send_message(msg.chat.id, "⚠️ Ocurrió un error inesperado. Intenta de nuevo.")
    

if __name__ == "__main__":
    logger.info("Bot Online!")
    bot.polling()
    
logger.info("Bot Offline!")

