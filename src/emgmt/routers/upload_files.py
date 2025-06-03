from fastapi import APIRouter, File, UploadFile, Form

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/single_file/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    with open(file.filename, "wb") as f:
        f.write(content)
    return {"filename": file.filename}


@router.post("/multiple_files/")
async def upload_files(files: list[UploadFile] = File(...)):
    filenames = []
    for file in files:
        content = await file.read()
        with open(file.filename, "wb") as f:
            f.write(content)
        filenames.append(file.filename)
    return {"filenames": filenames}


@router.post("/files_and_forms/")
async def create_file(
    file: bytes = File(), fileb: UploadFile = File(), token: str = Form()
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }
