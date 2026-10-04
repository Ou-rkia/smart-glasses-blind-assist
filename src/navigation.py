"""Navigation guidée par la voix : destination, distance GPS, retours audio."""
from __future__ import annotations

import math
import time
from typing import Callable

DESTINATIONS = {
    "ensias": (33.97084617376773, -6.870530384223207),
    "madinat al irfane": (33.98158045522268, -6.863130018925147),
    "marjane hay riad": (33.95664244102765, -6.848360174852717),
    "mosquee assounna": (34.01598429985946, -6.833034031234839),
}

# Variantes fréquentes de mauvaise reconnaissance vocale
ENSIAS_ALIASES = ["ensias", "encias", "ncias", "dacia", "sia"]


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance en mètres entre deux points GPS."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def extract_destination(text: str) -> str | None:
    text = text.lower()
    if any(alias in text for alias in ENSIAS_ALIASES):
        return "ensias"
    for place in DESTINATIONS:
        if place in text:
            return place
    return None


def recognize_audio_file(path: str, language: str = "fr-FR") -> str:
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio, language=language).lower()


def recognize_microphone(language: str = "fr-FR", timeout: int = 6) -> str:
    import speech_recognition as sr  # nécessite PyAudio

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=timeout)
    return recognizer.recognize_google(audio, language=language).lower()


class SimulatedGPS:
    """GPS simulé (démo). Remplacer par un module réel (voir README)."""

    def __init__(self, lat: float = 33.9650, lon: float = -6.8750, step: float = 0.00005):
        self.lat, self.lon, self.step = lat, lon, step

    def __call__(self) -> tuple[float, float]:
        self.lat += self.step
        self.lon += self.step
        return self.lat, self.lon


def navigate(
    target: str,
    speak: Callable[[str, str], None],
    get_position: Callable[[], tuple[float, float]] | None = None,
    interval: float = 3.0,
) -> None:
    """Boucle de guidage : message selon la distance restante."""
    get_position = get_position or SimulatedGPS()
    dest_lat, dest_lon = DESTINATIONS[target]
    speak(f"Navigation vers {target}", "fr")

    while True:
        lat, lon = get_position()
        dist = haversine(lat, lon, dest_lat, dest_lon)
        print(f"Distance : {int(dist)} m")

        if dist > 50:
            speak("سير نيشان", "ar")
        elif dist > 15:
            speak("راك قربتي", "ar")
        elif dist > 5:
            speak("وصلتي تقريبا", "ar")
        else:
            speak("وصلتي للبلاصة", "ar")
            return
        time.sleep(interval)
