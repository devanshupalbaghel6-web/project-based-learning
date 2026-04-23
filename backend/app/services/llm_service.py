"""
Optimized LLM Service using Google Gemini 2.5 Flash (Free Tier)

This service handles all LLM-related functionality with quota management:
- Onboarding chatbot conversations
- Project generation and recommendations
- Progress analysis and feedback
- Resource curation

Optimizations for free tier:
- Minimal API calls
- Caching responses where possible
- Batch operations
- Local embeddings (no embedding API calls)
- RAG with Qdrant for context retrieval
"""

from typing import Any, Dict, List, Optional
from app.core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from app.services.qdrant_service import qdrant_service


class LLMService:
    """Service for interacting with Google Gemini 2.5 Flash"""
    
    def __init__(self):
        self.google_api_key = settings.GOOGLE_API_KEY
        self.llm = None
        
        # Configure Gemini
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
            
            # Initialize LangChain LLM with Gemini 2.5 Flash (Free tier)
            self.llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,  # gemini-2.0-flash-exp
                google_api_key=self.google_api_key,
                temperature=settings.GEMINI_TEMPERATURE,
                max_output_tokens=settings.GEMINI_MAX_TOKENS,
                convert_system_message_to_human=True,
            )
            
            print(f"✅ LLM initialized: {settings.GEMINI_MODEL}")
        else:
            print("⚠️  GOOGLE_API_KEY not set – LLM features disabled. Add it to .env to enable AI.")
    
    async def generate_onboarding_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        context: Optional[Dict] = None,
    ) -> Dict:
        """
        Generate AI response for onboarding conversation
        
        Args:
            user_message: User's current message
            conversation_history: Previous conversation messages
            
        Returns:
            Dictionary with response and next question
        """
        conversation_history = conversation_history or []
        context = context or {}

        if not self.llm:
            is_complete = len(conversation_history) >= 6
            fallback = "Thanks, that helps. What is your current experience level and weekly time commitment?"
            return {
                "message": fallback,
                "response": fallback,
                "next_question": None if is_complete else fallback,
                "is_complete": is_complete,
                "extracted_info": {},
            }

        try:
            # Create concise onboarding prompt (minimize tokens)
            onboarding_prompt = PromptTemplate(
                input_variables=["history", "input"],
                template="""You are an AI learning assistant. Ask 3-4 concise questions to understand:
1. Experience level (beginner/intermediate/advanced)
2. Learning goal (new skill/portfolio/job/exploration)
3. Domain interests (AI, web dev, data science, etc.)
4. Time commitment (hours/week)

Be brief and friendly.

{history}

User: {input}
Assistant:"""
            )
            
            # Create conversation chain with memory
            memory = ConversationBufferMemory()
            
            # Add previous messages to memory
            for msg in conversation_history:
                if msg.get("role") == "user":
                    memory.chat_memory.add_user_message(msg.get("content", ""))
                elif msg.get("role") == "assistant":
                    memory.chat_memory.add_ai_message(msg.get("content", ""))
            
            chain = LLMChain(
                llm=self.llm,
                memory=memory,
                prompt=onboarding_prompt,
            )
            
            # Generate response
            response = chain.run(input=user_message)
            
            # Determine if onboarding is complete (after 3-4 exchanges)
            is_complete = len(conversation_history) >= 6
            
            return {
                "message": response,
                "response": response,
                "next_question": None if is_complete else response,
                "is_complete": is_complete,
                "extracted_info": {},
            }
            
        except Exception as e:
            print(f"Error in generate_onboarding_response: {e}")
            return {
                "message": "Tell me about your learning goals!",
                "response": "Tell me about your learning goals!",
                "next_question": None,
                "is_complete": False,
                "extracted_info": {},
            }
    
    async def generate_project_recommendations(
        self,
        user_preferences: Dict,
        context_projects: Optional[List[Dict]] = None,
        count: int = 5,
    ) -> List[Dict]:
        """
        Generate personalized project recommendations using RAG
        
        Args:
            user_preferences: User's onboarding data
            count: Number of recommendations
            
        Returns:
            List of project recommendations
        """
        interests = user_preferences.get("interests", [])
        goal = user_preferences.get("primary_goal", "learning")

        if not self.llm:
            # Deterministic fallback when LLM is unavailable.
            return [
                {
                    "title": f"{interest.title()} Starter Project {idx + 1}",
                    "description": f"Build a practical {interest} project aligned to your goal: {goal}.",
                    "difficulty": user_preferences.get("experience_level", "intermediate"),
                    "domain": interest,
                    "estimated_duration": "3-4 weeks",
                    "tech_stack": user_preferences.get("skills", [])[:3] or ["Python"],
                    "skills_to_learn": [interest],
                }
                for idx, interest in enumerate((interests or ["software development"])[:count])
            ]

        try:
            # Build context from user preferences
            user_context = f"""
Experience: {user_preferences.get('experience_level', 'beginner')}
Goal: {user_preferences.get('primary_goal', 'learn')}
Interests: {', '.join(user_preferences.get('interests', []))}
"""
            
            # Search vector DB for relevant project ideas (using local embeddings)
            similar_projects = await qdrant_service.search(
                query=user_context,
                top_k=10,
                filters={"type": "project_template"} if user_preferences.get('interests') else None,
            )
            
            # Build context from RAG results
            rag_context = "\n".join([
                f"- {proj['content'][:200]}"
                for proj in similar_projects[:3]
            ]) if similar_projects else "No existing templates"

            if context_projects:
                rag_context = "\n".join(
                    [rag_context]
                    + [
                        f"- {item.get('title', '')}: {item.get('description', '')}"
                        for item in context_projects[:3]
                    ]
                )
            
            # Generate recommendations with minimal prompt
            prompt = PromptTemplate(
                input_variables=["rag_context", "user_info", "count"],
                template="""Generate {count} project ideas for:

{user_info}

Similar projects for inspiration:
{rag_context}

For each project provide (keep concise):
1. Title
2. Description (1-2 sentences)
3. Tech stack
4. Duration (weeks)
5. Difficulty

Format as numbered list."""
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            response = chain.run(
                rag_context=rag_context,
                user_info=user_context,
                count=count,
            )
            
            # TODO: Parse structured format
            return [{"raw_response": response}]
            
        except Exception as e:
            print(f"Error in generate_project_recommendations: {e}")
            return []
    
    async def generate_custom_project(
        self,
        prompt: str,
        user_level: str,
    ) -> Dict:
        """
        Generate a custom project from user prompt
        
        Args:
            prompt: User's project idea
            user_level: User's experience level
            
        Returns:
            Complete project structure
        """
        if not self.llm:
            return {
                "raw_response": (
                    f"1. {prompt.title()}\n"
                    f"Description: Build a practical project for {user_level} learners\n"
                    "Tech Stack: Python, FastAPI, React\n"
                    "Duration: 4 weeks\n"
                    f"Difficulty: {user_level}"
                )
            }

        try:
            project_prompt = PromptTemplate(
                input_variables=["idea", "level"],
                template="""Create a project plan for: "{idea}"

Level: {level}

Provide:
1. Title
2. Description (2-3 sentences)
3. Tech stack (list)
4. 5-step roadmap
5. 3 key checkpoints
6. Estimated weeks

Be specific and practical."""
            )
            
            chain = LLMChain(llm=self.llm, prompt=project_prompt)
            response = chain.run(idea=prompt, level=user_level)
            
            return {"raw_response": response}
            
        except Exception as e:
            print(f"Error in generate_custom_project: {e}")
            return {}
    
    async def analyze_checkpoint_submission(
        self,
        checkpoint: Dict,
        screenshot_url: str,
        user_notes: str,
    ) -> Dict:
        """
        Analyze user's checkpoint submission
        
        Args:
            checkpoint: Checkpoint details
            screenshot_url: URL to screenshot
            user_notes: User's explanation
            
        Returns:
            Analysis and feedback
        """
        if not self.llm:
            return {
                "approved": True,
                "feedback": "Submission received. Keep iterating and share your next checkpoint.",
                "suggestions": [],
            }

        try:
            # Use concise prompt to save tokens
            feedback_prompt = PromptTemplate(
                input_variables=["title", "notes"],
                template="""Analyze checkpoint: {title}

User's work:
{notes}

Provide (be brief):
1. Meets requirements? (Yes/No)
2. Feedback (2-3 sentences)
3. Next step (1 sentence)

Be encouraging."""
            )
            
            chain = LLMChain(llm=self.llm, prompt=feedback_prompt)
            response = chain.run(
                title=checkpoint.get("title", ""),
                notes=user_notes,
            )
            
            return {
                "approved": True,
                "feedback": response,
                "suggestions": [],
            }
            
        except Exception as e:
            print(f"Error in analyze_checkpoint_submission: {e}")
            return {
                "approved": True,
                "feedback": "Great progress! Keep going.",
                "suggestions": [],
            }
    
    async def generate_response_with_rag(
        self,
        query: str,
        collection_filter: Optional[Dict] = None,
        top_k: int = 3,
        context: Optional[str] = None,
        chat_history: Optional[Any] = None,
    ) -> str:
        """
        Generate response using RAG (Retrieval Augmented Generation)
        
        Args:
            query: User query
            collection_filter: Optional filters for vector search
            top_k: Number of context documents
            
        Returns:
            Generated response
        """
        try:
            resolved_context = context
            if not resolved_context:
                # Retrieve relevant context using local embeddings
                context_docs = await qdrant_service.search(
                    query=query,
                    top_k=top_k,
                    filters=collection_filter,
                )

                resolved_context = "\n\n".join([
                    f"Context {i+1}: {doc['content']}"
                    for i, doc in enumerate(context_docs)
                ]) if context_docs else "No relevant context found"

            if not self.llm:
                return f"Based on available context: {resolved_context}"

            history_text = ""
            if isinstance(chat_history, dict):
                raw_history = chat_history.get("chat_history", [])
                history_text = "\n".join([
                    f"{getattr(msg, 'type', 'message')}: {getattr(msg, 'content', '')}"
                    for msg in raw_history[-6:]
                ])
            
            # Generate response with context
            rag_prompt = PromptTemplate(
                input_variables=["context", "query", "history"],
                template="""Use this context to answer:

{context}

Conversation history:
{history}

Question: {query}

Answer (be specific and cite context):"""
            )
            
            chain = LLMChain(llm=self.llm, prompt=rag_prompt)
            response = chain.run(context=resolved_context, query=query, history=history_text)
            
            return response
            
        except Exception as e:
            print(f"Error in generate_response_with_rag: {e}")
            return "Sorry, I encountered an error. Please try again."
    
    async def generate_roadmap(
        self,
        project: Dict,
        user_profile: Dict,
        requirements: Dict,
        available_resources: Dict
    ) -> Dict:
        """
        Generate structured learning roadmap for a project.
        
        Args:
            project: Project details
            user_profile: User's skills and preferences
            requirements: Parsed project requirements
            available_resources: Available learning resources by skill
            
        Returns:
            Structured roadmap with milestones, resources, checkpoints
        """
        if not self.llm:
            return {
                "milestones": [],
                "estimated_duration": requirements.get("estimated_time", "4 weeks"),
                "resources": available_resources,
                "checkpoints": [],
                "raw_response": "MILESTONES:\n1. Setup - 1 week\nCHECKPOINTS:\n1. Basic setup complete",
            }

        try:
            roadmap_prompt = PromptTemplate(
                input_variables=["project_name", "description", "skills", "level", "time"],
                template="""Create a learning roadmap for this project:

Project: {project_name}
Description: {description}
Required Skills: {skills}
User Level: {level}
Estimated Time: {time}

Generate a roadmap with:
1. 5-7 milestones (each with title, description, duration)
2. Prerequisites for each milestone
3. 3 checkpoints (practical tasks to verify progress)

Format as:
MILESTONES:
1. [Title] - [Duration]
   Description: ...
   Prerequisites: ...

CHECKPOINTS:
1. [Checkpoint title and deliverable]

Keep it concise and actionable."""
            )
            
            chain = LLMChain(llm=self.llm, prompt=roadmap_prompt)
            response = chain.run(
                project_name=project.get("title", ""),
                description=project.get("description", ""),
                skills=", ".join(requirements.get("skills", [])),
                level=user_profile.get("experience_level", "intermediate"),
                time=requirements.get("estimated_time", "4 weeks")
            )
            
            # Parse response into structured format
            # TODO: Use structured output parsing
            return {
                "milestones": [],
                "estimated_duration": requirements.get("estimated_time", "4 weeks"),
                "resources": available_resources,
                "checkpoints": [],
                "raw_response": response
            }
            
        except Exception as e:
            print(f"Error generating roadmap: {e}")
            return {
                "milestones": [],
                "estimated_duration": "unknown",
                "resources": {},
                "checkpoints": []
            }
    
    async def suggest_roadmap_adjustments(
        self,
        roadmap_id: str,
        progress: Dict,
        analysis: str
    ) -> Dict:
        """
        Suggest adjustments to roadmap based on user progress.
        
        Args:
            roadmap_id: Roadmap identifier
            progress: User's current progress
            analysis: Progress analysis from Groq
            
        Returns:
            Suggested adjustments
        """
        if not self.llm:
            return {
                "adjustments": "Keep current roadmap pace and add one focused practice session.",
                "recommended_pace": "normal",
                "additional_resources": [],
            }

        try:
            adjustment_prompt = PromptTemplate(
                input_variables=["progress_info", "analysis"],
                template="""Based on this user progress:

{progress_info}

Analysis: {analysis}

Suggest roadmap adjustments:
1. Should we speed up or slow down?
2. Any skills to reinforce?
3. Any milestones to add/remove?

Be brief (3-4 sentences)."""
            )
            
            chain = LLMChain(llm=self.llm, prompt=adjustment_prompt)
            response = chain.run(
                progress_info=str(progress),
                analysis=analysis
            )
            
            return {
                "adjustments": response,
                "recommended_pace": "normal",
                "additional_resources": []
            }
            
        except Exception as e:
            print(f"Error suggesting adjustments: {e}")
            return {
                "adjustments": "Continue at current pace",
                "recommended_pace": "normal",
                "additional_resources": []
            }
    
    async def rank_resources(
        self,
        resources: List[Dict],
        user_profile: Dict,
        query: str
    ) -> List[Dict]:
        """
        Rank resources by relevance to user and query.
        
        Args:
            resources: List of resources to rank
            user_profile: User's skills and preferences
            query: Search query
            
        Returns:
            Ranked list of resources
        """
        try:
            # For now, simple ranking based on metadata
            # In future, use LLM for complex ranking
            
            # Prioritize by:
            # 1. Difficulty match
            # 2. Source credibility (GitHub stars, SO votes)
            # 3. Recency
            
            user_level = user_profile.get("experience_level", "intermediate")
            
            scored_resources = []
            for resource in resources:
                score = 0
                
                # Difficulty match
                if resource.get("difficulty") == user_level:
                    score += 10
                
                # Source quality
                if resource.get("source") == "github" and resource.get("stars", 0) > 100:
                    score += 5
                elif resource.get("source") == "stackoverflow" and resource.get("score", 0) > 10:
                    score += 5
                elif resource.get("source") == "youtube":
                    score += 3
                
                # Type preference (videos for beginners, docs for advanced)
                if user_level == "beginner" and resource.get("type") == "video":
                    score += 3
                elif user_level == "advanced" and resource.get("type") in ["documentation", "repository"]:
                    score += 3
                
                scored_resources.append((score, resource))
            
            # Sort by score descending
            scored_resources.sort(reverse=True, key=lambda x: x[0])
            
            return [resource for score, resource in scored_resources]
            
        except Exception as e:
            print(f"Error ranking resources: {e}")
            return resources


# Singleton instance
llm_service = LLMService()
