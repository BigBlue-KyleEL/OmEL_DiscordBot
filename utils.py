# utils.py

import discord
import logging
from typing import Optional

from db import get_claimants
from flavor import get_sealing_phrase, get_gratitude_phrase
# DO NOT import the bot or constants directly from bot.py — it causes circular issues
# Instead, pass them in as parameters when calling this function

async def force_seal_quest(
    bot,  # commands.Bot or discord.Bot depending on your setup
    message: discord.Message,
    oathbound_channel_id: int,
    author_name: str = "Unknown Wanderer"
):
    # Get the channel to send the sealed message to
    oathbound_channel = bot.get_channel(oathbound_channel_id)
    if not oathbound_channel:
        logging.warning("⚠️ Oathbound Scrolls channel not found.")
        return

    if not message.embeds:
        logging.warning(f"🛑 Message {message.id} had no embed to seal.")
        return

    original_embed = message.embeds[0]
    sealed_embed = discord.Embed(
        title=f"📜 {original_embed.title}",
        description=original_embed.description,
        color=discord.Color.dark_green()
    )

    # Preserve the original embed author if available (dict-style compatibility)
    if isinstance(original_embed.author, dict):
        name = original_embed.author.get("name", "Unknown Wanderer")
        icon_url = original_embed.author.get("icon_url", discord.Embed.Empty)
    elif original_embed.author is not None:
        name = getattr(original_embed.author, "name", "Unknown Wanderer")
        icon_url = getattr(original_embed.author, "icon_url", discord.Embed.Empty)
    else:
        name = "Unknown Wanderer"
        icon_url = discord.Embed.Empty

    sealed_embed.set_author(name=name, icon_url=icon_url)

    # Fetch claimants from the database
    claimants = get_claimants(message.id)
    if claimants:
        gratitude_line = f"🪶 {get_gratitude_phrase()} {', '.join(claimants)}"
        sealed_embed.add_field(name="—", value=gratitude_line, inline=False)

    # Sealing phrase
    sealed_phrase = get_sealing_phrase(author_name)
    await oathbound_channel.send(content=sealed_phrase, embed=sealed_embed)

    # Delete original message from Hall of Deeds
    await message.delete()

    # Logging
    logging.info(
        f"🔒 The scroll '{original_embed.title}' has been sealed by {author_name}. "
        f"Those who bore its burden: {', '.join(claimants) if claimants else 'None. A lonely tale etched in silence.'}"
    )
