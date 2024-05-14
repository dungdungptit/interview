"""Main entrypoint for the app."""

import asyncio
from typing import Optional, Union
from uuid import UUID
from chain import xu_ly_video
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
import os
from typing import List
from fastapi import File, UploadFile

origins = ["*"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

static_folder = "Data"
app.mount("/static", StaticFiles(directory=static_folder), name="static")


class SendFeedbackBody(BaseModel):
    run_id: UUID
    key: str = "user_score"

    score: Union[float, int, bool, None] = None
    feedback_id: Optional[UUID] = None
    comment: Optional[str] = None


class UpdateFeedbackBody(BaseModel):
    feedback_id: UUID
    score: Union[float, int, bool, None] = None
    comment: Optional[str] = None


# TODO: Update when async API is available
async def _arun(func, *args, **kwargs):
    return await asyncio.get_running_loop().run_in_executor(None, func, *args, **kwargs)


class GetTraceBody(BaseModel):
    run_id: UUID


class DataChat(BaseModel):
    text: str
    prompt: str | None = None


@app.post("/virtual_interview_2")
async def virtual_interview_2(files: List[UploadFile] = File(...)):
    import os

    current_dir = os.getcwd()
    os.chdir("Data")
    for file in files:
        file.filename = current_dir + "/Data/" + file.filename

    for file in files:
        try:
            contents = file.file.read()
            with open(file.filename, "wb") as f:
                f.write(contents)
        except Exception:
            return {"message": "There was an error uploading the file(s)"}
        finally:
            file.file.close()
    list_filename = [file.filename for file in files]
    try:
        res = xu_ly_video(list_filename)
    except Exception as e:
        return {"message": f"Error processing files: {e}"}

    emotions = ["anger", "contempt", "disgust", "fear", "happy", "sadness", "surprise"]
    return {
        "message": f"Successfuly uploaded {[file.filename for file in files]}",
        "result": res,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
