"""Synthèse vocale (gTTS) avec anti-répétition des alertes."""
from __future__ import annotations

import os
import tempfile
import time

from gtts import gTTS

# Traduction des classes COCO -> Darija (translittération)
LABELS_DARIJA = {
    "person": "Bnadm",
    "car": "Tomobil",
    "bus": "Car",
    "truck": "Camion",
    "bicycle": "Bicyclette",
    "motorcycle": "Motor",
    "chair": "Koursi",
    "bench": "Banc",
    "dog": "Kelb",
    "cat": "Qetta",
    "traffic light": "Dow dial trafik",
    "stop sign": "Panneau stop",
    "potted plant": "Nebta",
}

POSITIONS_DARIJA = {
    "à gauche": "f'lyessar",
    "à droite": "f'lyemman",
    "devant": "goddamek",
}


def build_warning(label: str, position: str, proximity: str | None = None, darija: bool = True) -> str:
    if darija:
        text = f"{LABELS_DARIJA.get(label, label)} {POSITIONS_DARIJA[position]}"
    else:
        text = f"{label} {position}"
    if proximity == "très proche":
        text += " , attention"
    return text


class Speaker:
    def __init__(self, lang: str = "fr", cooldown: float = 4.0):
        self.lang = lang
        self.cooldown = cooldown
        self._last_spoken: dict[str, float] = {}

    def speak(self, text: str, lang: str | None = None, wait: bool = True) -> None:
        """Lit `text` à voix haute. `lang='ar'` pour du texte en écriture arabe."""
        path = os.path.join(tempfile.gettempdir(), "sg_voice.mp3")
        gTTS(text=text, lang=lang or self.lang).save(path)
        self._play(path, wait)

    def speak_once(self, text: str, lang: str | None = None) -> bool:
        """Parle seulement si ce message n'a pas été dit depuis `cooldown` secondes."""
        now = time.time()
        if now - self._last_spoken.get(text, 0) < self.cooldown:
            return False
        self._last_spoken[text] = now
        self.speak(text, lang)
        return True

    @staticmethod
    def _play(path: str, wait: bool) -> None:
        try:
            import pygame

            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while wait and pygame.mixer.music.get_busy():
                time.sleep(0.05)
        except Exception as exc:  # pas de carte son (serveur, CI...)
            print(f"[audio] lecture impossible ({exc}) -> fichier : {path}")
