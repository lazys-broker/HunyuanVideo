from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import uuid

app = FastAPI()

class PromptInput(BaseModel):
    prompt: str

@app.post("/generate")
def generate_video(data: PromptInput):
    prompt = data.prompt
    output_id = str(uuid.uuid4())
    output_dir = f"outputs/{output_id}"
    os.makedirs(output_dir, exist_ok=True)

    try:
        # This command should call HunyuanVideo's inference entrypoint
        subprocess.run([
            "python3", "inference.py",
            "--prompt", prompt,
            "--output_dir", output_dir
        ], check=True)

        # Get first output video file
        video_path = None
        for file in os.listdir(output_dir):
            if file.endswith(".mp4"):
                video_path = f"{output_dir}/{file}"
                break

        if not video_path:
            raise FileNotFoundError("No video generated")

        return {"id": output_id, "video_url": f"/{video_path}"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
