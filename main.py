from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import subprocess
import os

app = FastAPI()

class AudioRequest(BaseModel):
    url: str

@app.post("/transcribe/")
async def transcribe_audio(data: AudioRequest):
    uid = str(uuid.uuid4())
    mp4_path = f"/tmp/{uid}.mp4"
    wav_path = f"/tmp/{uid}.wav"
    txt_path = f"/tmp/{uid}.txt"

    # 1. Скачать аудио (поддержка mp3/mp4 ссылок)
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", data.url, "-vn", mp4_path],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=f"ffmpeg download error: {e.stderr.decode()}")

    # 2. Конвертация в WAV 16kHz mono
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp4_path, "-ar", "16000", "-ac", "1", wav_path],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"ffmpeg convert error: {e.stderr.decode()}")

    # 3. Вызов whisper.cpp бинарника
    try:
        subprocess.run(
            ["./main", "-m", "models/ggml-tiny.bin", "-f", wav_path, "-otxt", "-of", txt_path.replace(".txt", "")],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        with open(txt_path, "r") as f:
            text = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Whisper error: {str(e)}")

    # 4. Удаление временных файлов
    for file in [mp4_path, wav_path, txt_path]:
        if os.path.exists(file):
            os.remove(file)

    return {"text": text}
