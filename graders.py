import math
from models import Action, ActionType, Reward
from typing import List


def sigmoid(x: float) -> float:
    """
    Robust sigmoid function that ensures the output is strictly within (0, 1).
    Handles potential overflow errors and avoids exactly 0.0 or 1.0.
    """
    try:
        if x >= 0:
            z = math.exp(-x)
            val = 1.0 / (1.0 + z)
        else:
            z = math.exp(x)
            val = z / (1.0 + z)
        # Final safety clamp to avoid exactly 0.0 or 1.0 due to precision
        return max(0.0001, min(0.9999, val))
    except OverflowError:
        return 0.9999 if x > 0 else 0.0001


def grade_easy(action: Action) -> Reward:
    if action.action_type == ActionType.update_dependency:
        if action.target == "lodash" and action.version == "4.17.21":
            # Perfect answer: sigmoid(2.2) ≈ 0.900
            return Reward(score=sigmoid(2.2), is_done=True, message="Successfully bumped lodash to secure version.")
        else:
            # Wrong version/package: sigmoid(-1.5) ≈ 0.182
            return Reward(score=sigmoid(-1.5), is_done=True, message="Incorrect package or version chosen.")
    elif action.action_type == ActionType.resolve:
        # Gave up: sigmoid(-2.0) ≈ 0.119
        return Reward(score=sigmoid(-2.0), is_done=True, message="Resolved without taking action.")
    # Invalid action: sigmoid(-2.8) ≈ 0.057
    return Reward(score=sigmoid(-2.8), is_done=False, message="Invalid action for this task.")


def grade_medium(action: Action) -> Reward:
    if action.action_type == ActionType.change_base_image:
        if action.target == "alpine" and action.version == "3.18":
            # Perfect answer: sigmoid(2.2) ≈ 0.900
            return Reward(score=sigmoid(2.2), is_done=True, message="Successfully changed base image to secure version.")
        else:
            # Wrong image/version: sigmoid(-1.5) ≈ 0.182
            return Reward(score=sigmoid(-1.5), is_done=True, message="Incorrect image or version chosen.")
    elif action.action_type == ActionType.resolve:
        # Gave up: sigmoid(-2.5) ≈ 0.076
        return Reward(score=sigmoid(-2.5), is_done=True, message="Resolved without taking action.")
    # Invalid action: sigmoid(-3.2) ≈ 0.039
    return Reward(score=sigmoid(-3.2), is_done=False, message="Invalid action for this task.")


def grade_hard(action: Action, history: List[Action]) -> Reward:
    query_count = sum(
        1 for a in history
        if a.action_type == ActionType.query_cve and a.target == "CVE-2022-12345"
    )
    has_queried = query_count > 0

    if action.action_type == ActionType.query_cve:
        if action.target == "CVE-2022-12345":
            if query_count == 0:
                # First CVE query: sigmoid(-0.8) ≈ 0.310
                return Reward(score=sigmoid(-0.8), is_done=False, message="CVE details queried. Function 'legacyAuth()' is affected. Check codebase.")
            # Already queried: sigmoid(-3.0) ≈ 0.047
            return Reward(score=sigmoid(-3.0), is_done=False, message="Already queried this CVE.")
        # Wrong CVE: sigmoid(-3.0) ≈ 0.047
        return Reward(score=sigmoid(-3.0), is_done=False, message="Invalid CVE target.")

    if action.action_type == ActionType.ignore_vulnerability:
        if action.target == "CVE-2022-12345":
            if has_queried:
                # Investigated then correctly ignored: sigmoid(2.0) ≈ 0.880
                return Reward(score=sigmoid(2.0), is_done=True, message="Correctly identified false positive after investigating.")
            else:
                # Lucky guess, no investigation: sigmoid(0.5) ≈ 0.622
                return Reward(score=sigmoid(0.5), is_done=True, message="Guessed false positive correctly, but did not investigate the CVE first.")
        else:
            # Wrong vulnerability: sigmoid(-2.5) ≈ 0.076
            return Reward(score=sigmoid(-2.5), is_done=True, message="Ignored the wrong vulnerability.")

    elif action.action_type == ActionType.update_dependency:
        # Unnecessary update: sigmoid(-2.5) ≈ 0.076
        return Reward(score=sigmoid(-2.5), is_done=True, message="Unnecessary dependency update.")

    elif action.action_type == ActionType.resolve:
        # Gave up: sigmoid(-3.0) ≈ 0.047
        return Reward(score=sigmoid(-3.0), is_done=True, message="Resolved without taking appropriate action.")

    # Fallback: sigmoid(-3.5) ≈ 0.029
    return Reward(score=sigmoid(-3.5), is_done=False, message="Action does not progress the hard task.")


def grade_task(task_id: str, action: Action, history: List[Action]) -> Reward:
    if task_id == "easy":
        return grade_easy(action)
    elif task_id == "medium":
        return grade_medium(action)
    elif task_id == "hard":
        return grade_hard(action, history)
    # Unknown task: sigmoid(-4.0) ≈ 0.018
    return Reward(score=sigmoid(-4.0), is_done=True, message="Unknown task.")
