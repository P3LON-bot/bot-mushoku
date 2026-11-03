import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import asyncio
import io

CATEGORY_ID = 1566552525392576560
TRANSCRIPT_CHANNEL_ID = 1566552524826214515

CATEGORY_ROLES = {
    "Content Creators": [1566552522368356439, 1566552522351710296, 1566552522380935283],
    "Partnerships": [1566552522393657529, 1566552522393657526, 1566552522380935285, 1566552522380935286],
    "Report Staff": [1566552522380935285, 1566552522393657529],
    "In-Game Issues": [1566552522380935278, 1566552522380935281]
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

class CloseReasonModal(Modal, title="Motivo de Cierre / Closing Reason"):
    reason = TextInput(label="Motivo / Reason", placeholder="Problema solucionado...", style=discord.TextStyle.paragraph, required=True, max_length=300)

    def __init__(self, ticket_channel, claimed_by):
        super().__init__()
        self.ticket_channel = ticket_channel
        self.claimed_by = claimed_by

    async def on_submit(self, interaction: discord.Interaction):
        closing_reason = self.reason.value
        staff_member = interaction.user
        guild = interaction.guild

        await interaction.response.send_message(f"🔒 Ticket cerrado por **{staff_member.display_name}**. Cerrando en 5 segundos...", ephemeral=False)

        transcript_content = f"=== TRANSCRIPCIÓN: {self.ticket_channel.name} ===\nCerrado por: {staff_member}\nMotivo: {closing_reason}\n\n"
        async for message in self.ticket_channel.history(limit=500, oldest_first=True):
            transcript_content += f"[{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {message.author}: {message.content}\n"

        transcript_channel = guild.get_channel(TRANSCRIPT_CHANNEL_ID)
        if transcript_channel:
            file = discord.File(fp=io.BytesIO(transcript_content.encode("utf-8")), filename=f"transcripcion-{self.ticket_channel.name}.txt")
            await transcript_channel.send(file=file)

        await asyncio.sleep(5)
        try:
            await self.ticket_channel.delete()
        except:
            pass

class TicketActionsView(View):
    def __init__(self, ticket_channel, ticket_author, category_name):
        super().__init__(timeout=None)
        self.ticket_channel = ticket_channel
        self.ticket_author = ticket_author
        self.category_name = category_name
        self.claimed_by = None

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green, emoji="🙋‍♂️", custom_id="claim_ticket_btn")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.claimed_by and self.claimed_by != interaction.user:
            await interaction.response.send_message(f"❌ Ya fue reclamado por {self.claimed_by.mention}.", ephemeral=True)
            return
        if self.claimed_by == interaction.user:
            self.claimed_by = None
            button.label = "Claim"
            button.style = discord.ButtonStyle.green
            await interaction.response.send_message("🔄 Has dejado libre el ticket.", ephemeral=False)
            return
        self.claimed_by = interaction.user
        button.label = f"Claimed ({self.claimed_by.display_name})"
        button.style = discord.ButtonStyle.secondary
        await interaction.response.send_message(f"✅ Reclamado por {interaction.user.mention}.", ephemeral=False)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket_btn")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CloseReasonModal(self.ticket_channel, self.claimed_by))

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="In-Game Issues", description="Gamepasses, items or bugs", emoji="🛠️", value="In-Game Issues"),
            discord.SelectOption(label="Content Creators", description="Applications or creator matters", emoji="💳", value="Content Creators"),
            discord.SelectOption(label="Partnerships", description="Alliances & collaborations", emoji="📦", value="Partnerships"),
            discord.SelectOption(label="Report Staff", description="Misconduct or abuse of power", emoji="🤝", value="Report Staff")
        ]
        super().__init__(placeholder="Choose a support category / Elige una categoría", min_values=1, max_values=1, options=options, custom_id="ticket_select_menu")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category_name = self.values[0]
        user = interaction.user
        channel_name = f"ticket-{user.name.lower()}"

        if discord.utils.get(guild.channels, name=channel_name):
            await interaction.response.send_message("❌ Ya tienes un ticket abierto.", ephemeral=True)
            return

        target_category = guild.get_channel(CATEGORY_ID)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(name=channel_name, category=target_category, overwrites=overwrites)
        role_mentions = " ".join([f"<@&{r_id}>" for r_id in CATEGORY_ROLES.get(category_name, [])])

        embed = discord.Embed(description="Describe in detail how we can help. / Describe cómo podemos ayudarte.", color=discord.Color.from_rgb(88, 101, 242))
        embed.add_field(name="Category", value=category_name, inline=False)
        embed.add_field(name="Customer", value=user.mention, inline=False)

        await ticket_channel.send(content=f"{role_mentions} {user.mention}", embed=embed, view=TicketActionsView(ticket_channel, user, category_name))
        await interaction.response.send_message(f"✅ Creado en {ticket_channel.mention}", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.event
async def on_ready():
    print(f"🤖 Bot de TICKETS encendido: {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title="🔺 Official Assistance Panel", description="Select an option from the menu below to open a ticket:", color=discord.Color.red())
    await ctx.send(embed=embed, view=TicketView())

# TOKEN DEL BOT DE TICKETS (SUPPORT)
bot.run("MTU2NjU4ODEzMjQyMDIzMTMxOA.GkeXkD.VjqUn9yvVxkhGytlFWUHinmW0ULsFlr6N32fko")