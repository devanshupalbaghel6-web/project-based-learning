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
from app.utils.response_parser import response_parser
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

    def _serialize_memory_messages(self, messages: List[Any]) -> List[Dict[str, str]]:
        """Convert LangChain memory messages into lightweight dicts for model prompts."""
        serialized: List[Dict[str, str]] = []
        for msg in messages:
            role = "assistant"
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            elif isinstance(msg, SystemMessage):
                role = "system"

            serialized.append({
                "role": role,
                "content": getattr(msg, "content", ""),
            })
        return serialized
    
    # ============================================================================
    # ONBOARDING FLOW
    # ============================================================================
    
    async def process_onboarding_message(
        self,
        user_id: str,
        message: str,
        context: Dict,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
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
        conversation_history = conversation_history or []

        if conversation_history and not memory.chat_memory.messages:
            for msg in conversation_history[-8:]:
                role = msg.get("role")
                content = msg.get("content", "")
                if role == "user":
                    memory.chat_memory.add_user_message(content)
                elif role == "assistant":
                    memory.chat_memory.add_ai_message(content)

        chat_history = self._serialize_memory_messages(memory.chat_memory.messages)
        
        # Use Gemini for natural, conversational onboarding
        result = await self.llm_service.generate_onboarding_response(
            user_message=message,
            conversation_history=chat_history,
            context=context,
        )

        response_text = result.get("response") or result.get("message", "")
        
        # Save to memory
        memory.save_context(
            {"input": message},
            {"output": response_text}
        )

        extracted_info = result.get("extracted_info", {})
        if not extracted_info and result.get("is_complete", False):
            transcript = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history])
            transcript = f"{transcript}\nuser: {message}\nassistant: {response_text}".strip()
            extracted_info = response_parser.parse_onboarding_extraction(transcript)
        
        return {
            "response": response_text,
            "extracted_info": extracted_info,
            "next_question": result.get("next_question"),
            "is_complete": result.get("is_complete", False),
        }
    
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
        
        interests = user_profile.get("interests", [])
        experience_level = user_profile.get("experience_level", "beginner")

        # Step 1: Gather context from existing user-scoped vector data when available.
        context_projects: List[Dict] = []
        project_query = f"{experience_level} projects for {', '.join(interests)}".strip()
        if project_query:
            similar_projects = await self.qdrant_service.search(
                query=project_query,
                top_k=8,
                filters={"type": "project_template"},
            )

            context_projects = [
                {
                    "title": p.get("metadata", {}).get("title", ""),
                    "description": p.get("content", ""),
                    "skills": p.get("metadata", {}).get("skills", []),
                }
                for p in similar_projects
            ]
        
        # Step 3: Generate custom projects with Gemini (using RAG context)
        generated_projects = await self.llm_service.generate_project_recommendations(
            user_preferences=user_profile,
            context_projects=context_projects,
            count=count,
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
            similar_resources = await self.qdrant_service.search(
                query=f"Learn {skill} tutorial guide",
                top_k=5,
                filters={"type": "resource", "skill": skill, "user_id": user_id},
            )
            resources_by_skill[skill] = [
                {
                    "content": r.get("content", ""),
                    **r.get("metadata", {}),
                }
                for r in similar_resources
            ]
        
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
        reason: str = "",
        user_progress: Optional[Dict] = None,
    ) -> Dict:
        """
        Dynamically adjust roadmap based on user progress.
        
        Uses Gemini to analyze progress and suggest adjustments.
        """
        # Analyze progress patterns (Groq - classification)
        user_progress = user_progress or {}
        analysis_payload = {
            **user_progress,
            "reason": reason,
            "user_id": user_id,
            "roadmap_id": roadmap_id,
        }

        progress_analysis = self.groq_service.assess_difficulty(
            content=str(analysis_payload),
            user_skills=user_progress.get("completed_skills", []),
        )
        
        # Generate roadmap adjustments (Gemini - strategic planning)
        adjustments = await self.llm_service.suggest_roadmap_adjustments(
            roadmap_id=roadmap_id,
            progress=analysis_payload,
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
        await self._store_resources_in_vector_db(
            ranked_resources,
            user_id=user_profile.get("user_id"),
        )
        
        return ranked_resources
    
    async def _store_resources_in_vector_db(
        self,
        resources: List[Dict],
        user_id: Optional[str] = None,
    ):
        """Store resources in Qdrant for future retrieval"""
        documents = []
        
        for resource in resources:
            # Create searchable text from resource
            text = f"{resource.get('title', '')} {resource.get('description', '')}"
            
            documents.append({
                "content": text,
                "metadata": {
                    "type": "resource",
                    "url": resource.get("url", ""),
                    "title": resource.get("title", ""),
                    "source": resource.get("source", ""),
                    "skills": resource.get("skills", []),
                    "difficulty": resource.get("difficulty", "intermediate"),
                    "resource_type": resource.get("type", "other"),
                    "skill": (resource.get("skills") or [None])[0],
                    "user_id": user_id,
                }
            })
        
        if documents:
            await self.qdrant_service.add_documents(documents)
    
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
        filters: Dict[str, Any] = {"user_id": user_id}
        if context_type != "general":
            filters["type"] = context_type

        relevant_docs = await self.qdrant_service.search(
            query=question,
            top_k=5,
            filters=filters,
        )
        
        # Extract context
        context = "\n\n".join([
            doc.get("content", "")
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
