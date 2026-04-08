import os
import json
from openai import OpenAI
from env import ChainGuardEnv
from models import Action

# Ensure we use environment variables as requested by the judges
api_key = os.environ.get("OPENAI_API_KEY", "dummy")
base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
hf_token = os.environ.get("HF_TOKEN", "")

# If HF_TOKEN is provided and we aren't explicitly overriding the API key, apply it.
if hf_token and api_key == "dummy":
    api_key = hf_token

client = OpenAI(api_key=api_key, base_url=base_url)

def run_inference(task_id: str, env: ChainGuardEnv):
    print(f"[START] Task: {task_id}")
    obs = env.reset(task_id)
    
    done = False
    reward = 0.0
    
    while not done:
        # Construct the prompt based on the observation
        prompt = (
            f"You are ChainGuard AI. Your task is to remediate vulnerabilities.\n"
            f"Task ID: {obs.task_id}\n"
            f"Scan Report: {obs.scan_report}\n"
            f"Manifest Content: {obs.manifest_content}\n"
            f"Previous Query Result: {obs.query_result}\n"
            f"Previous Feedback: {obs.feedback}\n\n"
            f"Choose ONE action and output only a JSON representing the action.\n"
            f"Available actions: query_cve, update_dependency, change_base_image, ignore_vulnerability, resolve.\n"
            f"Format requirements: {{\"action_type\": \"<type>\", \"target\": \"<package_or_image_or_cve>\", \"version\": \"<new_version>\", \"justification\": \"<reason>\"}}"
        )

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a precise JSON-outputting agent."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            action_data = json.loads(response.choices[0].message.content)
            action = Action(**action_data)
        except Exception as e:
            # Fallback action if agent fails formatting or connection fails
            action = Action(action_type="resolve", justification=f"Fallback due to error: {e}")

        # Step environment
        obs, reward, done, info = env.step(action)
        
        # Log Step
        print(f"[STEP] Action: {action.model_dump_json()} | ObsFeedback: {obs.feedback} | Reward: {reward} | Done: {done}")
        
    print(f"[END] Task: {task_id} | Final Score: {reward}")
    return reward

if __name__ == "__main__":
    environment = ChainGuardEnv()
    tasks = ["easy", "medium", "hard"]
    
    print("Starting OpenEnv Inference Baseline...")
    for t in tasks:
        run_inference(t, environment)
