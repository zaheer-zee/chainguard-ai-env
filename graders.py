import math
from models import Action, ActionType, Reward
from typing import List


def sigmoid(x: float) -> float:
    """
    Sigmoid function: always returns a value strictly between 0 and 1.
    Mathematically impossible to return exactly 0.0 or 1.0 for any finite input.
    """
    return 1.0 / (1.0 + math.exp(-x))


def grade_easy(action: Action) -> Reward:
    if action.action_type == ActionType.update_dependency:
        if action.target == "lodash" and action.version == "4.17.21":
            # Perfect answer: sigmoid(2.2) ≈ 0.900
            return Reward(score=sigmoid(2.2), is_done=True, message="Successfully bumped lodash to secure version.")
        else:
            # Wrong version/package: sigmoid(-1.5) ≈ 0.182
            return Reward(score=sigmoid(-1.5), is_done=True, message="Incorrect package or version chosen.")
    elif action.action_type == ActionType.resolve:
        # Gave up: sigmoid(-2.5) ≈ 0.076
        return Reward(score=sigmoid(-2.5), is_done=True, message="Resolved without taking action.")
    # Invalid action: sigmoid(-3.0) ≈ 0.047
    return Reward(score=sigmoid(-3.0), is_done=False, message="Invalid action for this task.")


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
    # Invalid action: sigmoid(-3.0) ≈ 0.047
    return Reward(score=sigmoid(-3.0), is_done=False, message="Invalid action for this task.")


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
        # Gave up: sigmoid(-2.5) ≈ 0.076
        return Reward(score=sigmoid(-2.5), is_done=True, message="Resolved without taking appropriate action.")

    # Fallback: sigmoid(-3.0) ≈ 0.047
    return Reward(score=sigmoid(-3.0), is_done=False, message="Action does not progress the hard task.")


def grade_task(task_id: str, action: Action, history: List[Action]) -> Reward:
    if task_id == "easy":
        return grade_easy(action)
    elif task_id == "medium":
        return grade_medium(action)
    elif task_id == "hard":
        return grade_hard(action, history)
    # Unknown task: sigmoid(-3.0) ≈ 0.047
    return Reward(score=sigmoid(-3.0), is_done=True, message="Unknown task.")
