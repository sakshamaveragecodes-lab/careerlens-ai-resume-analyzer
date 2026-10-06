"""Normalize layout noise without erasing technical punctuation."""
import re
import unicodedata


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\x00", "").replace("\u200b", "").replace("\ufeff", "")
    text = text.replace("\u00ad", "").replace("\xa0", " ")
    text = re.sub(r"[\u2010-\u2015]", "-", text)
    text = re.sub(r"(?m)^\s*[-=_*~]{3,}\s*$", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def comparison_text(text: str) -> str:
    return clean_text(text).casefold()
