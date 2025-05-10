from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

app = FastAPI()

# Strona główna
@app.get("/")
def home():
    return HTMLResponse("""
    <html>
      <head>
        <title>YouTube Transcript API</title>
        <style>
          body { font-family: Arial, sans-serif; background: #f7f7f7; margin: 0; padding: 0; }
          .center { text-align: center; margin-top: 15vh; }
          h1 { color: #c4302b; font-size: 2.6em; }
          .docs { max-width: 800px; margin: 2em auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        </style>
      </head>
      <body>
        <div class="center">
          <h1>YouTube Transcript API</h1>
          <p>Proste API do pobierania napisów z filmów YouTube</p>
        </div>
        <div class="docs">
          <h2>Dokumentacja</h2>
          <p>Użyj endpointu <code>/transcript?video_id=ID_FILMU</code> aby pobrać transkrypcję.</p>
          <p>Przykład: <code>https://youtube-transcript-pf84.onrender.com/transcript?video_id=dQw4w9WgXcQ</code></p>
        </div>
      </body>
    </html>
    """)

# Endpoint do pobierania transkrypcji
@app.get("/transcript")
def get_transcript(video_id: str = Query(..., description="YouTube video ID")):
    """
    Zwraca napisy (transkrypt) dla podanego ID filmu na YouTube w formacie JSON.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return JSONResponse(transcript)
    except TranscriptsDisabled:
        raise HTTPException(status_code=404, detail="Transkrypcje są wyłączone dla tego filmu.")
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="Brak dostępnych transkryptów dla tego filmu.")
    except VideoUnavailable:
        raise HTTPException(status_code=404, detail="Film jest niedostępny.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Błąd: {e}")
