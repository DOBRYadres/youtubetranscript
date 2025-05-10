# YouTube Auto CC Transcript API

Aplikacja FastAPI do pobierania automatycznych transkrypcji (auto cc) z filmów YouTube przez endpoint API. Transkrypcja działa automatycznie w dowolnym języku (Whisper).

## Instalacja

1. Zainstaluj zależności:

```bash
pip install -r requirements.txt
```

2. Uruchom serwer:

```bash
uvicorn main:app --reload
```

## Użycie

Wywołaj endpoint:

```
GET /transcribe?url=YOUTUBE_URL
```

Przykład:

```
curl 'http://localhost:8000/transcribe?url=https://www.youtube.com/watch?v=ID'
```

Zwraca transkrypcję w formacie JSON.

## Wymagania

- Python 3.8+
- ffmpeg (musi być zainstalowany w systemie)

## Notatki
- Transkrypcja działa automatycznie dla dowolnego języka.
- Endpoint można wywoływać z narzędzi typu N8N.
