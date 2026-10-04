"""Détection d'obstacles avec YOLOv8 + estimation de la position spatiale."""
from __future__ import annotations

from dataclasses import dataclass


def get_spatial_position(x_center: float, frame_width: float) -> str:
    """Découpe l'image en 3 zones verticales : gauche / devant / droite."""
    if x_center < frame_width / 3:
        return "à gauche"
    if x_center > 2 * frame_width / 3:
        return "à droite"
    return "devant"


def estimate_proximity(area_ratio: float) -> str:
    """Estimation grossière de la proximité à partir de la taille de la boîte.

    Plus l'objet occupe de surface dans l'image, plus il est proche.
    """
    if area_ratio > 0.25:
        return "très proche"
    if area_ratio > 0.08:
        return "proche"
    return "loin"


@dataclass
class Detection:
    label: str
    confidence: float
    position: str
    proximity: str
    bbox: tuple[float, float, float, float]


class ObstacleDetector:
    """Wrapper léger autour de YOLOv8 (Ultralytics)."""

    def __init__(self, model_path: str = "yolov8n.pt", conf: float = 0.4, classes=None):
        from ultralytics import YOLO  # import tardif : garde les tests rapides

        self.model = YOLO(model_path)
        self.conf = conf
        self.classes = classes  # None = les 80 classes COCO

    def detect(self, frame) -> list[Detection]:
        results = self.model(frame, conf=self.conf, classes=self.classes, verbose=False)
        detections: list[Detection] = []
        for r in results:
            height, width = r.orig_shape[:2]
            for box in r.boxes:
                x1, y1, x2, y2 = (float(v) for v in box.xyxy[0])
                area_ratio = ((x2 - x1) * (y2 - y1)) / (width * height)
                detections.append(
                    Detection(
                        label=self.model.names[int(box.cls[0])],
                        confidence=float(box.conf[0]),
                        position=get_spatial_position((x1 + x2) / 2, width),
                        proximity=estimate_proximity(area_ratio),
                        bbox=(x1, y1, x2, y2),
                    )
                )
        # les obstacles les plus proches d'abord
        order = {"très proche": 0, "proche": 1, "loin": 2}
        detections.sort(key=lambda d: order[d.proximity])
        return detections
