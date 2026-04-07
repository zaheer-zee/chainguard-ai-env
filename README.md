---
title: ChainGuard AI - Env
emoji: 🛡️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
tags:
  - openenv
---

# ChainGuard AI - Blockchain-Secured Software Supply Chain Environment

ChainGuard AI is an advanced **Software Supply Chain Security** environment designed for evaluating intelligent AI agents within the OpenEnv specification. By combining Agentic AI with **Blockchain technology**, it creates a secure, verifiable, and immutable system for remediating software vulnerabilities.

## ⛓️ Blockchain Integration

The "Chain" in ChainGuard AI represents our commitment to cryptographic trust and transparency in software supply chains. While the environment evaluates AI agents, the underlying conceptual architecture leverages blockchain for:

- **Immutable Audit Trails**: Every remediation action taken by the AI agent (such as updating dependencies or changing base images) is treated as an on-chain transaction. This provides a transparent, tamper-proof history of security resolutions.
- **Verifiable Scan Reports**: Security scan reports and CVE detections are hashed and anchored to the blockchain, ensuring that vulnerability records cannot be altered or hidden.
- **Manifest Integrity**: The integrity of target manifests (e.g., `package.json`, `Dockerfile`) is cryptographically verified against the ledger before the agent interacts with them, preventing supply chain poisoning.

## 🚀 App Functionality

This application serves as a robust OpenEnv-compliant simulation where AI agents act as automated Security Engineers. Its primary functionalities include:

1. **Automated Vulnerability Remediation**: The environment presents agents with real-world scenarios over different difficulty levels (e.g., outdated NPM packages in `easy`, vulnerable Docker base images in `medium`, or false-positive CVEs in `hard` tasks).
2. **RESTful OpenEnv-compatible API**: Powered by FastAPI (`app.py`), the environment exposes `/reset` and `/step` HTTP interfaces that allow seamless integration with AI agents.
3. **Pydantic-driven Strict Typing**: `models.py` defines precise `Action` and `Observation` spaces:
    - *Observations* encapsulate the task details, scan reports, file manifests, and environment feedback.
    - *Actions* restrict the agent to meaningful security operations (`query_cve`, `update_dependency`, `change_base_image`, `ignore_vulnerability`, `resolve`).
4. **Agent Inference Engine**: The `inference.py` script provides a baseline implementation connecting any OpenAI-compatible LLM to the environment to autonomously solve security tasks.

## 🛠️ Setup Instructions

To run this environment locally or validate the agent interactions:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Validate with OpenEnv CLI:**
   ```bash
   openenv validate
   ```

## 🧠 Action and Observation Space

Agents interact with the environment using strongly typed JSON models:

- **Observation:** Provides the `task_id`, `scan_report`, `manifest_content` (the target file), previous `query_result` (if any), and `feedback` from the grader.
- **Action:** Agents must provide an `action_type` (Enum choosing between `query_cve`, `update_dependency`, `change_base_image`, `ignore_vulnerability`, `resolve`), `target` (package/image name), `version`, and `justification` for the action.

## 🤖 Baseline Inference

To evaluate a model against the environment tasks, execute the inference script using the standard `OpenAI` client interface:

```bash
export OPENAI_API_KEY="your-api-key"
export MODEL_NAME="gpt-4o" # or any compatible model
python inference.py
```
This script complies strictly with standard `[START]`, `[STEP]`, and `[END]` stdout logging formats for tracking the agent's progress and rewards.

## 🐳 Container & Deployment

The application is built for seamless cloud deployment, particularly to Hugging Face Spaces. The repository includes a `Dockerfile` that packages the FastAPI server running on port `8000`, satisfying the OpenEnv deployment requirements.

```bash
docker build -t chainguard .
docker run -p 8000:8000 chainguard
```

Once running, the environment natively handles the stateful `/reset` and `/step` HTTP requests required for remote AI agent evaluation.
