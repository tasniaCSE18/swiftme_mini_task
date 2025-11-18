from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from rag_service import RAGService
from typing import Dict, List
import os
import re


class ProposalService:
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service
        
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        self.proposal_history = []
    
    def extract_job_requirements(self, job_text: str) -> Dict:
      
        extraction_prompt = PromptTemplate(
            input_variables=["job_text"],
            template="""
            Analyze this job posting and extract the following information:
            
            Job Posting:
            {job_text}
            
            Extract and return:
            1. Required skills (comma-separated)
            2. Project scope (brief description)
            3. Budget/timeline (if mentioned)
            4. Key priorities (what matters most)
            
            Format your response as:
            SKILLS: <skills>
            SCOPE: <scope>
            BUDGET: <budget>
            PRIORITIES: <priorities>
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=extraction_prompt)
        result = chain.run(job_text=job_text)
        
        # Parse the result
        requirements = {
            "skills": [],
            "scope": "",
            "budget": "",
            "priorities": ""
        }
        
        lines = result.split('\n')
        for line in lines:
            if line.startswith("SKILLS:"):
                skills_text = line.replace("SKILLS:", "").strip()
                requirements["skills"] = [s.strip() for s in skills_text.split(',')]
            elif line.startswith("SCOPE:"):
                requirements["scope"] = line.replace("SCOPE:", "").strip()
            elif line.startswith("BUDGET:"):
                requirements["budget"] = line.replace("BUDGET:", "").strip()
            elif line.startswith("PRIORITIES:"):
                requirements["priorities"] = line.replace("PRIORITIES:", "").strip()
        
        return requirements
    
    def calculate_match_score(self, job_skills: List[str], profile_skills: List[str]) -> float:
        
        if not job_skills or not profile_skills:
            return 0.5
        
        job_skills_lower = [s.lower().strip() for s in job_skills]
        profile_skills_lower = [s.lower().strip() for s in profile_skills]
        
        matches = sum(1 for skill in job_skills_lower if any(ps in skill or skill in ps for ps in profile_skills_lower))
        score = matches / len(job_skills_lower) if job_skills_lower else 0.5
        return min(score, 1.0)
    
    def generate_proposal(self, job_text: str) -> Dict:
       
        
        job_requirements = self.extract_job_requirements(job_text)
        
        relevant_experience = self.rag_service.retrieve_relevant_experience(
            job_text, k=3
        )
        
        profile_data = self.rag_service.get_profile_data()
        
        
        profile_skills = profile_data.get("skills", [])
        matched_skills = [
            skill for skill in profile_skills 
            if any(req_skill.lower() in skill.lower() or skill.lower() in req_skill.lower() 
                   for req_skill in job_requirements.get("skills", []))
        ]
        confidence_score = self.calculate_match_score(
            job_requirements.get("skills", []),
            profile_skills
        )
        
        proposal_prompt = PromptTemplate(
            input_variables=["freelancer_name", "job_posting", "relevant_experience", "matched_skills"],
            template="""
            You are writing a professional job proposal for a freelancer.
            
            Freelancer: {freelancer_name}
            Matched Skills: {matched_skills}
            
            Job Posting:
            {job_posting}
            
            Relevant Experience from Profile:
            {relevant_experience}
            
            Write a compelling, personalized proposal with these sections:
            1. Professional greeting
            2. Brief statement showing you understand the project
            3. Highlight relevant experience (use the provided experience)
            4. Explain your approach/solution
            5. Mention timeline and next steps
            
            Keep it concise (200-300 words), professional, and personalized.
            Do not make up experience not provided in the relevant experience section.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=proposal_prompt)
        
        proposal_text = chain.run(
            freelancer_name=profile_data.get("name", ""),
            job_posting=job_text,
            relevant_experience="\n".join(relevant_experience),
            matched_skills=", ".join(matched_skills) if matched_skills else "General skills applicable to this project"
        )
        
    
        proposal_record = {
            "job_text": job_text[:100] + "...",
            "proposal": proposal_text,
            "confidence_score": confidence_score,
            "matched_skills": matched_skills
        }
        self.proposal_history.append(proposal_record)
        
        
        if len(self.proposal_history) > 5:
            self.proposal_history = self.proposal_history[-5:]
        
        return {
            "proposal": proposal_text,
            "confidence_score": round(confidence_score, 2),
            "matched_skills": matched_skills
        }
    
    def get_history(self) -> List[Dict]:
       
        return self.proposal_history