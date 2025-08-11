import regex as re

HARAKAT = set("ًٌٍَُِّْ")
SUKUN = "ْ"

def to_prosody(s: str) -> str:
    """Convert diacritized text into a pattern of short (∪) and long (–) syllables."""
    out = []
    prev = ""
    for ch in s:
        if ch in "اأإآوويى":
            out.append("–")
        elif ch in HARAKAT:
            if ch == SUKUN and out:
                out[-1] = "–"
            else:
                out.append("∪")
        prev = ch
    return "".join(out)

def tail_qafiyah(line: str) -> str:
    """Extract the last letter of the last word as a simple qafiyah (rhyme)."""
    w = line.strip().split()
    return w[-1][-1:] if w else ""
