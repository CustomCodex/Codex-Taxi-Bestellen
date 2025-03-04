import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime

load_dotenv()

# --- Configuratie ---
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
TAXI_DRIVER_ROLE_ID = int(os.getenv("TAXI_DRIVER_ROLE_ID")) # ID van de Taxi Chauffeur rol
TAXI_REQUEST_CHANNEL_ID = int(os.getenv("TAXI_REQUEST_CHANNEL_ID")) # ID van het kanaal waar taxi requests binnenkomen
LOG_CHANNEL_ID_STR = os.getenv("LOG_CHANNEL_ID") # Lees LOG_CHANNEL_ID als string
LOG_CHANNEL_ID = int(LOG_CHANNEL_ID_STR) if LOG_CHANNEL_ID_STR else None # Zet om naar int, of None indien leeg
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", 300)) # Timeout voor requests in seconden, default 300 (5 min)

if not all([BOT_TOKEN, TAXI_DRIVER_ROLE_ID, TAXI_REQUEST_CHANNEL_ID]): # LOG_CHANNEL_ID is nu optioneel in .env check
    print("Error: Niet alle vereiste omgevingsvariabelen zijn ingesteld in .env (BOT_TOKEN, TAXI_DRIVER_ROLE_ID, TAXI_REQUEST_CHANNEL_ID).")
    exit()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# --- Actieve Taxi Requests bijhouden ---
taxi_requests = {} # Dictionary om actieve requests op te slaan (message_id: requester_id)
driver_availability = {} # Dictionary om driver beschikbaarheid bij te houden (user_id: True/False)

# --- Functie voor logging met timestamp ---
async def log_message(log_channel, embed):
    if log_channel:
        embed.timestamp = datetime.utcnow() # Voeg timestamp toe aan de embed
        await log_channel.send(embed=embed)

# --- Prijs Input Modal ---
class PriceInputModal(discord.ui.Modal, title='💰 Prijsopgave Taxi Rit 💰'):
    price_input = discord.ui.TextInput(label='Prijs in Euro (€)', placeholder='Vul hier de prijs in (bijv. 15.50)', required=True)

    def __init__(self, requester_mention, request_message, location, notes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requester_mention = requester_mention
        self.request_message = request_message
        self.location = location # Bewaar locatie voor log
        self.notes = notes # Bewaar notities voor log

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            price = float(self.price_input.value)
            if price < 0:
                await interaction.followup.send("De prijs moet een positief getal zijn! Probeer het opnieuw.", ephemeral=True)
                return
        except ValueError:
            await interaction.followup.send("Ongeldige prijs. Gebruik een nummer en eventueel een decimaal punt (bijv. 15.50). Probeer het opnieuw.", ephemeral=True)
            return

        embed_accepted = self.request_message.embeds[0] # Pak de embed
        embed_accepted.color = discord.Color.green() # Verander kleur naar groen
        embed_accepted.title = "🚕 Taxi Bestelling - ACCEPTED 🚕" # Titel aanpassen
        embed_accepted.add_field(name="Geaccepteerd door:", value=interaction.user.mention, inline=False) # Vermeld chauffeur
        await self.request_message.edit(embed=embed_accepted, view=None) # Update embed en verwijder buttons
        await interaction.followup.send(f"Taxi bestelling geaccepteerd van {self.requester_mention}! Prijs: €{price:.2f}. Je kan contact opnemen.", ephemeral=True) # Chauffeur bevestiging # Gebruik interaction.followup.send ipv send_message

        request_channel = bot.get_channel(TAXI_REQUEST_CHANNEL_ID)
        await request_channel.send(f"Taxi rit van {self.requester_mention} is geaccepteerd door {interaction.user.mention} voor €{price:.2f}!", allowed_mentions=discord.AllowedMentions(users=[discord.User(id=int(self.requester_mention[3:-1]))])) # Tag requester met prijs

        if self.request_message.id in taxi_requests: # Check of request nog actief is voor verwijdering
            del taxi_requests[self.request_message.id] # Verwijder request uit actieve requests
        log_channel = bot.get_channel(LOG_CHANNEL_ID) # Log naar log kanaal (optioneel)
        log_embed_accept = discord.Embed(title="🟢 Taxi Bestelling Geaccepteerd (Log)", color=discord.Color.green()) # Groene kleur en emoji
        log_embed_accept.description = f"🚕💨 Taxi bestelling van **{self.requester_mention}** is geaccepteerd door **{interaction.user.mention}** voor **€{price:.2f}**." # Meer info en emoji
        log_embed_accept.add_field(name="Chauffeur:", value=interaction.user.mention, inline=False) # Extra detail
        log_embed_accept.add_field(name="Besteller:", value=self.requester_mention, inline=False) # Extra detail
        log_embed_accept.add_field(name="Locatie:", value=self.location, inline=False) # Locatie uit modal halen
        log_embed_accept.add_field(name="Notities:", value=self.notes, inline=False) # Notities uit modal halen
        await log_message(log_channel, log_embed_accept)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oeps! Er is iets fout gegaan bij het invoeren van de prijs. 🥺', ephemeral=True)
        print(f"Fout in PriceInputModal: {error}") # Log fout naar console
        log_channel = bot.get_channel(LOG_CHANNEL_ID) # Log naar log kanaal (optioneel)
        log_embed_price_error = discord.Embed(title="🔴 Prijs Input Modal Error (Log)", color=discord.Color.red()) # Rode kleur en emoji
        log_embed_price_error.description = f"⚠️ Er is een fout opgetreden in de `PriceInputModal` bij de acceptatie van een taxi bestelling door **{interaction.user.name}**." # Meer info en emoji
        log_embed_price_error.add_field(name="Chauffeur:", value=interaction.user.mention, inline=False) # Detail
        log_embed_price_error.add_field(name="Error:", value=str(error), inline=False) # Error detail
        await log_message(log_channel, log_embed_price_error)


# --- Taxi Request Modal ---
class TaxiRequestModal(discord.ui.Modal, title='🚕 Taxi Bestellen 🚕'):
    location_input = discord.ui.TextInput(label='Ophaal Locatie', placeholder='Waar moeten we je ophalen?', required=True)
    notes_input = discord.ui.TextInput(label='Extra Notities (optioneel)', placeholder='Bijv. specifieke plek, speciale instructies', style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True) # "Wacht even..." bericht

        location = str(self.location_input.value)
        notes = str(self.notes_input.value) if self.notes_input.value else "Geen extra notities"
        requester = interaction.user

        # Embed voor Taxi Request melding
        embed = discord.Embed(title="🚕 Nieuwe Taxi Bestelling 🚕", color=discord.Color.orange())
        embed.add_field(name="Besteller:", value=requester.mention, inline=False)
        embed.add_field(name="Ophaal Locatie:", value=location, inline=False)
        embed.add_field(name="Notities:", value=notes, inline=False)
        embed.set_footer(text=f"Bestelling geplaatst door {requester.name}")

        # Buttons: Accept Taxi en Cancel Taxi
        accept_button = discord.ui.Button(style=discord.ButtonStyle.success, label="✅ Accepteer Taxi", custom_id="accept_taxi")
        cancel_button = discord.ui.Button(style=discord.ButtonStyle.danger, label="❌ Annuleer Taxi", custom_id="cancel_taxi_requester")

        async def accept_taxi_callback(interaction_accept: discord.Interaction):
            if interaction_accept.user.get_role(TAXI_DRIVER_ROLE_ID): # Check of gebruiker de Taxi Chauffeur rol heeft
                request_message = await interaction_accept.channel.fetch_message(interaction_accept.message.id) # Haal message object op
                modal = PriceInputModal(requester.mention, request_message, location, notes) # Geef locatie en notes mee
                await interaction_accept.response.send_modal(modal) # Open prijs modal
            else:
                await interaction_accept.response.send_message("Alleen taxi chauffeurs kunnen bestellingen accepteren! ⚠️", ephemeral=True) # Foutmelding indien geen chauffeur
        accept_button.callback = accept_taxi_callback

        async def cancel_taxi_requester_callback(interaction_cancel: discord.Interaction):
            if interaction_cancel.user.id == requester.id: # Check of de juiste persoon annuleert
                request_message = await interaction_cancel.channel.fetch_message(interaction_cancel.message.id)
                embed_cancelled = request_message.embeds[0]
                embed_cancelled.color = discord.Color.red()
                embed_cancelled.title = "🚕 Taxi Bestelling - GEANNULEERD 🚕"
                embed_cancelled.set_footer(text=f"Bestelling geannuleerd door {requester.name}")
                await request_message.edit(embed=embed_cancelled, view=None) # Update embed en verwijder buttons
                await interaction_cancel.response.send_message("Je taxi bestelling is geannuleerd.", ephemeral=True)

                request_channel = bot.get_channel(TAXI_REQUEST_CHANNEL_ID)
                await request_channel.send(f"Taxi rit van {requester.mention} is geannuleerd door de besteller.", allowed_mentions=discord.AllowedMentions(users=[requester])) # Tag requester in annulering bericht

                if interaction_cancel.message.id in taxi_requests: # Check of request nog actief is voor verwijdering
                    del taxi_requests[interaction_cancel.message.id] # Verwijder request uit actieve requests
                log_channel = bot.get_channel(LOG_CHANNEL_ID) # Log naar log kanaal (optioneel)
                log_embed_cancel = discord.Embed(title="❌ Taxi Bestelling Geannuleerd (Log)", color=discord.Color.red()) # Rode kleur en emoji
                log_embed_cancel.description = f"🚫 Taxi bestelling van **{requester.mention}** is geannuleerd door de besteller **{requester.name}**." # Meer info en emoji
                log_embed_cancel.add_field(name="Besteller:", value=requester.mention, inline=False) # Detail
                log_embed_cancel.add_field(name="Locatie:", value=location, inline=False) # Detail
                log_embed_cancel.add_field(name="Notities:", value=notes, inline=False) # Detail
                await log_message(log_channel, log_embed_cancel)
            else:
                await interaction_cancel.response.send_message("Je kan alleen je eigen taxi bestelling annuleren! ⚠️", ephemeral=True)
        cancel_button.callback = cancel_taxi_requester_callback

        view = discord.ui.View()
        view.add_item(accept_button)
        view.add_item(cancel_button)

        request_channel = bot.get_channel(TAXI_REQUEST_CHANNEL_ID)
        if request_channel:
            request_message = await request_channel.send(embed=embed, view=view) # Stuur embed met buttons naar request kanaal
            taxi_requests[request_message.id] = requester.id # Voeg message_id en requester_id toe aan actieve requests
            await interaction.followup.send(f"Je taxi bestelling is geplaatst! Chauffeurs zijn gewaarschuwd. 🚕", ephemeral=True) # Gebruiker bevestiging
            log_channel = bot.get_channel(LOG_CHANNEL_ID) # Log naar log kanaal (optioneel)
            log_embed_new = discord.Embed(title="🚕 Nieuwe Taxi Bestelling Geplaatst (Log)", color=discord.Color.orange()) # Oranje kleur en emoji
            log_embed_new.description = f"📝 Nieuwe taxi bestelling is geplaatst door **{requester.mention}**." # Meer info en emoji
            log_embed_new.add_field(name="Besteller:", value=requester.mention, inline=False) # Detail
            log_embed_new.add_field(name="Locatie:", value=location, inline=False) # Detail
            log_embed_new.add_field(name="Notities:", value=notes, inline=False) # Detail
            await log_message(log_channel, log_embed_new)

            # Start auto-cancel timer
            async def auto_cancel_request(message_id_to_cancel, original_requester, req_location, req_notes): # locatie en notes meegeven
                await asyncio.sleep(REQUEST_TIMEOUT_SECONDS)
                if message_id_to_cancel in taxi_requests: # Check if request is still active after timeout
                    request_msg_timeout = await request_channel.fetch_message(message_id_to_cancel)
                    if request_msg_timeout and request_msg_timeout.embeds: # Check if message and embed still exist
                        embed_timeout = request_msg_timeout.embeds[0]
                        embed_timeout.color = discord.Color.red()
                        embed_timeout.title = "🚕 Taxi Bestelling - TIMEOUT ⏰ - GEANNULEERD 🚕"
                        embed_timeout.description = "Geen chauffeur heeft de bestelling op tijd geaccepteerd."
                        embed_timeout.set_footer(text=f"Bestelling automatisch geannuleerd wegens timeout.")
                        await request_msg_timeout.edit(embed=embed_timeout, view=None) # Update embed en verwijder buttons
                        del taxi_requests[message_id_to_cancel] # Verwijder request uit actieve requests

                        await request_channel.send(f"Taxi rit van {original_requester.mention} is geannuleerd wegens timeout (geen chauffeur geaccepteerd).", allowed_mentions=discord.AllowedMentions(users=[original_requester])) # Tag requester in timeout bericht


                        log_channel_timeout = bot.get_channel(LOG_CHANNEL_ID) # Log naar log kanaal (optioneel)
                        log_embed_timeout_log = discord.Embed(title="⏰ Taxi Bestelling Timeout (Log)", color=discord.Color.red()) # Rode kleur en emoji
                        log_embed_timeout_log.description = f"⏱️ Taxi bestelling van **{original_requester.mention}** is automatisch geannuleerd wegens timeout. Geen enkele chauffeur heeft de bestelling op tijd geaccepteerd." # Meer info en emoji
                        log_embed_timeout_log.add_field(name="Besteller:", value=original_requester.mention, inline=False) # Detail
                        log_embed_timeout_log.add_field(name="Locatie:", value=req_location, inline=False) # Detail
                        log_embed_timeout_log.add_field(name="Notities:", value=req_notes, inline=False) # Detail
                        log_embed_timeout_log.set_footer(text="Timeout duur: {} seconden".format(REQUEST_TIMEOUT_SECONDS)) # Extra info: timeout duur
                        await log_message(log_channel_timeout, log_embed_timeout_log)
            bot.loop.create_task(auto_cancel_request(request_message.id, requester, location, notes)) # locatie en notes meegeven aan timer

        else:
            await interaction.followup.send("Kon het taxi request kanaal niet vinden. Contacteer een admin! ⚠️", ephemeral=True) # Foutmelding indien kanaal niet gevonden

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oeps! Er is iets fout gegaan. 🥺', ephemeral=True)
        print(f"Fout in TaxiRequestModal: {error}") # Log fout naar console
        log_channel = bot.get_channel(LOG_CHANNEL_ID) # Log naar log kanaal (optioneel)
        log_embed_modal_error = discord.Embed(title="🔴 Taxi Modal Error (Log)", color=discord.Color.red()) # Rode kleur en emoji
        log_embed_modal_error.description = f"⚠️ Er is een fout opgetreden in de `TaxiRequestModal` bij het plaatsen van een taxi bestelling door **{interaction.user.name}**." # Meer info en emoji
        log_embed_modal_error.add_field(name="Besteller:", value=interaction.user.mention, inline=False) # Detail
        log_embed_modal_error.add_field(name="Error:", value=str(error), inline=False) # Error detail
        await log_message(log_channel, log_embed_modal_error)


# --- /taxi-bestellen Commando ---
@bot.tree.command(name="taxi-bestellen", description="Bestel een taxi naar je locatie.")
async def taxi_bestellen_command(interaction: discord.Interaction):
    """Opent een modal om een taxi te bestellen."""
    await interaction.response.send_modal(TaxiRequestModal())

# --- /taxi-status Commando ---
@bot.tree.command(name="taxi-status", description="Zet je beschikbaarheid als taxi chauffeur.")
@discord.app_commands.choices(status=[
    discord.app_commands.Choice(name="Beschikbaar", value="available"),
    discord.app_commands.Choice(name="Niet Beschikbaar", value="unavailable"),
])
async def taxi_status_command(interaction: discord.Interaction, status: discord.app_commands.Choice[str]):
    """Stel de beschikbaarheid van de taxi chauffeur in."""
    if interaction.user.get_role(TAXI_DRIVER_ROLE_ID):
        if status.value == "available":
            driver_availability[interaction.user.id] = True
            await interaction.response.send_message("Je status is nu ingesteld op **Beschikbaar** voor taxi bestellingen. ✅", ephemeral=True)
        elif status.value == "unavailable":
            driver_availability[interaction.user.id] = False
            await interaction.response.send_message("Je status is nu ingesteld op **Niet Beschikbaar** voor taxi bestellingen. ❌", ephemeral=True)
        log_channel = bot.get_channel(LOG_CHANNEL_ID) # Log naar log kanaal (optioneel)
        log_embed_status = discord.Embed(title="🚦 Taxi Status Update (Log)", color=discord.Color.blue()) # Blauwe kleur en emoji
        log_embed_status.description = f"🚕 Chauffeur **{interaction.user.name}** heeft status veranderd naar **{status.name}**." # Meer info en emoji
        log_embed_status.add_field(name="Chauffeur:", value=interaction.user.mention, inline=False) # Detail
        log_embed_status.add_field(name="Nieuwe Status:", value=status.name, inline=False) # Detail
        await log_message(log_channel, log_embed_status)

    else:
        await interaction.response.send_message("Alleen taxi chauffeurs kunnen hun status aanpassen! ⚠️", ephemeral=True)

# --- /taxi-requests-clear Commando (Admin only) ---
@bot.tree.command(name="taxi-requests-clear", description="Verwijder alle actieve taxi requests (ADMIN ONLY).")
@commands.has_permissions(administrator=True) # Vereist administrator permissies
async def taxi_requests_clear_command(interaction: discord.Interaction):
    """Verwijdert alle actieve taxi requests."""
    global taxi_requests
    num_requests_cleared = len(taxi_requests)
    taxi_requests = {} # Reset de dictionary
    await interaction.response.send_message(f"Alle actieve taxi requests ({num_requests_cleared} requests) zijn verwijderd. ✅", ephemeral=True)
    log_channel = bot.get_channel(LOG_CHANNEL_ID) # Log naar log kanaal (optioneel)
    log_embed_clear_all = discord.Embed(title="🧹 Taxi Requests Opgekuist (Admin Log)", color=discord.Color.purple()) # Paarse kleur en emoji
    log_embed_clear_all.description = f"Admin **{interaction.user.name}** heeft alle actieve taxi requests verwijderd. 🗑️" # Meer info en emoji
    log_embed_clear_all.add_field(name="Admin:", value=interaction.user.mention, inline=False) # Detail
    log_embed_clear_all.add_field(name="Aantal verwijderde requests:", value=str(num_requests_cleared), inline=False) # Detail
    await log_message(log_channel, log_embed_clear_all)


@taxi_requests_clear_command.error
async def taxi_requests_clear_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message("Je hebt geen administrator rechten om dit commando uit te voeren! ⚠️", ephemeral=True)
    else:
        await interaction.response.send_message(f"Er is een fout opgetreden bij het uitvoeren van dit commando. 🥺", ephemeral=True)
        log_channel = bot.get_channel(LOG_CHANNEL_ID) # Log naar log kanaal (optioneel)
        log_embed_clear_error = discord.Embed(title="🔴 Taxi Requests Clear Error (Log)", color=discord.Color.red()) # Rode kleur en emoji
        log_embed_clear_error.description = f"⚠️ Fout bij uitvoeren van `/taxi-requests-clear` commando door admin **{interaction.user.name}**." # Meer info en emoji
        log_embed_clear_error.add_field(name="Admin:", value=interaction.user.mention, inline=False) # Detail
        log_embed_clear_error.add_field(name="Error:", value=str(error), inline=False) # Error detail
        await log_message(log_channel, log_embed_clear_error)


# --- Bot Ready Event ---
@bot.event
async def on_ready():
    print(f'Ingelogd als {bot.user.name} ({bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f"Gesynced {len(synced)} commando(s)")
    except Exception as e:
        print(f"Fout bij syncen commando\'s: {e}")
        log_channel = bot.get_channel(LOG_CHANNEL_ID) # Log naar log kanaal (optioneel)
        log_embed_sync_error = discord.Embed(title="🔴 Command Sync Error (Log)", color=discord.Color.red()) # Rode kleur en emoji
        log_embed_sync_error.description = f"⚠️ Fout bij het syncen van commando's bij bot start. Commando's zijn mogelijk niet correct geregistreerd." # Meer info en emoji
        log_embed_sync_error.add_field(name="Error:", value=str(e), inline=False) # Error detail
        await log_message(log_channel, log_embed_sync_error)

# --- Run de Bot ---
if __name__ == "__main__":
    bot.run(BOT_TOKEN)