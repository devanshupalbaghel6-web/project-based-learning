"""
LangChain Orchestrator

Central orchestration service that manages:
1. LLM routing (Gemini for complex, Groq for simple)
2. RAG pipeline (embeddings -> Qdrant -> context retrieval)
3. Multi-agent workflows (project generation, roadmap creation, resource aggregation)
4. Context management and memory
"""

from typing import List, Dict, Optional, Any
from langchain.chains import ConversationChain, LLMChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.services.llm_service import llm_service
from app.services.groq_service import groq_service
from app.services.qdrant_service import qdrant_service
from app.utils.embeddings import get_embedding
from app.core.config import settings


class LearningOrchestrator:
    """
    Orchestrates all AI components for the learning platform.
    Decides which LLM to use, when to use RAG, and how to combine results.
    """
    
    def __init__(self):
        """Initialize orchestrator with all AI services"""
        self.llm_service = llm_service
        self.groq_service = groq_service
        self.qdrant_service = qdrant_service
        
        # User session memories (key: user_id)
        self.user_memories: Dict[str, ConversationBufferMemory] = {}
        
        print("✅ LearningOrchestrator initialized")
    
    def get_user_memory(self, user_id: str) -> ConversationBufferMemory:
        """Get or create conversation memory for user"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
        return self.user_memories[user_id]
    
    # ============================================================================
    # ONBOARDING FLOW
    # ============================================================================
    
    async def process_onboarding_message(
        self,
        user_id: str,
        message: str,
        context: Dict
    ) -> Dict[str, Any]:
        """
        Process onboarding conversation message.
        Uses Gemini for natural conversation and user profiling.
        
        Returns:
            {
                "response": str,
                "extracted_info": Dict,
                "next_question": str,
                "is_complete": bool
            }
        """
        memory = self.get_user_memory(user_id)
        
        # Use Gemini for natural, conversational onboarding
        result = await self.llm_service.generate_onboarding_response(
            user_message=message,
            context=context,
            chat_history=memory.load_memory_variables({})
        )
        
        # Save to memory
        memory.save_context(
            {"input": message},
            {"output": result["response"]}
        )
        
        return result
    
    # ============================================================================
    # PROJECT GENERATION
    # ============================================================================
    
    async def generate_personalized_projects(
        self,
        user_profile: Dict,
        count: int = 5
    ) -> List[Dict]:
        """
        Generate personalized project recommendations.
        
        Strategy:
        1. Use Groq to extract key user interests and skills
        2. Search Qdrant for similar existing projects (RAG)
        3. Use Gemini to generate custom projects based on profile + context
        4. Use web scraper to find real-world project examples
        5. Combine all sources with de-duplication
        
        Returns list of project dicts with title, description, skills, etc.
        """
        projects = []
        
        # Step 1: Analyze user profile (Groq - lightweight)
        skills = user_profile.get("skills", [])
        interests = user_profile.get("interests", [])
        experience_level = user_profile.get("experience_level", "beginner")
        
        # Step 2: RAG - Find similar projects in vector DB
        query = f"Projects for {experience_level} developer interested in {', '.join(interests)}"
        query_embedding = get_embedding(query)
        
        similar_projects = self.qdrant_service.search(
            query_embedding=query_embedding,
            limit=10,
            filter_dict={"type": "project"}
        )
        
        # Extract context from similar projects
        context_projects = [
            {
                "title": p["payload"].get("title", ""),
                "description": p["payload"].get("description", ""),
                "skills": p["payload"].get("skills", [])
            }
            for p in similar_projects
        ]
        
        # Step 3: Generate custom projects with Gemini (using RAG context)
        generated_projects = await self.llm_service.generate_project_recommendations(
            user_profile=user_profile,
            context_projects=context_projects,
            count=count
        )
        
        projects.extend(generated_projects)
        
        return projects[:count]
    
    # ============================================================================
    # ROADMAP GENERATION
    # ============================================================================
    
    async def generate_dynamic_roadmap(
        self,
        user_id: str,
        project: Dict,
        user_profile: Dict
    ) -> Dict:
        """
        Generate personalized learning roadmap for a project.
        
        Strategy:
        1. Use Groq to parse project requirements
        2. Search Qdrant for relevant learning resources (RAG)
        3. Use Gemini to create structured roadmap with milestones
        4. Include adaptive checkpoints that adjust based on progress
        
        Returns:
            {
                "milestones": List[Dict],
                "estimated_duration": str,
                "resources": List[Dict],
                "checkpoints": List[Dict]
            }
        """
        # Step 1: Parse project requirements (Groq - fast)
        requirements = self.groq_service.parse_project_requirements(
            project.get("description", "")
        )
        
        # Step 2: RAG - Find relevant learning resources
        required_skills = requirements.get("skills", [])
        resources_by_skill = {}
        
        for skill in required_skills:
            query_embedding = get_embedding(f"Learn {skill} tutorial guide")
            similar_resources = self.qdrant_service.search(
                query_embedding=query_embedding,
                limit=5,
                filter_dict={"type": "resource", "skill": skill}
            )
            resources_by_skill[skill] = [r["payload"] for r in similar_resources]
        
        # Step 3: Generate structured roadmap (Gemini - complex reasoning)
        roadmap = await self.llm_service.generate_roadmap(
            project=project,
            user_profile=user_profile,
            requirements=requirements,
            available_resources=resources_by_skill
        )
        
        return roadmap
    
    async def adapt_roadmap(
        self,
        user_id: str,
        roadmap_id: str,
        user_progress: Dict
    ) -> Dict:
        """
        Dynamically adjust roadmap based on user progress.
        
        Uses Gemini to analyze progress and suggest adjustments.
        """
        # Analyze progress patterns (Groq - classification)
        progress_analysis = self.groq_service.assess_difficulty(
            content=str(user_progress),
            user_skills=user_progress.get("completed_skills", [])
        )
        
        # Generate roadmap adjustments (Gemini - strategic planning)
        adjustments = await self.llm_service.suggest_roadmap_adjustments(
            roadmap_id=roadmap_id,
            progress=user_progress,
            analysis=progress_analysis
        )
        
        return adjustments
    
    # ============================================================================
    # RESOURCE AGGREGATION
    # ============================================================================
    
    async def aggregate_resources(
        self,
        query: str,
        user_profile: Dict,
        sources: List[str] = None
    ) -> List[Dict]:
        """
        Aggregate learning resources from multiple sources.
        
        Strategy:
        1. Use Groq to generate optimized search queries
        2. Scrape from GitHub, YouTube, Reddit, Google
        3. Use Groq to classify and tag resources
        4. Use Gemini to rank and filter based on relevance
        5. Store in Qdrant for future RAG
        
        Sources: ["github", "youtube", "reddit", "google", "stackoverflow"]
        """
        if sources is None:
            sources = ["github", "youtube", "reddit", "google"]
        
        # Step 1: Generate optimized search query (Groq)
        optimized_query = self.groq_service.generate_search_query(
            user_intent=query,
            context=user_profile
        )
        
        # Step 2: Scrape resources (parallel)
        # This will be implemented in scraper_service
        from app.services.scraper_service import scraper_service
        
        scraped_resources = await scraper_service.scrape_all_sources(
            query=optimized_query,
            sources=sources
        )
        
        # Step 3: Classify and enrich (Groq - fast classification)
        enriched_resources = []
        for resource in scraped_resources:
            resource_type = self.groq_service.classify_resource_type(
                url=resource.get("url", ""),
                title=resource.get("title", "")
            )
            
            skills = self.groq_service.extract_skills(
                text=resource.get("description", ""),
                max_skills=5
            )
            
            difficulty = self.groq_service.assess_difficulty(
                content=resource.get("description", ""),
                user_skills=user_profile.get("skills", [])
            )
            
            enriched_resources.append({
                **resource,
                "type": resource_type,
                "skills": skills,
                "difficulty": difficulty
            })
        
        # Step 4: Rank by relevance (Gemini - complex reasoning)
        ranked_resources = await self.llm_service.rank_resources(
            resources=enriched_resources,
            user_profile=user_profile,
            query=query
        )
        
        # Step 5: Store in Qdrant for future RAG
        await self._store_resources_in_vector_db(ranked_resources)
        
        return ranked_resources
    
    async def _store_resources_in_vector_db(self, resources: List[Dict]):
        """Store resources in Qdrant for future retrieval"""
        documents = []
        
        for resource in resources:
            # Create searchable text from resource
            text = f"{resource.get('title', '')} {resource.get('description', '')}"
            
            documents.append({
                "text": text,
                "metadata": {
                    "type": "resource",
                    "url": resource.get("url", ""),
                    "title": resource.get("title", ""),
                    "source": resource.get("source", ""),
                    "skills": resource.get("skills", []),
                    "difficulty": resource.get("difficulty", "intermediate"),
                    "resource_type": resource.get("type", "other")
                }
            })
        
        if documents:
            self.qdrant_service.add_documents(documents)
    
    # ============================================================================
    # CONTEXT-AWARE Q&A
    # ============================================================================
    
    async def answer_question(
        self,
        user_id: str,
        question: str,
        context_type: str = "general"
    ) -> str:
        """
        Answer user question with RAG.
        
        context_type: "project", "resource", "roadmap", "general"
        
        Strategy:
        1. Search Qdrant for relevant context
        2. Use Gemini with retrieved context to answer
        3. Maintain conversation memory
        """
        # Get conversation memory
        memory = self.get_user_memory(user_id)
        
        # Search for relevant context (RAG)
        query_embedding = get_embedding(question)
        relevant_docs = self.qdrant_service.search(
            query_embedding=query_embedding,
            limit=5,
            filter_dict={"type": context_type} if context_type != "general" else None
        )
        
        # Extract context
        context = "\n\n".join([
            doc["payload"].get("text", "") or doc["payload"].get("description", "")
            for doc in relevant_docs
        ])
        
        # Generate answer with Gemini (complex reasoning)
        response = await self.llm_service.generate_response_with_rag(
            query=question,
            context=context,
            chat_history=memory.load_memory_variables({})
        )
        
        # Save to memory
        memory.save_context(
            {"input": question},
            {"output": response}
        )
        
        return response
    
    # ============================================================================
    # SMART LLM ROUTING
    # ============================================================================
    
    def route_task(self, task_type: str, complexity: str = "medium") -> str:
        """
        Decide which LLM to use for a task.
        
        Returns: "gemini" or "groq"
        
        Strategy:
        - Groq (Llama): Fast, simple tasks (classification, extraction, summarization)
        - Gemini: Complex reasoning, generation, creative tasks
        """
        simple_tasks = [
            "classify", "extract", "summarize", "tag",
            "parse", "analyze_simple", "validate"
        ]
        
        if task_type in simple_tasks and complexity in ["low", "medium"]:
            return "groq"
        
        return "gemini"


# Singleton instance
orchestrator = LearningOrchestrator()
