from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import os
import subprocess

app = FastAPI()

class AudioRequest(BaseModel):
    url: str  # ссылка на аудиофайл (mp3, mp4, m4a и т.д.)
    start: int = 0  # можно реализовать обрезку по времени
    end: int = 0

@app.post("/transcribe/")
async def transcribe_audio(data: AudioRequest):
    uid = str(uuid.uuid4())
    input_path = f"/tmp/{uid}.input"  # универсальное расширение
    wav_path = f"/tmp/{uid}.wav"

    # 1. Скачивание аудиофайла по ссылке
    try:
        download_cmd = [
            "ffmpeg", "-y",           # -y = overwrite
            "-i", data.url,
            input_path
        ]
        subprocess.run(download_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=f"ffmpeg download error: {e.stderr.decode()}")

    # 2. Конвертация в WAV 16kHz mono
    try:
        convert_cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ar", "16000",           # sample rate
            "-ac", "1",               # mono
            wav_path
        ]
        subprocess.run(convert_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"ffmpeg convert error: {e.stderr.decode()}")

    # 3. Здесь в будущем можно вставить вызов whisper.cpp или curl к серверу
    transcription = f"Файл успешно обработан: {uid}.wav (вставь сюда вызов whisper.cpp)"

    # 4. Удаление временных файлов
    try:
        os.remove(input_path)
        os.remove(wav_path)
    except Exception:
        pass  # не критично, если удалить не получилось

    return {"text": transcription}
