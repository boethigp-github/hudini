import cv2
import logging
from ultralytics import YOLO
from bytetrack.byte_tracker import BYTETracker  # ByteTrack-Tracker importieren

# OpenCV & Logging minimieren
cv2.setLogLevel(0)
logging.getLogger("ultralytics").setLevel(logging.WARNING)

# Kamera-Namen
camera_names = {0: "Internal Webcam", 1: "External USB Camera", 2: "OBS Virtual Cam"}

# Kameras finden
def list_webcams():
    index = 0
    cams = []
    while True:
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            break
        cams.append(index)
        cap.release()
        index += 1
    return cams


# Kameraliste anzeigen
cams = list_webcams()
for cam in cams:
    print(f"[{cam}] - {camera_names.get(cam, f'Camera {cam}')}")

cam_id = int(input("Choose camera ID: "))
if cam_id not in cams:
    exit("Invalid camera!")

# Modell laden – Größere Version für bessere Erkennung
model = YOLO('yolov8m.pt')  # Medium statt Nano

# ByteTrack-Tracker initialisieren
tracker = BYTETracker(track_thresh=0.5, match_thresh=0.8, frame_rate=30)  # Anpassbare Parameter

# Kamera starten
cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

if not cap.isOpened():
    exit(f"Camera {cam_id} not accessible.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Erkennung – Niedrigere Schwelle für mehr Treffer
    results = model(frame, device='cuda', conf=0.2, iou=0.45)  # Vertrauen + IoU-Anpassung

    # Bounding Boxes extrahieren für den Tracker
    detections = []
    for result in results[0].boxes.data:
        x1, y1, x2, y2, score, class_id = result.tolist()
        detections.append([x1, y1, x2, y2, score, int(class_id)])  # ByteTrack benötigt Klassen-IDs

    # Tracker aktualisieren
    tracked_objects = tracker.update(detections, frame.shape)  # Frame-Größe wird übergeben

    # Ergebnisse zeichnen
    for obj in tracked_objects:
        x1, y1, x2, y2, obj_id = [int(v) for v in obj[:5]]  # ByteTrack liefert ID direkt zurück

        # Bounding-Box zeichnen
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f'ID {int(obj_id)}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Ausgabe anzeigen
    cv2.imshow(f'YOLOv8 Detection + ByteTrack - {camera_names.get(cam_id, f"Camera {cam_id}")}', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
