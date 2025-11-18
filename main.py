from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models import FreelancerProfile, JobPosting, ProposalResponse, ProposalHistory
from rag_service import RAGService
from proposal_service import ProposalService
import os


load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables")

app = FastAPI(
    title="Swiftme Mini - Smart Job Proposal Generator",
    description="AI-powered job proposal generator using RAG and LangChain",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = RAGService()
proposal_service = ProposalService(rag_service)


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Swiftme Mini API",
        "version": "1.0.0"
    }


@app.post("/api/profile/setup")
def setup_profile(profile: FreelancerProfile):

    try:
        result = rag_service.setup_profile(profile)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/proposal/generate", response_model=ProposalResponse)
def generate_proposal(job: JobPosting):

    try:
        # Check if profile is set up
        if not rag_service.get_profile_data():
            raise HTTPException(
                status_code=400,
                detail="Please setup your profile first using /api/profile/setup"
            )
        
        result = proposal_service.generate_proposal(job.job_text)
        return ProposalResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/proposal/history", response_model=ProposalHistory)
def get_proposal_history():

    try:
        history = proposal_service.get_history()
        return ProposalHistory(proposals=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)