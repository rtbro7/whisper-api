from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import subprocess
import os

app = FastAPI()

class AudioRequest(BaseModel):
    url: str
    filename: str

def is_youtube_url(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url

@app.get("/")
async def root():
    return {"message": "yt-whisper-api is running"}

@app.post("/transcribe/")
async def transcribe_audio(data: AudioRequest):
    uid = str(uuid.uuid4())
    base_path = f"/tmp/{uid}"
    mp4_path = base_path + ".mp4"
    wav_path = base_path + ".wav"
    txt_path = base_path + ".txt"
    model_path = "models/ggml-tiny.bin"
    main_binary_path = "./main"

    if not os.path.exists(main_binary_path):
        raise HTTPException(status_code=500, detail="whisper.cpp бинарник 'main' не найден")
    if not os.path.exists(model_path):
        raise HTTPException(status_code=500, detail="Модель не найдена: models/ggml-tiny.bin")

    # 1. Скачать аудио
    try:
        print("Текущие файлы в директории:", os.listdir("."))

        if is_youtube_url(data.url):
            subprocess.run(
                ["yt-dlp", "--cookies", "cookies.txt", "-f", "bestaudio", "-o", mp4_path, data.url],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            subprocess.run(
                ["ffmpeg", "-y", "-i", data.url, "-vn", mp4_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=f"Download error: {e.stderr.decode()}")

    # 2. Конвертировать в WAV
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp4_path, "-ar", "16000", "-ac", "1", wav_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Convert error: {e.stderr.decode()}")

    # 3. Распознавание
    try:
        subprocess.run(
            [main_binary_path, "-m", model_path, "-f", wav_path, "-otxt", "-of", base_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        with open(txt_path, "r") as f:
            text = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"whisper.cpp error: {str(e)}")

    # 4. Очистка
    for path in [mp4_path, wav_path, txt_path]:
        if os.path.exists(path):
            os.remove(path)

    return {"text": text}
