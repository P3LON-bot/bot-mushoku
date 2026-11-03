import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot de Verificacion activo 24/7"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_ID = 1566552522301116423

class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify / Verificarme ✅", style=discord.ButtonStyle.green, custom_id="verify_button_persistent")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_ID)
        if role:
            if role in interaction.user.roles:
                await interaction.response.send_message("¡Ya estás verificado en el servidor! / You are already verified!", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("¡Verificación exitosa! Bienvenido/a 🎉 / Successfully verified! Welcome!", ephemeral=True)
        else:
            await interaction.response.send_message("Error: Rol no encontrado / Role not found.", ephemeral=True)

class LanguageSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Español", description="Selecciona tu idioma español", emoji="🇪🇸"),
            discord.SelectOption(label="English", description="Select English language", emoji="🇬🇧"),
        ]
        super().__init__(placeholder="Elige tu idioma / Choose your language", min_values=1, max_values=1, custom_id="language_select_persistent")

    async def callback(self, interaction: discord.Interaction):
        lang = self.values[0]
        await interaction.response.send_message(f"Has seleccionado / You selected: **{lang}** 🌐", ephemeral=True)

class LanguageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(LanguageSelect())

@bot.event
async def on_ready():
    bot.add_view(VerificationView())
    bot.add_view(LanguageView())
    print(f'Bot de Verificación conectado como {bot.user}')

# --- COMANDO DE TEXTO !verificacion ---
@bot.command(name="verificacion")
@commands.has_permissions(administrator=True)
async def verificacion(ctx):
    embed = discord.Embed(
        title="🔒 Server Verification / Verificación del Servidor",
        description="Haz clic en el botón de abajo para verificar tu cuenta.\n*Click the button below to verify your account.*",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=VerificationView())
    try:
        await ctx.message.delete()
    except:
        pass

# --- COMANDO DE TEXTO !idiomas ---
@bot.command(name="idiomas")
@commands.has_permissions(administrator=True)
async def idiomas(ctx):
    embed = discord.Embed(
        title="🌐 Language Selection / Selección de Idioma",
        description="Elige tu idioma en el menú de abajo.\n*Choose your language from the menu below.*",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=LanguageView())
    try:
        await ctx.message.delete()
    except:
        pass

keep_alive()
bot.run(os.environ.get('DISCORD_TOKEN'))