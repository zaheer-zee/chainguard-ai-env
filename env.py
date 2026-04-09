from typing import Dict, Any, Tuple
import yaml
from models import Observation, Action, Reward
from graders import grade_task

class ChainGuardEnv:
    def __init__(self):
        with open("tasks.yaml", "r") as f:
            self.tasks = yaml.safe_load(f)
        self.current_task_id = None
        self.history = []
        self.step_count = 0
        self.is_done = False

    def reset(self, task_id: str = "easy") -> Observation:
        if task_id not in self.tasks:
            raise ValueError(f"Unknown task {task_id}")
        self.current_task_id = task_id
        self.history = []
        self.step_count = 0
        self.is_done = False
        
        task_data = self.tasks[task_id]
        return Observation(
            task_id=task_id,
            scan_report=task_data["scan_report"],
            manifest_content=task_data["manifest_content"],
            query_result=None,
            feedback=None
        )

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        if self.is_done:
            raise RuntimeError("Episode is already done. Call reset().")
            
        self.step_count += 1
        reward_obj = grade_task(self.current_task_id, action, self.history)
        self.history.append(action)
        
        task_data = self.tasks[self.current_task_id]
        obs = Observation(
            task_id=self.current_task_id,
            scan_report=task_data["scan_report"],
            manifest_content=task_data["manifest_content"],
            query_result=None,
            feedback=reward_obj.message
        )
        
        if self.step_count >= 10:
            self.is_done = True
            obs.feedback += " (Max steps reached)"
            return obs, 0.01, self.is_done, {"message": "Episode limit reached."}
            
        if action.action_type == "query_cve":
            if action.target == "CVE-2022-12345":
                obs.query_result = "NVD Database: CVE-2022-12345 strictly affects legacyAuth(). Verify implementation."
            else:
                obs.query_result = f"NVD Database: No specific context found for {action.target}."

        self.is_done = reward_obj.is_done
        return obs, reward_obj.score, self.is_done, {"message": reward_obj.message}

    def state(self) -> Dict[str, Any]:
        return {
            "task_id": self.current_task_id,
            "step_count": self.step_count,
            "history": [a.model_dump() for a in self.history],
            "is_done": self.is_done
        }
