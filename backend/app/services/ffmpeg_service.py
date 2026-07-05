import subprocess
import shutil
from pathlib import Path

def extract_audio(video_path: Path) -> Path:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed or not found in system PATH")

    # The transcripts folder is at the same level as uploads
    base_dir = video_path.parent.parent
    transcripts_dir = base_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    
    # Save audio in transcripts folder with the same UUID
    audio_filename = f"{video_path.stem}.mp3"
    audio_path = transcripts_dir / audio_filename

    command = [
        "ffmpeg",
        "-i", str(video_path),
        "-q:a", "0",
        "-map", "a",
        str(audio_path),
        "-y" # Overwrite output if it exists
    ]
    
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed with error: {e.stderr.decode()}")
    except Exception as e:
        raise RuntimeError(f"FFmpeg execution failed: {str(e)}")

    return audio_path
