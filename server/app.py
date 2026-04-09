import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, HTTPException, Body
from typing import Any, Dict, Optional
from env import ChainGuardEnv
from models import Action

app = FastAPI(title="ChainGuard AI OpenEnv")
env = ChainGuardEnv()

@app.get("/")
def home():
    return {"status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/reset")
def reset_env(body: Dict[str, Any] = Body(default={})):
    """Reset the environment. Accepts optional task_id (defaults to 'easy')."""
    task_id = body.get("task_id", "easy") if body else "easy"
    try:
        obs = env.reset(task_id)
        return {"observation": obs.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step")
def step_env(body: Dict[str, Any] = Body(...)):
    """
    Step the environment.

    Accepts two formats:
    1. Direct: {"action_type": "resolve", "justification": "..."}
    2. Wrapped (OpenEnv client format): {"action": {"action_type": "resolve", ...}, "timeout_s": 15}
    """
    try:
        # Handle both direct and wrapped action formats
        if "action" in body:
            action_data = body["action"]
        else:
            action_data = {k: v for k, v in body.items() if k != "timeout_s"}

        action = Action(**action_data)
        obs, reward, is_done, info = env.step(action)

        # Clamp reward defensively to be strictly within (0, 1)
        reward = max(0.01, min(0.99, float(reward)))

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
