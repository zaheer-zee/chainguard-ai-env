from models import Action, ActionType, Reward
from typing import List

def grade_easy(action: Action) -> Reward:
    if action.action_type == ActionType.update_dependency:
        if action.target == "lodash" and action.version == "4.17.21":
            return Reward(score=0.85, is_done=True, message="Successfully bumped lodash to secure version.")
        else:
            return Reward(score=0.15, is_done=True, message="Incorrect package or version chosen.")
    elif action.action_type == ActionType.resolve:
        return Reward(score=0.05, is_done=True, message="Resolved without taking action.")
    return Reward(score=0.01, is_done=False, message="Invalid action for this task.")

def grade_medium(action: Action) -> Reward:
    if action.action_type == ActionType.change_base_image:
        if action.target == "alpine" and action.version == "3.18":
            return Reward(score=0.85, is_done=True, message="Successfully changed base image to secure version.")
        else:
            return Reward(score=0.15, is_done=True, message="Incorrect image or version chosen.")
    elif action.action_type == ActionType.resolve:
        return Reward(score=0.05, is_done=True, message="Resolved without taking action.")
    return Reward(score=0.01, is_done=False, message="Invalid action for this task.")

def grade_hard(action: Action, history: List[Action]) -> Reward:
    query_count = sum(1 for a in history if a.action_type == ActionType.query_cve and a.target == "CVE-2022-12345")
    if action.action_type == ActionType.query_cve:
        if action.target == "CVE-2022-12345":
            if query_count == 0:
                return Reward(score=0.25, is_done=False, message="CVE details queried. Function 'legacyAuth()' is affected. Check codebase.")
            return Reward(score=0.01, is_done=False, message="Already queried.")
        return Reward(score=0.01, is_done=False, message="Invalid CVE target.")
        
    has_queried = query_count > 0
    
    if action.action_type == ActionType.ignore_vulnerability:
        if action.target == "CVE-2022-12345":
            if has_queried:
                return Reward(score=0.65, is_done=True, message="Correctly identified false positive after investigating.")
            else:
                return Reward(score=0.45, is_done=True, message="Guessed false positive correctly, but did not investigate the CVE first.")
        else:
            return Reward(score=0.05, is_done=True, message="Ignored the wrong vulnerability.")
            
    elif action.action_type == ActionType.update_dependency:
        return Reward(score=0.05, is_done=True, message="Unnecessary dependency update. Breakage potential for false positive.")
    
    elif action.action_type == ActionType.resolve:
        return Reward(score=0.05, is_done=True, message="Resolved without taking appropriate action.")
        
    return Reward(score=0.01, is_done=False, message="Action does not progress the hard task.")

def grade_task(task_id: str, action: Action, history: List[Action]) -> Reward:
    if task_id == "easy":
        return grade_easy(action)
    elif task_id == "medium":
        return grade_medium(action)
    elif task_id == "hard":
        return grade_hard(action, history)
    return Reward(score=0.01, is_done=True, message="Unknown task.")
