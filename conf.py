import logging
from logging_conf import configure_logging
import os

from dotenv import load_dotenv

load_dotenv()

tasa_mlc = 260
tasa_usd = 370

commands = ("/start", "/balance", "/ingresar", "/extraer", "/historial", "/convertir", "/help", "/grafica")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")


configure_logging()
logger = logging.getLogger("app")