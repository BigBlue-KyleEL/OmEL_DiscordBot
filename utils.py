# utils.py
import discord

async def force_seal_quest(message: discord.Message, author_name: str = "Unknown Wanderer"):
    from main import bot  # Or wherever your bot is instantiated
    from constants import OATHBOUND_SCROLLS_CHANNEL_ID  # Adjust to your layout
    from db import get_claimants
    from lore import get_sealing_phrase, get_gratitude_phrase  # Your custom lore functions

    # Reconstruct and send to Oathbound Scrolls
    oathbound_channel = bot.get_channel(OATHBOUND_SCROLLS_CHANNEL_ID)
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
    sealed_embed.set_author(name=original_embed.author.name, icon_url=original_embed.author.icon_url)

    claimants = get_claimants(message.id)
    if claimants:
        gratitude_line = f"🪶 {get_gratitude_phrase()} {', '.join(claimants)}"
        sealed_embed.add_field(name="—", value=gratitude_line, inline=False)

    sealed_phrase = get_sealing_phrase(author_name)
    await oathbound_channel.send(content=sealed_phrase, embed=sealed_embed)
    await message.delete()

    # 🪶 Lore-themed log entry
    quest_title = original_embed.title
    logging.info(
        f"🔒 The scroll '{quest_title}' has been sealed by {author_name}. "
        f"Those who bore its burden: {', '.join(claimants) if claimants else 'None. A lonely tale etched in silence.'}"
    )
