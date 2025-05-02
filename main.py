from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import os
import subprocess

app = FastAPI()

class AudioRequest(BaseModel):
    url: str
    start: int = 0
    end: int = 0

@app.post("/transcribe/")
async def transcribe_audio(data: AudioRequest):
    uid = str(uuid.uuid4())
    mp3_path = f"/tmp/{uid}.mp3"
    wav_path = f"/tmp/{uid}.wav"

    # 1. Скачать mp3 файл
    try:
        download_cmd = [
            "ffmpeg", "-y",
            "-i", data.url,
            mp3_path
        ]
        subprocess.run(download_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=f"ffmpeg download error: {e.stderr.decode()}")

    # 2. Конвертировать в WAV 16kHz mono (если нужно whisper.cpp)
    try:
        convert_cmd = [
            "ffmpeg", "-y",
            "-i", mp3_path,
            "-ar", "16000",
            "-ac", "1",
            wav_path
        ]
        subprocess.run(convert_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"ffmpeg convert error: {e.stderr.decode()}")

    # 3. TODO: Вставь сюда вызов whisper.cpp, если готов
    transcription = f"Файл скачан и подготовлен: {uid}.wav"

    # 4. Очистка
    os.remove(mp3_path)
    os.remove(wav_path)

    return {"text": transcription}
