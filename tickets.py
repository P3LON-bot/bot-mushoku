import os
from threading import Thread
import discord
from discord.ext import commands
from flask import Flask

# --- Mini servidor web para satisfacer el puerto de Render ---
app = Flask('')


@app.route('/')
def home():
  return 'Bot de Soporte activo 24/7'


def run():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


def keep_alive():
  t = Thread(target=run)
  t.daemon = True
  t.start()


# Iniciar el servidor web
keep_alive()

# --- Configuración del Bot de Discord ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
  print(f'¡Bot de Soporte conectado como {bot.user}!')


# Obtener el token de forma segura desde las variables de entorno de Render
TOKEN = os.environ.get('DISCORD_TOKEN_SUPPORT')

if TOKEN:
  bot.run(TOKEN)
else:
  print('Error: No se encontró la variable DISCORD_TOKEN_SUPPORT')