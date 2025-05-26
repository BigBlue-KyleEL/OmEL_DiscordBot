import random

# Codex of Deeds
CODEX_OF_DEEDS = {
    "Chapter IV, Line 42": "*Only the Originator of a Quest may seal its fate.*"
}

def get_codex_rule(chapter_line: str) -> str:
    rule = CODEX_OF_DEEDS.get(chapter_line)
    if rule:
        delivery_styles = [
            f"📚 *Based on the Sacred Codex of Deeds, {chapter_line}:*\n\n{rule}\n\n⚖️ Om'El’s voice echoes with authority.",
            f"📖 *As etched in the Codex of Deeds, {chapter_line}:*\n\n{rule}\n\n🔯 Om'El speaks in solemn tones.",
            f"🨶 *By decree of the Codex, {chapter_line}:*\n\n{rule}\n\n💫 The air stills as Om'El utters the law.",
            f"📜 *Scrolls whisper of {chapter_line}:*\n\n{rule}\n\n🕯️ Om'El’s words linger like incense."
        ]
        return random.choice(delivery_styles)
    else:
        return "📖 This passage of the Codex remains unwritten... for now."

def get_sealing_phrase(sealer_name: str) -> str:
    phrases = [
        f"🔒 **Thus the Quest is sealed.**\n📜 Let this deed be etched among the Oathbound Scrolls.\n*Sealed by {sealer_name}.*",
        f"🕯️ **The parchment curls, the ink dries.**\nAnother chapter concludes, sealed by {sealer_name}.",
        f"🏺 **A tale ends.**\nThe scroll is bound, the deed archived.\nOm'El nods as {sealer_name} seals the fate.",
        f"⚖️ **Om'El bears witness.**\nA Quest once open now rests forever, thanks to {sealer_name}."
    ]
    return random.choice(phrases)

def get_unclaim_phrase():
    unclaim_phrases = [
        "A shame you could not see it through. The scroll shall await another hand.",
        "Even the bravest sometimes falter. The quest returns to the Hall.",
        "Om'El frowns... but says nothing. The parchment rolls back up silently.",
        "Perhaps this was not your tale to tell. Another may rise.",
        "Duty abandoned... for now. But the Quest endures.",
        "Perhaps another day, another champion.",
        "Om'El sighs... the parchment curls back into shadow.",
        "The winds of fate shift; the quest returns to the ether.",
        "Destiny rewrites itself — the Quest is unbound once more."
    ]
    return random.choice(unclaim_phrases)

def get_claim_phrase():
    phrases = [
        "A new hero rises to meet the challenge!",
        "Quest claimed! May fortune favor your path.",
        "The scroll has been taken — destiny awaits!",
        "Your journey begins now. Make it legendary.",
        "Claimed! The gods are watching.",
        "Another quest, another tale to tell.",
        "The flames of purpose burn bright within you."
    ]
    return random.choice(phrases)

def get_gratitude_phrase():
    phrases = [
        "My heartfelt thanks goes out to:",
        "May the stars shine upon the brave souls of:",
        "Gratitude echoes for the following champions:",
        "These valiant hearts have stepped forth:",
        "Let it be known, the Quest was met by:",
        "Bound in honor, I commend:"
    ]
    return random.choice(phrases)
