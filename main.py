from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def home():
    return HTMLResponse("""
    <html>
      <head>
        <title>YouTube Transcript</title>
        <style>
          body { font-family: Arial, sans-serif; background: #f7f7f7; margin: 0; padding: 0; }
          .center { text-align: center; margin-top: 15vh; }
          h1 { color: #c4302b; font-size: 2.6em; }
        </style>
      </head>
      <body>
        <div class="center">
          <h1>YouTube Transcript</h1>
          <p>API do pobierania napisów z filmów YouTube</p>
        </div>
      </body>
    </html>
    """)
                