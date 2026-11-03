import discord
from discord.ext import commands
from discord.ui import View

ROLE_MIEMBRO_ID = 1566552522301116423
ROLE_SPANISH_ID = 1566552522301116422
ROLE_ENGLISH_ID = 1566552522301116419

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_member_join(member):
    embed = discord.Embed(
        title=f"⚔️ ¡Bienvenido/a a Mushoku Legends, {member.name}! / Welcome!",
        description=f"Hola {member.mention}, nos alegra mucho tenerte en **{member.guild.name}**.\n\n"
                    "🇪🇸 **Pasos para empezar:**\n"
                    "1. Ve al canal de verificación y reacciona con ✅ para ver el servidor.\n"
                    "2. Selecciona tu idioma en el panel de idiomas.\n\n"
                    "🇬🇧 **Getting started:**\n"
                    "1. Go to the verification channel and react with ✅ to access the server.\n"
                    "2. Select your language in the language panel.",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)
    embed.set_footer(text="Mushoku Legends • Official Bot")

    try:
        await member.send(embed=embed)
    except discord.Forbidden:
        pass

class LanguageView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Spanish 🇪🇸", style=discord.ButtonStyle.primary, custom_id="lang_spanish")
    async def spanish_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_SPANISH_ID)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("🔄 Rol Spanish retirado.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ ¡Rol Spanish añadido!", ephemeral=True)

    @discord.ui.button(label="English 🇬🇧", style=discord.ButtonStyle.secondary, custom_id="lang_english")
    async def english_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_ENGLISH_ID)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("🔄 Rol English retirado.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ ¡Rol English añadido!", ephemeral=True)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member and payload.member.bot: return
    if str(payload.emoji) == "✅":
        guild = bot.get_guild(payload.guild_id)
        if guild:
            member = guild.get_member(payload.user_id)
            role = guild.get_role(ROLE_MIEMBRO_ID)
            if member and role: await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    if str(payload.emoji) == "✅":
        guild = bot.get_guild(payload.guild_id)
        if guild:
            member = guild.get_member(payload.user_id)
            role = guild.get_role(ROLE_MIEMBRO_ID)
            if member and role: await member.remove_roles(role)

@bot.event
async def on_ready():
    print(f"🤖 Bot de VERIFICACIÓN e IDIOMAS encendido: {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def verifypanel(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title="✅ Verificación / Verification", description="Reacciona con ✅ para verificar tu cuenta.\nReact with ✅ to verify.", color=discord.Color.green())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")

@bot.command()
@commands.has_permissions(administrator=True)
async def langpanel(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title="🌐 Idioma / Language", description="Elige tu idioma / Choose your language:", color=discord.Color.blurple())
    await ctx.send(embed=embed, view=LanguageView())

# TOKEN DEL BOT DE VERIFICACIÓN
bot.run("MTU2NjkyMDE0NTExMTM1NTQwMg.GmI8Y5.S5cVENz7TFS6X5r3pCFCdqG9gYO2zJ1sjXueNc")