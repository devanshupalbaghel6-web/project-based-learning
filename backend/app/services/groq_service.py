"""
Groq LLM Service

Lightweight LLM service using Groq's API with Llama models.
Used for simple tasks like classification, extraction, summarization
to save Gemini API quota for complex generation tasks.
"""

from typing import Dict, List, Optional
from groq import Groq
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from app.core.config import settings


class GroqService:
    """Service for lightweight LLM tasks using Groq API"""
    
    def __init__(self):
        """Initialize Groq client and LangChain integration"""
        if not settings.GROQ_API_KEY:
            print("⚠️ GROQ_API_KEY not set, Groq service will be unavailable")
            self.client = None
            self.llm = None
            return
        
        try:
            # Direct Groq client
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            
            # LangChain wrapper
            self.llm = ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model_name=settings.GROQ_MODEL,
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS,
            )
            
            print(f"✅ Groq service initialized with model: {settings.GROQ_MODEL}")
            
        except Exception as e:
            print(f"❌ Error initializing Groq: {e}")
            self.client = None
            self.llm = None
    
    def classify_resource_type(self, url: str, title: str = "") -> str:
        """
        Classify resource type from URL and title.
        Returns: "tutorial", "documentation", "video", "article", "course", "other"
        """
        if not self.llm:
            # Fallback to simple heuristics
            if "youtube.com" in url or "youtu.be" in url:
                return "video"
            elif "github.com" in url:
                return "documentation"
            elif "udemy.com" in url or "coursera.org" in url:
                return "course"
            return "article"
        
        try:
            prompt = ChatPromptTemplate.from_template(
                "Classify this resource into ONE category: tutorial, documentation, video, article, course, or other.\n"
                "URL: {url}\n"
                "Title: {title}\n\n"
                "Respond with ONLY the category name, nothing else."
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(url=url, title=title or "N/A")
            
            return result.strip().lower()
            
        except Exception as e:
            print(f"Error classifying resource: {e}")
            return "other"
    
    def extract_skills(self, text: str, max_skills: int = 5) -> List[str]:
        """
        Extract key skills/technologies from text.
        Used for tagging resources and projects.
        """
        if not self.llm:
            return []
        
        try:
            prompt = ChatPromptTemplate.from_template(
                "Extract up to {max_skills} key technical skills or technologies from this text.\n"
                "Text: {text}\n\n"
                "Return ONLY a comma-separated list of skills, nothing else."
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(text=text, max_skills=max_skills)
            
            skills = [s.strip() for s in result.split(",")]
            return [s for s in skills if s][:max_skills]
            
        except Exception as e:
            print(f"Error extracting skills: {e}")
            return []
    
    def summarize_content(self, content: str, max_length: int = 200) -> str:
        """
        Generate concise summary of content.
        Used for resource descriptions and project overviews.
        """
        if not self.llm:
            # Simple truncation fallback
            return content[:max_length] + "..." if len(content) > max_length else content
        
        try:
            prompt = ChatPromptTemplate.from_template(
                "Summarize this content in {max_length} characters or less:\n\n"
                "{content}\n\n"
                "Summary:"
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(content=content, max_length=max_length)
            
            return result.strip()
            
        except Exception as e:
            print(f"Error summarizing: {e}")
            return content[:max_length] + "..." if len(content) > max_length else content
    
    def assess_difficulty(self, content: str, user_skills: List[str]) -> str:
        """
        Assess difficulty level based on content and user skills.
        Returns: "beginner", "intermediate", "advanced"
        """
        if not self.llm:
            return "intermediate"
        
        try:
            prompt = ChatPromptTemplate.from_template(
                "Assess the difficulty level of this content for a learner with these skills: {skills}\n\n"
                "Content: {content}\n\n"
                "Respond with ONLY one word: beginner, intermediate, or advanced"
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(
                content=content[:500],  # Limit to avoid token overflow
                skills=", ".join(user_skills) if user_skills else "none"
            )
            
            difficulty = result.strip().lower()
            if difficulty not in ["beginner", "intermediate", "advanced"]:
                return "intermediate"
            
            return difficulty
            
        except Exception as e:
            print(f"Error assessing difficulty: {e}")
            return "intermediate"
    
    def generate_search_query(self, user_intent: str, context: Dict) -> str:
        """
        Generate optimized search query from user intent.
        Used for web scraping and resource discovery.
        """
        if not self.llm:
            return user_intent
        
        try:
            prompt = ChatPromptTemplate.from_template(
                "Generate a concise search query (max 10 words) for finding resources.\n\n"
                "User wants: {intent}\n"
                "Their skills: {skills}\n"
                "Learning goal: {goal}\n\n"
                "Search query:"
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(
                intent=user_intent,
                skills=", ".join(context.get("skills", [])),
                goal=context.get("goal", "general learning")
            )
            
            return result.strip()
            
        except Exception as e:
            print(f"Error generating search query: {e}")
            return user_intent
    
    def parse_project_requirements(self, project_description: str) -> Dict:
        """
        Extract structured requirements from project description.
        Returns dict with skills, estimated_time, difficulty, prerequisites.
        """
        if not self.llm:
            return {
                "skills": [],
                "estimated_time": "unknown",
                "difficulty": "intermediate",
                "prerequisites": []
            }
        
        try:
            prompt = ChatPromptTemplate.from_template(
                "Extract project requirements from this description:\n\n"
                "{description}\n\n"
                "Respond in this exact format (one per line):\n"
                "SKILLS: skill1, skill2, skill3\n"
                "TIME: X hours/days/weeks\n"
                "DIFFICULTY: beginner/intermediate/advanced\n"
                "PREREQUISITES: prereq1, prereq2"
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(description=project_description)
            
            # Parse the structured response
            requirements = {
                "skills": [],
                "estimated_time": "unknown",
                "difficulty": "intermediate",
                "prerequisites": []
            }
            
            for line in result.strip().split("\n"):
                if line.startswith("SKILLS:"):
                    requirements["skills"] = [s.strip() for s in line.replace("SKILLS:", "").split(",")]
                elif line.startswith("TIME:"):
                    requirements["estimated_time"] = line.replace("TIME:", "").strip()
                elif line.startswith("DIFFICULTY:"):
                    requirements["difficulty"] = line.replace("DIFFICULTY:", "").strip().lower()
                elif line.startswith("PREREQUISITES:"):
                    requirements["prerequisites"] = [s.strip() for s in line.replace("PREREQUISITES:", "").split(",")]
            
            return requirements
            
        except Exception as e:
            print(f"Error parsing requirements: {e}")
            return {
                "skills": [],
                "estimated_time": "unknown",
                "difficulty": "intermediate",
                "prerequisites": []
            }


# Singleton instance
groq_service = GroqService()
