from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from pytube import YouTube
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Konfiguracja CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Strona główna
@app.get("/check_video/{video_id}")
async def check_video(video_id: str):
    """
    Sprawdza dostępność filmu na YouTube.
    Zwraca informacje o filmie i dostępnych transkrypcjach.
    """
    try:
        # Pobierz informacje o filmie
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        
        # Pobierz dostępne transkrypcje
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcripts = [{
                'language': t.language,
                'language_code': t.language_code,
                'is_generated': t.is_generated
            } for t in transcript_list]
            has_transcripts = True
        except Exception as e:
            transcripts = []
            has_transcripts = False
        
        return {
            'video_id': video_id,
            'title': yt.title,
            'length': yt.length,
            'views': yt.views,
            'author': yt.author,
            'publish_date': str(yt.publish_date) if yt.publish_date else None,
            'is_age_restricted': yt.age_restricted,
            'has_transcripts': has_transcripts,
            'available_transcripts': transcripts
        }
        
    except Exception as e:
        error_msg = f"Nie można pobrać informacji o filmie: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

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
async def get_transcript(
    request: Request,
    video_id: str = Query(..., description="YouTube video ID"),
    lang: str = Query("en", description="Kod języka (np. 'pl', 'en')")
):
    """
    Zwraca napisy (transkrypt) dla podanego ID filmu na YouTube w formacie JSON.
    """
    logger.info(f"Pobieranie transkrypcji dla filmu {video_id} (język: {lang})")
    
    try:
        # Pobierz listę dostępnych transkrypcji
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Spróbuj pobrać transkrypcję w żądanym języku
        try:
            transcript = transcript_list.find_transcript([lang])
        except:
            # Jeśli nie ma w żądanym języku, użyj domyślnego
            transcript = transcript_list.find_transcript(["en"])
        
        # Pobierz transkrypcję
        transcript_data = transcript.fetch()
        
        # Logowanie sukcesu (bez wyświetlania pełnych danych)
        logger.info(f"Pobrano transkrypcję dla filmu {video_id} (język: {transcript.language_code})")
        
        return JSONResponse({
            "video_id": video_id,
            "language": transcript.language_code,
            "transcript": transcript_data
        })
        
    except TranscriptsDisabled:
        error_msg = f"Transkrypcje są wyłączone dla filmu {video_id}"
        logger.warning(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)
        
    except NoTranscriptFound:
        error_msg = f"Brak dostępnych transkryptów dla filmu {video_id}"
        logger.warning(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)
        
    except VideoUnavailable as e:
        error_msg = f"Film {video_id} jest niedostępny lub nie można go odtworzyć. Możliwe przyczyny:\n"
        error_msg += "1. Film został usunięty lub jest prywatny\n"
        error_msg += "2. Są ograniczenia geograficzne\n"
        error_msg += "3. YouTube blokuje żądania z tego serwera\n\n"
        error_msg += f"Szczegóły: {str(e)}"
        logger.warning(f"VideoUnavailable dla {video_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=error_msg)
        
    except Exception as e:
        error_msg = f"Wewnętrzny błąd serwera: {str(e)}"
        logger.error(f"Błąd dla filmu {video_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)
