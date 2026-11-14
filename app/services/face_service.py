import cv2

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def detect_faces_mediapipe(image_bgr):
    if image_bgr is None:
        return False, 0

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return False, 0

    h, w = image_bgr.shape[:2]
    area = sum([fw * fh for (x, y, fw, fh) in faces])

    return True, (area / (h * w)) * 100