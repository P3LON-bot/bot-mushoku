import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot de Soporte activo 24/7"

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

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Soporte General / General Support", description="Dudas generales / General questions", emoji="❓"),
            discord.SelectOption(label="Reportar / Report Issue", description="Reportar fallas / Report problems", emoji="⚠️"),
            discord.SelectOption(label="Compras / Purchases", description="Dudas con pagos / Payment help", emoji="💳"),
        ]
        super().__init__(placeholder="Choose a support category / Elige una categoría", min_values=1, max_values=1, custom_id="ticket_select_persistent")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        category_name = self.values[0]
        guild = interaction.guild
        user = interaction.user
        
        channel_name = f"ticket-{user.name}".lower()

        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if existing_channel:
            await interaction.followup.send(f"Ya tienes un ticket abierto / You already have an open ticket: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        
        embed = discord.Embed(
            title=f"Ticket: {category_name}",
            description=f"Hola {user.mention}, bienvenido a tu ticket.\nExplica tu problema y te atenderemos pronto.\n\n*Hello {user.mention}, welcome to your ticket. Explain your issue and we'll assist you shortly.*",
            color=discord.Color.red()
        )
        await ticket_channel.send(content=user.mention, embed=embed)
        await interaction.followup.send(f"Ticket creado correctamente / Ticket created successfully: {ticket_channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.event
async def on_ready():
    bot.add_view(TicketView())
    print(f'Bot de Soporte conectado como {bot.user}')

# --- COMANDO DE TEXTO !panel ---
@bot.command(name="panel")
@commands.has_permissions(administrator=True)
async def panel(ctx):
    embed = discord.Embed(
        title="🔺 Official Assistance Panel / Panel Oficial de Asistencia",
        description="Selecciona una opción del menú de abajo para abrir un ticket:\n*Select an option from the menu below to open a ticket:*",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed, view=TicketView())
    try:
        await ctx.message.delete()
    except:
        pass

keep_alive()
bot.run(os.environ.get('DISCORD_TOKEN'))