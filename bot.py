# bot.py

import asyncio
import datetime
import discord
import logging
import os
import pytz
import sys

from db import initialize_db, add_claimant, remove_claimant, get_claimants
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from dotenv import load_dotenv
from flavor import get_codex_rule, get_sealing_phrase, get_unclaim_phrase, get_claim_phrase, get_gratitude_phrase
from logging.handlers import RotatingFileHandler


load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
EDICTS_CHANNEL_ID = int(os.getenv("EDICTS_CHANNEL_ID"))
HALL_OF_DEEDS_CHANNEL_ID = int(os.getenv("HALL_OF_DEEDS_CHANNEL_ID"))
OATHBOUND_SCROLLS_CHANNEL_ID = int(os.getenv("OATHBOUND_SCROLLS_CHANNEL_ID"))

print("[BOOT] Om'EL script is starting up...")


intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Set up rotating log file — 100MB per file, unlimited backup files
log_handler = RotatingFileHandler(
    "omel.log",           # Log file name
    maxBytes=100 * 1024 * 1024,  # 100 MB
    backupCount=0         # 0 means unlimited backups
)

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        log_handler,
        logging.StreamHandler()  # Optional: also see logs in console
    ]
)

def is_within_active_hours(now, start_hour, end_hour):
    """
    Returns True if the current hour is within the defined active hours.
    Handles wrap-around midnight ranges (e.g., 22 to 6).
    """
    if start_hour < end_hour:
        return start_hour <= now.hour < end_hour
    else:
        return now.hour >= start_hour or now.hour < end_hour


# 🏩 Codex of Deeds
CODEX_OF_DEEDS = {
    "Chapter IV, Line 42": "*Only the Originator of a Quest may seal its fate.*"
}

class QuestModal(Modal, title="Enscribe Your Quest"):
    quest_title = TextInput(label="Quest Title",  max_length=45, placeholder="Name the call to action…")
    quest_description = TextInput(label="Quest Description", style=discord.TextStyle.paragraph, placeholder="Detail the nature of your Quest…")

    async def on_submit(self, interaction: discord.Interaction):
        hall_of_deeds = bot.get_channel(HALL_OF_DEEDS_CHANNEL_ID)
        embed = discord.Embed(title=self.quest_title.value, description=self.quest_description.value, color=discord.Color.gold())
        embed.set_author(name=f"{interaction.user.display_name} has posted a Quest!", icon_url=interaction.user.display_avatar.url)
        view = QuestActionButtons(interaction.user.id)
        await hall_of_deeds.send(embed=embed, view=view)
        await interaction.response.send_message("🨶 Your Quest has been inscribed upon the Hall of Deeds.", ephemeral=True)

class QuestActionButtons(View):
    def __init__(self, author_id):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.claimed_by = []
        self.claim_button = Button(
            label="Claim Quest",
            style=discord.ButtonStyle.primary,
            custom_id="claim_quest"
        )
        self.claim_button.callback = self.claim_quest

        self.close_button = Button(
            label="Seal Quest",
            style=discord.ButtonStyle.danger,
            custom_id="close_quest"
        )
        self.close_button.callback = self.close_quest
        self.add_item(self.claim_button)
        self.add_item(self.close_button)
        self.unclaim_button = None  # Prevent dangling buttons

    async def claim_quest(self, interaction: discord.Interaction):
        user = interaction.user

        # Check if already claimed
        if user in self.claimed_by:
            await interaction.response.send_message("You've already claimed this Quest.", ephemeral=True)
            return

        # Add user to the claimed list
        self.claimed_by.append(user)

        # Store claimant in the database
        add_claimant(interaction.message.id, interaction.user.id, interaction.user.global_name or interaction.user.name)

        # Update button label
        self.update_claim_button_label()

        # If this is the first claimer, add the Unclaim button
        if not self.unclaim_button:
            self.unclaim_button = Button(
                label="Unclaim Quest",
                style=discord.ButtonStyle.danger,
                custom_id="unclaim_quest"
            )
            self.unclaim_button.callback = self.unclaim_quest
            self.add_item(self.unclaim_button)

        claim_message = get_claim_phrase()
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"📜 {claim_message}", ephemeral=True)

    async def close_quest(self, interaction: discord.Interaction):
        try:  # Begin exception handling
            if interaction.user.id != self.author_id:
                codex_text = get_codex_rule("Chapter IV, Line 42")
                await interaction.response.send_message(codex_text, ephemeral=True)
                return

            await interaction.response.defer()  # Critical: Prevents timeout
            try:
                # Bypass cache by fetching fresh message
                fresh_message = await interaction.channel.fetch_message(interaction.message.id)
            except discord.NotFound:
                await interaction.followup.send("⚠️ The scroll has already vanished!", ephemeral=True)
                return

            # ✅ Capture all necessary data before deletion
            if not interaction.message.embeds:
                await interaction.user.send("⚠️ The sacred parchment could not be recovered—lost to the winds of fate.")
                return

            # New (fetches fresh from Discord)
            try:
                fresh_message = await interaction.channel.fetch_message(interaction.message.id)
                original_embed = fresh_message.embeds[0]
            except discord.NotFound:
                await interaction.response.send_message(
                    "⚠️ The scroll has already vanished from this realm!",
                    ephemeral=True
                )
                return
            claimants = get_claimants(fresh_message.id)
            sealer_name = interaction.user.display_name

            # 🗑️ Now it's safe to delete
            await fresh_message.delete()

            # 📜 Send to #oathbound-scrolls
            oathbound_channel = bot.get_channel(OATHBOUND_SCROLLS_CHANNEL_ID)
            if not oathbound_channel:
                raise ValueError("The Hall of Oathbound Scrolls remains shrouded in mystery—its gates unseen.")

            sealed_embed = discord.Embed(
                title=f"📜 {original_embed.title}",
                description=original_embed.description,
                color=discord.Color.dark_green()
            )
            sealed_embed.set_author(
                name=original_embed.author.name,
                icon_url=original_embed.author.icon_url
            )

            if claimants:
                gratitude_line = f"🪶 {get_gratitude_phrase()} {', '.join(claimants)}"
                sealed_embed.add_field(name="—", value=gratitude_line, inline=False)

            await oathbound_channel.send(content=get_sealing_phrase(sealer_name), embed=sealed_embed)

            logging.info(
                f"🔒 The scroll '{original_embed.title}' has been sealed by {sealer_name}. "
                f"Those who bore its burden: {', '.join(claimants) if claimants else 'None. A lonely tale etched in silence.'}"
            )

            # ✅ Send confirmation (only if interaction hasn't been responded to yet)
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "The quest has been sealed, its tale now bound within the annals of history.",
                    ephemeral=True
                )

        except Exception as e:
            logging.error(f"Failed to seal quest: {str(e)}")

            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "⚠️ A disturbance in the flow of fate has prevented the sealing ritual. Seek guidance from the keepers of wisdom.",
                    ephemeral=True
                )

    def update_claim_button_label(self):
        if not self.claimed_by:
            self.claim_button.label = "Claim Quest"
            return

        names = [user.display_name for user in self.claimed_by]
        if len(names) == 1:
            label = f"Claimed by {names[0]}"
        elif len(names) == 2:
            label = f"Claimed by {names[0]} & {names[1]}"
        else:
            label = f"Claimed by {names[0]} & {names[1]} + {len(names) - 2} more"

        self.claim_button.label = label


class QuestBoard(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Enscribe a New Quest", style=discord.ButtonStyle.green, custom_id="new_quest"))

@bot.event
async def on_ready():
    print(f"✅ Om'El has awakened as {bot.user}!")
    logging.info(f"✅ Om’EL has awakened as {bot.user} at {datetime.datetime.now()}")

    # Register persistent views
    bot.add_view(QuestBoard())  # for the main "Enscribe a New Quest" button
    bot.add_view(QuestActionButtons(0))  # Dummy author_id so Discord registers it

    channel = bot.get_channel(EDICTS_CHANNEL_ID)
    if channel:
        def is_own_message(msg):
            return msg.author == bot.user

        await channel.purge(limit=10, check=is_own_message)
        welcome_embed = discord.Embed(
            title="📜 Hearken, Seekers of Purpose!",
            description=(
                 "**I am Om’EL, the eternal flame of guidance.**\n\n"
                "This chamber, the `#edicts-of-el`, is a sanctum where quests are forged and fates entwined.\n\n"
                "**To Issue a Quest** 🔱\n"
                "Click the button below to submit your sacred task. Share your cause, your call to arms, or your plea for aid.\n\n"
                "**To Claim a Quest** 🛡️\n"
                "Venture into the `#hall-of-deeds`, where quests await brave hearts. Press the **Claim** button to bind your name to a task.\n\n"
                "**To Unclaim a Quest** 🔄\n"
                "Should fate turn or courage falter, you may step back. Press **Unclaim** to release your bond without dishonor.\n\n"
                "**To Close a Quest** 🔒\n"
                "Only the one who authored a quest may conclude it. Finish your tale and seal it with purpose.\n\n"
                "Let the legends of House of EL be written by your deeds."
            ),
            color=discord.Color.purple()
        )
        await channel.send(embed=welcome_embed)

        summon_embed = discord.Embed(
            title="⚔️ 📜 A New Scroll Beckons...",
            description=(
                "Heed this call, brave soul.\n\n"
                "To inscribe a new Quest upon the annals of the **Hall of Deeds**, "
                "press the sacred button below. Your words shall be etched in virtual stone, "
                "awaiting champions to rise.\n\n"
                "*Let your intentions be clear, your rewards enticing, and your cause just.*"
            ),
            color=discord.Color.dark_gold()
        )
        await channel.send(embed=summon_embed, view=QuestBoard())
        logging.info("🔥 Om’EL has awakened and stands watch in the sanctum.")
    else:
        logging.warning("📭 Om’EL could not divine the presence of the `#edicts-of-el` channel. Was it renamed or lost in the void?")

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component and interaction.data.get("custom_id") == "new_quest":
        await interaction.response.send_modal(QuestModal())

@bot.event
async def on_command_error(ctx, error):
    logging.error(f"Unhandled command error: {error}")

@bot.event
async def on_error(event, *args, **kwargs):
    logging.error(f"⚠️ A disturbance has rippled through the aether! Event: {event}, Args: {args}, Kwargs: {kwargs}")


# Updated time_guard()
async def time_guard():
    tz = pytz.timezone("Asia/Manila")
    startup_time = datetime.datetime.now(tz)
    if startup_time.hour == 0 and startup_time.minute <= 1:
        await asyncio.sleep(120)  # Avoid immediate shutdown

    while True:
        now = datetime.datetime.now(tz)
        if now.hour == 0 and now.minute == 0:
            logging.info("🌘 Midnight shutdown initiated")
            await bot.close()
            await asyncio.sleep(2)
            sys.exit(0)

        sleep_time = 300 if now.hour not in [23, 0] else 30
        await asyncio.sleep(sleep_time)


# Enhanced main()
async def main():
    try:
        initialize_db()
        asyncio.create_task(time_guard())
        await bot.start(TOKEN)
    except discord.LoginError:
        logging.critical("❌ Invalid bot token")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"💀 Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())