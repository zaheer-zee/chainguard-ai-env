from env import ChainGuardEnv
from models import Action

env = ChainGuardEnv()

print("==== CHAIN GUARD AI: EASY TASK DEMO ====")
obs = env.reset("easy")
print("\n🔍 1. OBSERVATION RECEIVED BY AGENT:\n")
print(f"Task ID: {obs.task_id}")
print(f"Report: {obs.scan_report}")
print(f"File Content: {obs.manifest_content}")

# Simulate perfectly correct Agent Action
print("\n🤖 2. THE AI AGENT DECIDES ON AN ACTION:\n")
action = Action(
    action_type="update_dependency",
    target="lodash",
    version="4.17.21",
    justification="Fixing CVE-2021-23337 by updating lodash to 4.17.21."
)
print(f"Action Type: {action.action_type.value}")
print(f"Target: {action.target} | Version: {action.version}")
print(f"Justification: {action.justification}")

# Environment handles step
new_obs, reward, done, info = env.step(action)

print("\n🌍 3. ENVIRONMENT GRADE & REWARD:\n")
print(f"Reward Score: {reward} / 1.0")
print(f"Task Done?: {done}")
print(f"Grader Message: {info['message']}")
print("========================================")
