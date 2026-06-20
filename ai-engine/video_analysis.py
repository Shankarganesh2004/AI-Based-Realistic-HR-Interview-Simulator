"""
AI Engine – Video-based emotion/confidence analysis using OpenCV + DeepFace.

This module can run standalone or be imported by the backend.
It processes video frames and returns emotion & confidence scores.
"""

import base64
import io
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False


def analyze_frame_base64(frame_b64: str) -> dict:
    """Analyze a base64-encoded video frame for emotions and confidence."""
    if not CV2_AVAILABLE:
        return _fallback_scores()

    try:
        img_bytes = base64.b64decode(frame_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return analyze_frame(frame)
    except Exception as e:
        print(f"Frame analysis error: {e}")
        return _fallback_scores()


def analyze_frame(frame) -> dict:
    """Analyze a CV2 frame for emotions and confidence."""
    if not DEEPFACE_AVAILABLE or frame is None:
        return _fallback_scores()

    try:
        results = DeepFace.analyze(
            frame,
            actions=["emotion"],
            enforce_detection=False,
            silent=True,
        )
        if isinstance(results, list):
            results = results[0]

        emotions = results.get("dominant_emotion", "neutral")
        emotion_scores = results.get("emotion", {})

        # Calculate confidence score based on emotions
        confidence = _compute_confidence(emotion_scores)
        emotion_stability = _compute_stability(emotion_scores)

        return {
            "dominant_emotion": emotions,
            "emotion_scores": emotion_scores,
            "confidence_score": confidence,
            "emotion_stability": emotion_stability,
            "eye_contact": _estimate_eye_contact(frame),
        }
    except Exception as e:
        print(f"DeepFace analysis error: {e}")
        return _fallback_scores()


def _compute_confidence(emotions: dict) -> float:
    """Estimate confidence from emotion distribution."""
    happy = emotions.get("happy", 0)
    neutral = emotions.get("neutral", 0)
    fear = emotions.get("fear", 0)
    sad = emotions.get("sad", 0)
    angry = emotions.get("angry", 0)

    # Confidence: high happy/neutral, low fear/sad
    positive = happy * 0.4 + neutral * 0.3
    negative = fear * 0.5 + sad * 0.3 + angry * 0.2
    score = max(0, min(100, 50 + positive - negative))
    return round(score, 1)


def _compute_stability(emotions: dict) -> float:
    """Compute emotion stability – lower variance = more stable."""
    if not emotions:
        return 50.0
    values = list(emotions.values())
    variance = np.var(values) if values else 0
    # Lower variance → higher stability
    stability = max(0, min(100, 100 - variance * 0.5))
    return round(stability, 1)


def _estimate_eye_contact(frame) -> float:
    """Basic eye contact estimation using face detection."""
    if not CV2_AVAILABLE:
        return 50.0
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) > 0:
            return 80.0  # Face detected, likely looking at camera
        return 30.0  # No face detected
    except Exception:
        return 50.0


def _fallback_scores() -> dict:
    return {
        "dominant_emotion": "neutral",
        "emotion_scores": {},
        "confidence_score": 50.0,
        "emotion_stability": 50.0,
        "eye_contact": 50.0,
    }


if __name__ == "__main__":
    print("AI Engine – Video Analysis Module")
    print("Dependencies:")
    print(f"  OpenCV: {'✅' if CV2_AVAILABLE else '❌'}")
    print(f"  DeepFace: {'✅' if DEEPFACE_AVAILABLE else '❌'}")
