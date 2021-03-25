from fastapi import FastAPI, File, UploadFile, Body
from git import Repo
import os
import shutil

workspace = "workspace"
repo = os.path.join(workspace, ".git")

gitrepo = None
if not os.path.exists(repo):
    gitrepo = Repo.init(repo, bare=True)
    gitrepo.create_head("master", force=True)
else:
    gitrepo = Repo(repo)



app = FastAPI(title="Configuration File Backups")

@app.get("/")
async def read_index():
    return {"dirty": gitrepo.is_dirty(untracked_files=True), "active_branch": gitrepo.active_branch.name }

@app.post("/")
def upload_file(file: UploadFile = File(...), directory: str = Body(...)):
    print(directory)
    dest_dir = os.path.abspath(os.path.join(workspace, directory))
    print(dest_dir)
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    
    with open(os.path.join(dest_dir, file.filename), "wb+") as upload_file:
        shutil.copyfileobj(file.file, upload_file)


    if gitrepo.is_dirty(untracked_files=True):
        gitrepo.index.add(gitrepo.untracked_files)
        changedFiles = [item.a_path for item in gitrepo.index.diff(None)]
        gitrepo.index.add(changedFiles)

        gitrepo.index.commit(f"adds {os.path.join(directory,file.filename)}")


    return {
        "repo_dirty": gitrepo.is_dirty(),
    }