from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Body
from starlette.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from git import Repo, Actor
from pathlib import Path
import os
import shutil

# define the location of the workspace 
# and repo
workspace = "workspace"
repo = os.path.join(workspace, ".git")

# initialize the repo
gitrepo = None
if not os.path.exists(repo):
    gitrepo = Repo.init(repo, bare=True)
    gitrepo.create_head("master", force=True)
else:
    gitrepo = Repo(repo)

# The app for file controller
app = FastAPI(title="Configuration File Backups")
app.mount("/downloads", StaticFiles(directory="workspace"), name="downloads")
app.mount("/app", StaticFiles(directory="frontend/build"), name="app")
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="app-static")

@app.get("/status")
async def read_index():
    return {"dirty": gitrepo.is_dirty(untracked_files=True), "active_branch": gitrepo.active_branch.name }

@app.post("/upload")
async def upload_file(directory: Optional[str] = Body(...), files: List[UploadFile] = File(...)):

    # create the destination directory
    dest_dir = os.path.abspath(os.path.join(workspace, directory))
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    # copy all the files into their locations
    for f in files:
        with open(os.path.join(dest_dir, f.filename), "wb+") as upload_file:
            shutil.copyfileobj(f.file, upload_file)

    return {
        "received_files_count": len(files),
        "received_files_names": [ f.filename for f in files ],
        "changed": gitrepo.is_dirty(untracked_files=True)
    }

@app.post("/add-and-commit")
async def add_to_index(author_name: Optional[str] = Body(...), author_email: Optional[str] = Body(...), msg: Optional[str] = None):
    if gitrepo.is_dirty(untracked_files=True):
        # add the changed files to the index for this commit
        changedFiles = [item.a_path for item in gitrepo.index.diff(None)]
        
        # create a status message
        num_changed_files = len(changedFiles)
        num_new_files = len(gitrepo.untracked_files)
        if msg is None:
            msg = f"adds {num_changed_files} changed and {num_new_files} new files to repo"

        # add changed and new files to index for commit
        gitrepo.index.add(gitrepo.untracked_files)
        gitrepo.index.add(changedFiles)

        # set author and committer
        committer = Actor("file-repo", "feoautomation@cox.com")
        if author_email is None:
            author_email = "feoautomation@cox.com"
        if author_name is None:
            author_name = "file-repo"

        author = Actor(f"{author_name}", f"{author_email}")

        gitrepo.index.commit(msg, author=author, committer=committer)

        return {
            "num_changed_files": num_changed_files,
            "num_new_files": num_new_files,
            "changed": (num_new_files > 0 or num_changed_files > 0) 
        }

@app.get("/web/{rest_of_path:path}")
async def read_workspace(rest_of_path: Optional[str] = None):
    read_path = os.path.join(workspace, rest_of_path)

    if os.path.isfile(read_path):
        return FileResponse(read_path, media_type="text/plain")
    path_parent = str(Path(read_path).parent)[len(workspace):] + '/'

    listing = {}
    listing["path"], listing["directories"], listing["files"] = next(os.walk(read_path))
    listing['path_parent'] = path_parent

    # filter out the .git directory
    listing['directories'] = [ directory for directory in listing['directories'] if directory != ".git" ]
    
    # remove the workspace dir from path
    listing['path'] = listing['path'][len(workspace):]
    # create a url pass back here
    listing['url'] = "/web" + listing['path']

    file_data = []
    for f in listing['files']:
        file = {
            "name": f,
            "stat_result": os.stat(os.path.join(read_path, f))[6:]
        }
        file_data.append(file)
    
    listing['files'] = file_data
    file_data = None

    return listing
