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


@app.post("/feedback")
async def send_feedback(body: SendFeedbackBody):
    client.create_feedback(
        body.run_id,
        body.key,
        score=body.score,
        comment=body.comment,
        feedback_id=body.feedback_id,
    )
    return {"result": "posted feedback successfully", "code": 200}


class UpdateFeedbackBody(BaseModel):
    feedback_id: UUID
    score: Union[float, int, bool, None] = None
    comment: Optional[str] = None


@app.patch("/feedback")
async def update_feedback(body: UpdateFeedbackBody):
    feedback_id = body.feedback_id
    if feedback_id is None:
        return {
            "result": "No feedback ID provided",
            "code": 400,
        }
    client.update_feedback(
        feedback_id,
        score=body.score,
        comment=body.comment,
    )
    return {"result": "patched feedback successfully", "code": 200}


# TODO: Update when async API is available
async def _arun(func, *args, **kwargs):
    return await asyncio.get_running_loop().run_in_executor(None, func, *args, **kwargs)


async def aget_trace_url(run_id: str) -> str:
    for i in range(5):
        try:
            await _arun(client.read_run, run_id)
            break
        except langsmith.utils.LangSmithError:
            await asyncio.sleep(1**i)

    if await _arun(client.run_is_shared, run_id):
        return await _arun(client.read_run_shared_link, run_id)
    return await _arun(client.share_run, run_id)


class GetTraceBody(BaseModel):
    run_id: UUID


@app.post("/get_trace")
async def get_trace(body: GetTraceBody):
    run_id = body.run_id
    if run_id is None:
        return {
            "result": "No LangSmith run ID provided",
            "code": 400,
        }
    return await aget_trace_url(str(run_id))


@app.get("/preprocess")
async def preprocess(text: str):
    text = normalize_replace_abbreviation_text(text)
    return {"result": "preprocessed successfully", "code": 200, "text": text}


class DataChat(BaseModel):
    text: str
    prompt: str | None = None


@app.post("/virtual_interview")
async def virtual_interview(files: List[UploadFile] = File(...)):
    for file in files:
        try:
            contents = file.file.read()
            with open(file.filename, 'wb') as f:
                f.write(contents)
        except Exception:
            return {"message": "There was an error uploading the file(s)"}
        finally:
            file.file.close()

    return {"message": f"Successfuly uploaded {[file.filename for file in files]}"}

@app.post("/virtual_interview_2")
async def virtual_interview_2(files: List[UploadFile] = File(...)):
    for file in files:
        try:
            contents = file.file.read()
            with open(file.filename, 'wb') as f:
                f.write(contents)
        except Exception:
            return {"message": "There was an error uploading the file(s)"}
        finally:
            file.file.close()

    return {"message": f"Successfuly uploaded {[file.filename for file in files]}", "similarity": 76}

@app.post("/emoji")
async def emoji():
    return {"result": {'extroversion': 70, 'neurotic':5, 'agreeable':6, 'conscientious':9, 'open':10}}

@app.get("/prep_output")
async def prep_output(text: str):
    text = normalize_replace_abbreviation_text(text)
    sources = get_source(text)
    """ 
    {"sources": [{
      "page_content": "Chỉ tiêu tuyển sinh đại học Ngoại thương (FTU) năm 2024\n\nTổng chỉ tiêu tuyển sinh 2024 của trường là 4130 gồm:\n\n1. Tổng chỉ tiêu tuyển sinh Trụ sở chính Hà Nội là 3080\n\n2. Tổng chỉ tiêu tuyển sinh CS Quảng Ninh là 100\n\n3. Tổng chỉ tiêu tuyển sinh Cơ sở II-TP Hồ Chí Minh là 950\n\nChi tiết chỉ tiêu tuyển sinh từng ngành/ nhóm ngành tại từng cơ sở theo từng phương thức xét tuyển:\n\n1. chỉ tiêu tuyển sinh Xét tuyển riêng PT3 và đặc thù tại Trụ sở chính Hà Nội (Mã ngành/ nhóm ngành xét tuyển: NTH409,",
      "metadata": {
        "source": "Đề án tuyển sinh 2024 (dự thảo 2)\\245.txt"
      },
      "type": "Document"
    }]}
       """
    list_sources = []
    for source in sources:
        # print(source)
        source.metadata = {"source": static_folder + "/" + source.metadata["source"]}
        list_sources.append(source.metadata["source"])
    return {
        "result": "preprocessed successfully",
        "code": 200,
        "list_sources": list_sources,
        "text": text,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
