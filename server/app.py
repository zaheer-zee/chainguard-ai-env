import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from env import ChainGuardEnv
from models import Action
from typing import Optional

app = FastAPI(title="ChainGuard AI OpenEnv")
env = ChainGuardEnv()

class ResetRequest(BaseModel):
    task_id: str = "easy"

@app.get("/")
def home():
    return {"status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/reset")
def reset_env(req: Optional[ResetRequest] = None):
    # If the autograder sends an empty body, default to "easy"
    task_id = req.task_id if req and hasattr(req, 'task_id') else "easy"
    try:
        obs = env.reset(task_id)
        return {"observation": obs.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step")
def step_env(action: Action):
    try:
        obs, reward, is_done, info = env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": reward,
            "done": is_done,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
def state_env():
    return env.state()

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
