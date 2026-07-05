from pathlib import Path
from faster_whisper import WhisperModel

# Use the base model
model_size = "base"
# Omit device to use auto selection (works for CPU and GPU)
model = WhisperModel(model_size, device="cpu", compute_type="int8")

def transcribe(audio_path: Path) -> list:
    segments, info = model.transcribe(str(audio_path), beam_size=5)
    
    result = []
    for segment in segments:
        result.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })
    return result
