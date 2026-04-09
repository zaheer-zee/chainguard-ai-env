from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum

class ActionType(str, Enum):
    query_cve = "query_cve"
    update_dependency = "update_dependency"
    change_base_image = "change_base_image"
    ignore_vulnerability = "ignore_vulnerability"
    resolve = "resolve"

class Action(BaseModel):
    """The action taken by the ChainGuard Agent."""
    action_type: ActionType = Field(ActionType.resolve, description="The type of action to take.")
    target: Optional[str] = Field(None, description="The target package, image, or CVE ID.")
    version: Optional[str] = Field(None, description="The target version to bump or change to.")
    justification: str = Field("", description="Reasoning for this action.")

class Observation(BaseModel):
    """The observation the agent receives from the environment."""
    task_id: str = Field(description="The current task identifier.")
    scan_report: str = Field(description="The security scan report detailing CVEs.")
    manifest_content: str = Field(description="The file contents of the package.json or Dockerfile.")
    query_result: Optional[str] = Field(None, description="Internal observation result from a previous query_cve action.")
    feedback: Optional[str] = Field(None, description="Feedback from the environment on the previous action.")

class Reward(BaseModel):
    """Reward for the action."""
    score: float = Field(0.01, gt=0.0, lt=1.0, description="The objective score strictly between 0 and 1.")
    is_done: bool = Field(False, description="Whether the episode is finished.")
    message: str = Field("", description="Reasoning for the reward.")
