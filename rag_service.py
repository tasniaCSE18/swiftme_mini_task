import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models import FreelancerProfile
from typing import List, Dict
import os


class RAGService:
    def __init__(self):
       
        self.embeddings = OpenAIEmbeddings()
        self.persist_directory = "./chroma_db"
        self.vectorstore = None
        self.profile_data = None
        
    def setup_profile(self, profile: FreelancerProfile) -> Dict:
        """Store freelancer profile in vector database"""
        try:
           
            documents = []
            
        
            skills_text = f"Skills: {', '.join(profile.skills)}"
            documents.append(skills_text)
            
          
            documents.append(f"Experience: {profile.experience}")
            
            
            for project in profile.past_projects:
                documents.append(f"Past Project: {project}")
           
            documents.append(f"Freelancer: {profile.name}")
            if profile.rate:
                documents.append(f"Rate: {profile.rate}")
            
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            splits = text_splitter.create_documents(documents)
            
        
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            
            self.profile_data = profile.dict()
            
            return {
                "status": "success",
                "message": f"Profile for {profile.name} stored successfully",
                "documents_stored": len(documents)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def retrieve_relevant_experience(self, job_requirements: str, k: int = 3) -> List[str]:
     
        if not self.vectorstore:
          
            try:
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
            except:
                return []
        
     
        results = self.vectorstore.similarity_search(job_requirements, k=k)
        return [doc.page_content for doc in results]
    
    def get_profile_data(self) -> Dict:
        """Get stored profile data"""
        return self.profile_data if self.profile_data else {}