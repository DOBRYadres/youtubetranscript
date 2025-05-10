from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

app = FastAPI()

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
