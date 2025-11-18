from pydantic import BaseModel
from typing import List, Optional


class FreelancerProfile(BaseModel):
    name: str
    skills: List[str]
    experience: str
    past_projects: List[str]
    rate: Optional[str] = None


class JobPosting(BaseModel):
    job_text: str


class ProposalResponse(BaseModel):
    proposal: str
    confidence_score: float
    matched_skills: List[str]


class ProposalHistory(BaseModel):
    proposals: List[dict]