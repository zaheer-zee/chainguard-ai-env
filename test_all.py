"""
Full simulation of what the OpenEnv autograder does:
1. Tests every possible action on every task
2. Verifies EVERY score returned is strictly between 0 and 1
3. Simulates a multi-step episode to check accumulated scoring
4. Tests the FastAPI endpoints directly
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from env import ChainGuardEnv
from models import Action, ActionType
from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)

ERRORS = []

def check_score(score, context=""):
    if not (0 < score < 1):
        msg = f"[FAIL] Score {score} is NOT strictly between 0 and 1! Context: {context}"
        print(msg)
        ERRORS.append(msg)
    else:
        print(f"  [OK] score={score} — {context}")

print("=" * 60)
print("TEST 1: Every grader action on every task via env.step()")
print("=" * 60)

env = ChainGuardEnv()

# All possible actions to throw at the grader
test_actions = [
    Action(action_type=ActionType.update_dependency, target="lodash", version="4.17.21", justification="correct fix"),
    Action(action_type=ActionType.update_dependency, target="lodash", version="4.0.0", justification="wrong version"),
    Action(action_type=ActionType.change_base_image, target="alpine", version="3.18", justification="correct fix"),
    Action(action_type=ActionType.change_base_image, target="ubuntu", version="22.04", justification="wrong image"),
    Action(action_type=ActionType.query_cve, target="CVE-2022-12345", justification="investigate"),
    Action(action_type=ActionType.ignore_vulnerability, target="CVE-2022-12345", justification="false positive"),
    Action(action_type=ActionType.ignore_vulnerability, target="CVE-9999-9999", justification="wrong cve"),
    Action(action_type=ActionType.resolve, target=None, version=None, justification="give up"),
]

for task_id in ["easy", "medium", "hard"]:
    print(f"\n--- Task: {task_id} ---")
    for action in test_actions:
        env.reset(task_id)
        obs, score, done, info = env.step(action)
        check_score(score, f"task={task_id}, action={action.action_type.value}")

print("\n" + "=" * 60)
print("TEST 2: Multi-step hard episode (simulate the hardest path)")
print("=" * 60)

env.reset("hard")
# Step 1: query CVE
obs, score, done, info = env.step(Action(action_type=ActionType.query_cve, target="CVE-2022-12345", justification="investigate"))
check_score(score, "hard step 1: query_cve")
# Step 2: ignore correctly after querying
if not done:
    obs, score, done, info = env.step(Action(action_type=ActionType.ignore_vulnerability, target="CVE-2022-12345", justification="false positive confirmed"))
    check_score(score, "hard step 2: ignore after query")

print("\n" + "=" * 60)
print("TEST 3: 10-step stress test (should not crash or exceed bounds)")
print("=" * 60)

env.reset("easy")
for i in range(12):  # Intentionally go over 10
    if env.is_done:
        print(f"  [OK] Episode terminated at step {i}")
        break
    try:
        obs, score, done, info = env.step(Action(action_type=ActionType.resolve, target=None, version=None, justification="spam"))
        check_score(score, f"stress step {i+1}")
    except RuntimeError as e:
        print(f"  [OK] Episode correctly raised: {e}")
        break

print("\n" + "=" * 60)
print("TEST 4: FastAPI endpoint tests")
print("=" * 60)

# /reset with task_id
r = client.post("/reset", json={"task_id": "easy"})
assert r.status_code == 200, f"[FAIL] /reset easy: {r.status_code} {r.text}"
print("  [OK] POST /reset {'task_id': 'easy'} → 200")

# /reset with empty body
r = client.post("/reset", json=None)
assert r.status_code == 200, f"[FAIL] /reset empty: {r.status_code} {r.text}"
print("  [OK] POST /reset (empty body) → 200")

# /step
r = client.post("/step", json={"action_type": "resolve", "justification": "test"})
assert r.status_code == 200, f"[FAIL] /step: {r.status_code} {r.text}"
score = r.json()["reward"]
check_score(score, "API /step resolve")

# /state
r = client.get("/state")
assert r.status_code == 200, f"[FAIL] /state: {r.status_code} {r.text}"
print("  [OK] GET /state → 200")

print("\n" + "=" * 60)
if ERRORS:
    print(f"FAILED — {len(ERRORS)} issue(s) found:")
    for e in ERRORS:
        print(f"  {e}")
    sys.exit(1)
else:
    print("ALL TESTS PASSED! Safe to submit.")
print("=" * 60)
