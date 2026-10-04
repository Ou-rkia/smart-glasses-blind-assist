"""Point d'entrée CLI.

Exemples :
    python -m src.main detect --source 0                 # webcam
    python -m src.main detect --source data/image1.png   # image
    python -m src.main navigate --destination ensias
    python -m src.main navigate --audio data/commande.wav
"""
from __future__ import annotations

import argparse

import cv2

from .audio import Speaker, build_warning
from .detector import ObstacleDetector
from .navigation import DESTINATIONS, extract_destination, navigate, recognize_audio_file


def run_detect(args) -> None:
    detector = ObstacleDetector(args.model, conf=args.conf)
    speaker = Speaker(cooldown=args.cooldown)

    # Image fixe
    if args.source.lower().endswith((".png", ".jpg", ".jpeg")):
        frame = cv2.imread(args.source)
        for d in detector.detect(frame):
            print(f"Obstacle : {d.label} {d.position} ({d.proximity}, {d.confidence:.2f})")
            if not args.mute:
                speaker.speak_once(build_warning(d.label, d.position, d.proximity))
        return

    # Flux vidéo / webcam
    cap = cv2.VideoCapture(int(args.source) if args.source.isdigit() else args.source)
    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        detections = detector.detect(frame)
        for d in detections[: args.max_alerts]:
            if not args.mute:
                speaker.speak_once(build_warning(d.label, d.position, d.proximity))
        if args.show:
            for d in detections:
                x1, y1, x2, y2 = map(int, d.bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{d.label} {d.position}", (x1, y1 - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.imshow("Smart Glasses", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    cap.release()
    cv2.destroyAllWindows()


def run_navigate(args) -> None:
    speaker = Speaker()
    if args.audio:
        text = recognize_audio_file(args.audio)
        print("Texte reconnu :", text)
        target = extract_destination(text)
    else:
        target = args.destination

    if target not in DESTINATIONS:
        speaker.speak("Ma fhemtch l destination")
        raise SystemExit(f"Destination inconnue. Choix : {', '.join(DESTINATIONS)}")
    navigate(target, speaker.speak)


def main() -> None:
    parser = argparse.ArgumentParser(description="Lunettes intelligentes pour malvoyants")
    sub = parser.add_subparsers(dest="command", required=True)

    d = sub.add_parser("detect", help="Détection d'obstacles (YOLOv8)")
    d.add_argument("--source", default="0", help="0 = webcam, ou chemin image/vidéo")
    d.add_argument("--model", default="yolov8n.pt")
    d.add_argument("--conf", type=float, default=0.4)
    d.add_argument("--cooldown", type=float, default=4.0, help="secondes entre deux mêmes alertes")
    d.add_argument("--max-alerts", type=int, default=2, help="alertes max par image")
    d.add_argument("--show", action="store_true", help="afficher la vidéo annotée")
    d.add_argument("--mute", action="store_true", help="désactiver l'audio")
    d.set_defaults(func=run_detect)

    n = sub.add_parser("navigate", help="Guidage vers une destination")
    n.add_argument("--destination", choices=list(DESTINATIONS))
    n.add_argument("--audio", help="fichier audio de la commande vocale")
    n.set_defaults(func=run_navigate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
