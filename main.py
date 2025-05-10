import os
import tempfile
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from yt_dlp import YoutubeDL
import whisper

app = FastAPI()

# Whisper model (load once)
model = whisper.load_model("base")

@app.get("/transcribe")
def transcribe(url: str = Query(..., description="YouTube video URL")):
    """
    Download audio from YouTube, transcribe using Whisper, return transcript.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.mp3")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_path,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"YouTube download error: {e}")

        try:
            result = model.transcribe(audio_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Transcription error: {e}")

        return JSONResponse({
            "text": result["text"],
            "segments": result.get("segments", []),
            "language": result.get("language", "unknown")
        })
