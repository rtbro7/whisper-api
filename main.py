from fastapi import FastAPI, UploadFile, File
import subprocess
import tempfile
import os

app = FastAPI()

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    output_path = tmp_path + ".txt"

    result = subprocess.run([
        "./main",
        "-m", "models/ggml-tiny.bin",
        "-f", tmp_path,
        "-otxt"
    ], capture_output=True)

    if not os.path.exists(output_path):
        return {"error": "Transcription failed", "stderr": result.stderr.decode()}

    with open(output_path, "r") as f:
        text = f.read()

    return {"text": text}
