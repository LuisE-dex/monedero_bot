# Monedero Bot

Bot de Telegram desarrollado en Python para la gestión de un monedero virtual personal. Permite registrar ingresos y extracciones, consultar el saldo actual, visualizar el historial de movimientos, exportar datos a CSV y generar gráficas de evolución del saldo.

La información se almacena de forma persistente en PostgreSQL utilizando SQLAlchemy como ORM.

## Características

* 💰 Consulta de saldo actual.
* ➕ Registro de ingresos.
* ➖ Registro de extracciones.
* 📜 Historial completo de transacciones.
* 📊 Generación de gráficas de evolución del saldo.
* 📄 Exportación del historial en formato CSV.
* 💱 Conversión de USD y MLC a CUP.
* 🗄️ Persistencia de datos mediante PostgreSQL.

## Tecnologías utilizadas

* Python
* PostgreSQL
* SQLAlchemy
* pyTelegramBotAPI
* Matplotlib

## Requisitos

* Python 3.10 o superior
* PostgreSQL
* pip

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/LuisE-dex/monedero_bot.git
cd monedero_bot
```

### 2. Crear y activar un entorno virtual (Opcional)

```bash
python -m venv venv
```

Linux / macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Completa los valores requeridos.

## Variables de entorno

| Variable       | Descripción                                |
| -------------- | ------------------------------------------ |
| TELEGRAM_TOKEN | Token del bot generado mediante BotFather. |
| DATABASE_URL   | Cadena de conexión a PostgreSQL.           |

### Ejemplo

```env
TELEGRAM_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/banco
```

## Obtención del Token de Telegram

1. Abre Telegram.
2. Busca el usuario **@BotFather**.
3. Ejecuta el comando `/newbot`.
4. Sigue las instrucciones para crear tu bot.
5. Copia el token generado y guárdalo en la variable `TELEGRAM_TOKEN`.

## Configuración de la Base de Datos

Crea una base de datos PostgreSQL y utiliza su cadena de conexión en la variable `DATABASE_URL`.

Ejemplo:

```sql
CREATE DATABASE banco;
```

## Ejecución

```bash
python main.py
```

## Comandos disponibles

| Comando    | Descripción                            |
| ---------- | -------------------------------------- |
| /start     | Mostrar menú principal                 |
| /balance   | Consultar saldo actual                 |
| /ingresar  | Registrar un ingreso                   |
| /extraer   | Registrar una extracción               |
| /historial | Mostrar historial de transacciones     |
| /convertir | Convertir USD o MLC a CUP              |
| /grafica   | Generar gráfica de evolución del saldo |
| /exportar  | Exportar historial en CSV              |
| /help      | Mostrar ayuda                          |
