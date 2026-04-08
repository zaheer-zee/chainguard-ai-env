import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from env import ChainGuardEnv
from models import Action

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
def reset_env(req: ResetRequest):
    try:
        obs = env.reset(req.task_id)
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
