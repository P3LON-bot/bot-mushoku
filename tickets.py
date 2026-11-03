import os
import discord
from discord.ext import commands

# Configuración inicial del bot de Soporte/Tickets
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"¡Bot de Tickets conectado como {bot.user}!")

# Aquí va toda la lógica de tus comandos de tickets...

# Ejecutar el bot de forma segura usando la variable de entorno
TOKEN = os.environ.get("DISCORD_TOKEN_SUPPORT")
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: No se encontró el token de soporte en las variables de entorno.")