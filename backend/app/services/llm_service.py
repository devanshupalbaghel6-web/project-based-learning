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
import logging
import time
from app.core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from app.services.qdrant_service import qdrant_service
from app.services.groq_service import groq_service
from app.utils.response_parser import response_parser

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Google Gemini 2.5 Flash"""
    
    def __init__(self):
        self.google_api_key = settings.GOOGLE_API_KEY
        self.llm = None
        self._gemini_blocked_until = 0.0
        
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
                max_retries=0,
            )
            
            print(f"✅ LLM initialized: {settings.GEMINI_MODEL}")
        else:
            print("⚠️  GOOGLE_API_KEY not set – LLM features disabled. Add it to .env to enable AI.")

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        # Lightweight approximation for observability without external tokenizers.
        return max(1, int(len(text or "") / 4))

    def _log_prompt_observability(self, feature: str, prompt: str, extra: Optional[Dict[str, Any]] = None):
        payload = {
            "feature": feature,
            "chars": len(prompt or ""),
            "estimated_tokens": self._estimate_tokens(prompt or ""),
        }
        if extra:
            payload.update(extra)
        logger.info("llm_prompt_metrics %s", payload)

    @staticmethod
    def _is_quota_error(exc: Exception) -> bool:
        text = str(exc).lower()
        return "quota" in text or "resourceexhausted" in text or "429" in text

    def _block_gemini_temporarily(self, seconds: int = 1800) -> None:
        self._gemini_blocked_until = time.time() + seconds

    def _can_use_gemini(self) -> bool:
        return bool(self.llm) and time.time() >= self._gemini_blocked_until

    def _fallback_projects(self, user_preferences: Dict, count: int = 5) -> List[Dict]:
        interests = user_preferences.get("interests", []) or ["software development"]
        level = user_preferences.get("experience_level", "beginner")
        goal = user_preferences.get("primary_goal", "learn")
        skills = user_preferences.get("skills", []) or user_preferences.get("current_skills", [])
        results: List[Dict] = []
        for idx in range(count):
            interest = interests[idx % len(interests)]
            results.append(
                {
                    "title": f"{interest.title()} Portfolio Sprint {idx + 1}",
                    "description": (
                        f"Build a practical {interest} project tailored for a {level} learner "
                        f"focused on {goal} outcomes."
                    ),
                    "difficulty": level,
                    "domain": interest,
                    "estimated_duration": "3-5 weeks",
                    "tech_stack": skills[:3] or ["Python", "FastAPI", "React"],
                    "skills_to_learn": [interest],
                    "source": "profile_fallback",
                }
            )
        return results

    def _groq_text(self, prompt: str, max_tokens: int = 512) -> Optional[str]:
        return groq_service.generate_text(prompt=prompt, max_tokens=max_tokens)
    
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

        if not settings.GEMINI_ENABLE_ONBOARDING_CHAT or not self._can_use_gemini():
            is_complete = len(conversation_history) >= 6
            compact_history = "\n".join(
                f"{msg.get('role', 'user')}: {msg.get('content', '')[:160]}"
                for msg in conversation_history[-6:]
            )
            groq_prompt = (
                "You are an onboarding assistant.\n"
                "Collect these fields over chat: experience_level, primary_goal, interests, "
                "time_commitment, current_skills.\n"
                "Keep response under 60 words and ask one clear follow-up.\n"
                f"History:\n{compact_history}\n"
                f"User: {user_message}\nAssistant:"
            )
            fallback = self._groq_text(groq_prompt, max_tokens=180) or (
                "Thanks, that helps. What is your current experience level and weekly time commitment?"
            )
            return {
                "message": fallback,
                "response": fallback,
                "next_question": None if is_complete else fallback,
                "is_complete": is_complete,
                "extracted_info": {},
            }

        try:
            # Keep prompt/context short to reduce token usage and latency.
            recent_messages = conversation_history[-6:]
            compact_history = "\n".join(
                f"{msg.get('role', 'user')}: {msg.get('content', '')[:200]}"
                for msg in recent_messages
            )
            onboarding_prompt = PromptTemplate(
                input_variables=["history", "input"],
                template="""You are an onboarding assistant. Keep responses under 80 words.
Goal: collect exactly these fields across conversation:
- experience_level (beginner/intermediate/advanced)
- primary_goal
- interests (list)
- time_commitment (hours/week)
- current_skills (list)

Rules:
- Ask at most one focused follow-up question.
- If enough information is already collected, confirm completion in a short sentence.
- Do not repeat long context.

Conversation:
{history}
user: {input}
assistant:""",
            )
            self._log_prompt_observability(
                "onboarding_chat",
                onboarding_prompt.template,
                {
                    "history_turns": len(recent_messages),
                    "user_message_chars": len(user_message or ""),
                },
            )

            chain = LLMChain(llm=self.llm, prompt=onboarding_prompt)
            chain_result = chain.invoke({"history": compact_history, "input": user_message})
            response = chain_result.get("text", "").strip()

            # Estimate completeness using parsed extraction from compact transcript.
            transcript = f"{compact_history}\nuser: {user_message}\nassistant: {response}".strip()
            extracted_info = response_parser.parse_onboarding_extraction(transcript)
            has_core = bool(extracted_info.get("interests")) and extracted_info.get("time_commitment") not in (
                None,
                "",
                "unknown",
            )
            user_turns = sum(1 for msg in conversation_history if msg.get("role") == "user") + 1
            is_complete = has_core and user_turns >= 3

            return {
                "message": response,
                "response": response,
                "next_question": None if is_complete else response,
                "is_complete": is_complete,
                "extracted_info": extracted_info if is_complete else {},
            }
            
        except Exception as e:
            if self._is_quota_error(e):
                self._block_gemini_temporarily()
                fallback = self._groq_text(
                    (
                        "Act as onboarding assistant. Ask one concise follow-up question to collect: "
                        "experience_level, primary_goal, interests, time_commitment, current_skills.\n"
                        f"User message: {user_message}\nAssistant:"
                    ),
                    max_tokens=160,
                ) or "Tell me about your learning goals!"
                return {
                    "message": fallback,
                    "response": fallback,
                    "next_question": fallback,
                    "is_complete": False,
                    "extracted_info": {},
                }
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

        if not settings.GEMINI_ENABLE_PROJECT_GENERATION:
            groq_prompt = (
                f"Generate {count} practical project ideas for this learner profile.\n"
                f"{user_preferences}\n"
                "Return numbered list with Title, Description, Tech Stack, Duration, Difficulty."
            )
            groq_projects = self._groq_text(groq_prompt, max_tokens=900)
            if groq_projects:
                return [{"raw_response": groq_projects, "source": "groq_fallback"}]
            return self._fallback_projects(user_preferences=user_preferences, count=count)

        if not self._can_use_gemini():
            groq_prompt = (
                f"Generate {count} practical project ideas for this learner profile.\n"
                f"{user_preferences}\n"
                "Return numbered list with Title, Description, Tech Stack, Duration, Difficulty."
            )
            groq_projects = self._groq_text(groq_prompt, max_tokens=900)
            if groq_projects:
                return [{"raw_response": groq_projects, "source": "groq_fallback"}]
            # Deterministic fallback when LLM is unavailable.
            return self._fallback_projects(user_preferences=user_preferences, count=count)

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
            self._log_prompt_observability(
                "project_recommendations",
                prompt.template,
                {
                    "context_projects": len(context_projects or []),
                    "requested_count": count,
                },
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            chain_result = chain.invoke(
                {
                    "rag_context": rag_context,
                    "user_info": user_context,
                    "count": count,
                }
            )
            response = chain_result.get("text", "")
            
            # TODO: Parse structured format
            return [{"raw_response": response}]
            
        except Exception as e:
            if self._is_quota_error(e):
                self._block_gemini_temporarily()
                groq_projects = self._groq_text(
                    (
                        f"Generate {count} practical personalized project ideas.\n"
                        f"Profile: {user_preferences}\n"
                        "Format as numbered list with title and short description."
                    ),
                    max_tokens=900,
                )
                if groq_projects:
                    return [{"raw_response": groq_projects, "source": "groq_fallback"}]
            print(f"Error in generate_project_recommendations: {e}")
            return self._fallback_projects(user_preferences=user_preferences, count=count)
    
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
        if not settings.GEMINI_ENABLE_PROJECT_GENERATION or not self._can_use_gemini():
            groq_response = self._groq_text(
                (
                    f"Create one project plan for idea: {prompt}\n"
                    f"Learner level: {user_level}\n"
                    "Include title, description, tech stack, roadmap steps, and checkpoints."
                ),
                max_tokens=700,
            )
            if groq_response:
                return {"raw_response": groq_response}
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
            self._log_prompt_observability(
                "custom_project",
                project_prompt.template,
                {"idea_chars": len(prompt or "")},
            )
            
            chain = LLMChain(llm=self.llm, prompt=project_prompt)
            chain_result = chain.invoke({"idea": prompt, "level": user_level})
            response = chain_result.get("text", "")
            
            return {"raw_response": response}
            
        except Exception as e:
            if self._is_quota_error(e):
                self._block_gemini_temporarily()
                groq_response = self._groq_text(
                    (
                        f"Create one project plan for idea: {prompt}\n"
                        f"Learner level: {user_level}\n"
                        "Include title, description, tech stack, roadmap, checkpoints."
                    ),
                    max_tokens=700,
                )
                if groq_response:
                    return {"raw_response": groq_response}
            print(f"Error in generate_custom_project: {e}")
            return {
                "raw_response": (
                    f"1. {prompt.title()}\n"
                    f"Description: Build a practical project for {user_level} learners\n"
                    "Tech Stack: Python, FastAPI, React\n"
                    "Duration: 4 weeks\n"
                    f"Difficulty: {user_level}"
                )
            }
    
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
            self._log_prompt_observability(
                "checkpoint_feedback",
                feedback_prompt.template,
                {"notes_chars": len(user_notes or "")},
            )
            
            chain = LLMChain(llm=self.llm, prompt=feedback_prompt)
            chain_result = chain.invoke(
                {"title": checkpoint.get("title", ""), "notes": user_notes}
            )
            response = chain_result.get("text", "")
            
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
            self._log_prompt_observability(
                "rag_answer",
                rag_prompt.template,
                {
                    "context_chars": len(resolved_context or ""),
                    "history_chars": len(history_text or ""),
                },
            )
            
            chain = LLMChain(llm=self.llm, prompt=rag_prompt)
            chain_result = chain.invoke(
                {"context": resolved_context, "query": query, "history": history_text}
            )
            response = chain_result.get("text", "")
            
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
            self._log_prompt_observability(
                "roadmap_generation",
                roadmap_prompt.template,
                {
                    "skills_count": len(requirements.get("skills", [])),
                    "resources_skills_count": len(available_resources or {}),
                },
            )
            
            chain = LLMChain(llm=self.llm, prompt=roadmap_prompt)
            chain_result = chain.invoke(
                {
                    "project_name": project.get("title", ""),
                    "description": project.get("description", ""),
                    "skills": ", ".join(requirements.get("skills", [])),
                    "level": user_profile.get("experience_level", "intermediate"),
                    "time": requirements.get("estimated_time", "4 weeks"),
                }
            )
            response = chain_result.get("text", "")
            
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
            self._log_prompt_observability(
                "roadmap_adjustment",
                adjustment_prompt.template,
                {"progress_payload_chars": len(str(progress) or "")},
            )
            
            chain = LLMChain(llm=self.llm, prompt=adjustment_prompt)
            chain_result = chain.invoke(
                {"progress_info": str(progress), "analysis": analysis}
            )
            response = chain_result.get("text", "")
            
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
