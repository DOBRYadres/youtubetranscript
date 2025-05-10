import os
import tempfile
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from yt_dlp import YoutubeDL

app = FastAPI()

@app.get("/transcribe")
def transcribe(url: str = Query(..., description="YouTube video URL")):
    """
    Pobierz napisy (auto CC lub oryginalne) z YouTube, zwróć jako tekst/JSON.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitlesformat': 'vtt',
            'outtmpl': os.path.join(tmpdir, '%(id)s'),
            'quiet': True,
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info.get('id')
                subtitles = info.get('subtitles', {})
                auto_captions = info.get('automatic_captions', {})

            # Prefer regular subtitles, fallback to auto CC
            sub_file = None
            lang = None
            # Try to find any subtitles
            if subtitles:
                # Get the first language available
                lang = list(subtitles.keys())[0]
                sub_file = os.path.join(tmpdir, f"{video_id}.{lang}.vtt")
            elif auto_captions:
                lang = list(auto_captions.keys())[0]
                sub_file = os.path.join(tmpdir, f"{video_id}.{lang}.vtt")

            if sub_file and os.path.exists(sub_file):
                with open(sub_file, "r", encoding="utf-8") as f:
                    vtt = f.read()
                # Convert VTT to plain text
                lines = [line for line in vtt.splitlines() if line and not line.startswith("WEBVTT") and not line[0].isdigit() and "-->" not in line]
                text = " ".join(lines)
                return JSONResponse({
                    "text": text.strip(),
                    "language": lang,
                    "source": "subtitles" if subtitles else "auto_cc"
                })
            else:
                raise HTTPException(status_code=404, detail="Brak napisów (auto CC lub oryginalnych) w tym filmie.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"YouTube subtitles error: {e}")
