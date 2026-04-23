"""
Progress Tracking Service

Tracks user progress through roadmaps and triggers adaptive adjustments.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.models.progress import (
    Roadmap, Milestone, Checkpoint, ProgressEntry, UserProgress,
    ProgressAnalysis, MilestoneStatus, CheckpointStatus
)
from app.services.groq_service import groq_service
from app.services.llm_service import llm_service
from app.db.repositories import get_repos


class ProgressService:
    """Service for tracking and analyzing user progress"""
    
    def __init__(self):
        print("✅ ProgressService initialized")
    
    async def track_milestone_start(
        self,
        user_id: str,
        roadmap_id: str,
        milestone_id: str
    ) -> ProgressEntry:
        """Record when user starts a milestone"""
        repos = get_repos()
        payload = {
            "user_id": user_id,
            "roadmap_id": roadmap_id,
            "milestone_id": milestone_id,
            "action": "started_milestone",
            "metadata": {"timestamp": datetime.utcnow().isoformat()},
            "timestamp": datetime.utcnow(),
        }

        entry_id = await repos.progress.create_entry(payload)
        return ProgressEntry(
            id=entry_id,
            user_id=user_id,
            roadmap_id=roadmap_id,
            milestone_id=milestone_id,
            action="started_milestone",
            metadata=payload["metadata"],
            timestamp=payload["timestamp"],
        )
    
    async def track_checkpoint_submission(
        self,
        user_id: str,
        roadmap_id: str,
        checkpoint_id: str,
        submission_data: Dict
    ) -> ProgressEntry:
        """Record checkpoint submission"""
        repos = get_repos()
        payload = {
            "user_id": user_id,
            "roadmap_id": roadmap_id,
            "milestone_id": submission_data.get("milestone_id", ""),
            "checkpoint_id": checkpoint_id,
            "action": "submitted_checkpoint",
            "metadata": submission_data,
            "timestamp": datetime.utcnow(),
        }

        entry_id = await repos.progress.create_entry(payload)
        return ProgressEntry(
            id=entry_id,
            user_id=user_id,
            roadmap_id=roadmap_id,
            milestone_id=payload["milestone_id"],
            checkpoint_id=checkpoint_id,
            action="submitted_checkpoint",
            metadata=submission_data,
            timestamp=payload["timestamp"],
        )
    
    async def calculate_user_progress(
        self,
        user_id: str,
        roadmap_id: str
    ) -> UserProgress:
        """
        Calculate aggregated user progress.
        """
        repos = get_repos()

        roadmap = await repos.roadmaps.find_by_id(roadmap_id)
        if not roadmap or roadmap.get("user_id") != user_id:
            return UserProgress(user_id=user_id, roadmap_id=roadmap_id)

        milestones = await repos.roadmaps.find_milestones_by_roadmap(roadmap_id)
        milestones_total = len(milestones)
        milestones_completed = sum(1 for item in milestones if item.get("status") == "completed")

        checkpoints_total = 0
        checkpoints_completed = 0
        for milestone in milestones:
            checkpoint_items = await repos.roadmaps.find_checkpoints_by_milestone(milestone["_id"])
            checkpoints_total += len(checkpoint_items)
            checkpoints_completed += sum(1 for cp in checkpoint_items if cp.get("is_completed", False))

        current_milestone = None
        for milestone in milestones:
            if milestone.get("status") in {"in_progress", "not_started"}:
                current_milestone = milestone.get("title")
                break

        entries = await repos.progress.find_by_roadmap(roadmap_id, limit=500)
        user_entries = [entry for entry in entries if entry.get("user_id") == user_id]

        last_activity = user_entries[0].get("timestamp") if user_entries else None

        time_spent_hours = 0.0
        for entry in user_entries:
            metadata = entry.get("metadata", {}) or {}
            duration = metadata.get("duration_hours")
            if isinstance(duration, (int, float)):
                time_spent_hours += float(duration)
        if time_spent_hours == 0 and user_entries:
            time_spent_hours = round(len(user_entries) * 0.5, 2)

        completed_actions = {
            "checkpoint_completed",
            "milestone_completed",
            "submitted_checkpoint",
        }
        completed_count = sum(1 for entry in user_entries if entry.get("action") in completed_actions)

        strengths = []
        if completed_count >= 5:
            strengths.append("consistency")
        if checkpoints_completed > 0 and checkpoints_completed == checkpoints_total:
            strengths.append("execution")

        struggles = []
        for entry in user_entries:
            metadata = entry.get("metadata", {}) or {}
            struggle_items = metadata.get("struggles", [])
            if isinstance(struggle_items, list):
                struggles.extend([str(item) for item in struggle_items if item])

        if not struggles:
            revision_count = sum(1 for entry in user_entries if entry.get("action") in {"needs_revision", "checkpoint_needs_revision"})
            if revision_count > 0:
                struggles.append("checkpoint quality")

        skills_acquired = []
        for milestone in milestones:
            if milestone.get("status") == "completed":
                skills_acquired.extend(milestone.get("skills_to_learn", []))

        skills_acquired = list(dict.fromkeys([skill for skill in skills_acquired if skill]))
        struggles = list(dict.fromkeys(struggles))

        streak_days = await repos.progress.calculate_streak(user_id, roadmap_id)

        average_pace = "normal"
        if milestones_total > 0:
            completion_ratio = milestones_completed / milestones_total
            if completion_ratio > 0.75 and time_spent_hours < 8:
                average_pace = "fast"
            elif completion_ratio < 0.25 and time_spent_hours > 15:
                average_pace = "slow"

        return UserProgress(
            user_id=user_id,
            roadmap_id=roadmap_id,
            milestones_completed=milestones_completed,
            milestones_total=milestones_total,
            checkpoints_completed=checkpoints_completed,
            checkpoints_total=checkpoints_total,
            current_milestone=current_milestone,
            time_spent_hours=time_spent_hours,
            average_pace=average_pace,
            skills_acquired=skills_acquired,
            struggles=struggles,
            strengths=strengths,
            last_activity=last_activity,
            streak_days=streak_days,
        )
    
    async def analyze_progress(
        self,
        user_id: str,
        roadmap_id: str
    ) -> ProgressAnalysis:
        """
        Analyze user progress and generate recommendations.
        
        Uses Groq for quick analysis, Gemini for complex recommendations.
        """
        # Get user progress
        progress = await self.calculate_user_progress(user_id, roadmap_id)
        
        # Quick difficulty assessment with Groq
        difficulty_level = groq_service.assess_difficulty(
            content=f"User completed {progress.milestones_completed}/{progress.milestones_total} milestones. "
                   f"Struggling with: {', '.join(progress.struggles)}. "
                   f"Strong in: {', '.join(progress.strengths)}.",
            user_skills=progress.skills_acquired
        )
        
        # Determine pace
        pace = self._assess_pace(progress)
        
        # Generate recommendations with Gemini
        adjustments = await llm_service.suggest_roadmap_adjustments(
            roadmap_id=roadmap_id,
            progress=progress.dict(),
            analysis=f"Difficulty: {difficulty_level}, Pace: {pace}"
        )
        
        # Build analysis
        analysis = ProgressAnalysis(
            user_id=user_id,
            roadmap_id=roadmap_id,
            overall_performance=self._assess_performance(progress),
            pace_assessment=pace,
            recommendations=adjustments.get("additional_resources", []),
            struggling_areas=progress.struggles,
            suggested_adjustments=adjustments,
            next_steps=self._generate_next_steps(progress)
        )
        
        return analysis
    
    def _assess_pace(self, progress: UserProgress) -> str:
        """Assess if user is moving too fast/slow"""
        completion_rate = progress.milestones_completed / max(progress.milestones_total, 1)
        
        # Simple heuristic: check against expected pace
        # TODO: Make this more sophisticated based on time spent
        if progress.time_spent_hours < 5 and completion_rate > 0.5:
            return "too_fast"  # Might be skipping content
        elif progress.time_spent_hours > 30 and completion_rate < 0.3:
            return "too_slow"  # Might be stuck
        else:
            return "optimal"
    
    def _assess_performance(self, progress: UserProgress) -> str:
        """Assess overall performance"""
        checkpoint_rate = progress.checkpoints_completed / max(progress.checkpoints_total, 1)
        
        if checkpoint_rate > 0.8 and len(progress.struggles) == 0:
            return "excellent"
        elif checkpoint_rate > 0.5 and len(progress.struggles) <= 2:
            return "good"
        else:
            return "needs_support"
    
    def _generate_next_steps(self, progress: UserProgress) -> List[str]:
        """Generate concrete next steps"""
        steps = []
        
        if progress.current_milestone:
            steps.append(f"Continue working on: {progress.current_milestone}")
        
        if progress.struggles:
            steps.append(f"Review resources for: {', '.join(progress.struggles[:2])}")
        
        if progress.checkpoints_completed == progress.checkpoints_total:
            steps.append("Complete current milestone and move to next")
        else:
            steps.append(f"Complete remaining checkpoints ({progress.checkpoints_total - progress.checkpoints_completed})")
        
        return steps
    
    async def should_adapt_roadmap(
        self,
        user_id: str,
        roadmap_id: str
    ) -> bool:
        """
        Determine if roadmap should be adapted based on progress.
        
        Triggers:
        - User struggling with same skill for > 3 checkpoints
        - User moving too fast/slow
        - User skipping content
        - New interests detected
        """
        progress = await self.calculate_user_progress(user_id, roadmap_id)
        
        # Trigger adaptation if:
        # 1. Too many struggles
        if len(progress.struggles) >= 3:
            return True
        
        # 2. Pace issues
        pace = self._assess_pace(progress)
        if pace in ["too_fast", "too_slow"]:
            return True
        
        # 3. Low checkpoint completion rate
        checkpoint_rate = progress.checkpoints_completed / max(progress.checkpoints_total, 1)
        if checkpoint_rate < 0.4 and progress.milestones_completed > 1:
            return True
        
        return False
    
    async def adapt_roadmap(
        self,
        roadmap: Roadmap,
        analysis: ProgressAnalysis
    ) -> Roadmap:
        """
        Adapt roadmap based on progress analysis.
        
        Possible adaptations:
        - Add reinforcement milestones for struggling areas
        - Skip advanced topics if basics are not solid
        - Adjust duration estimates
        - Add/remove resources
        - Reorder milestones
        """
        adaptations = []
        
        # Add reinforcement for struggling areas
        if analysis.struggling_areas:
            for area in analysis.struggling_areas:
                adaptation = {
                    "type": "add_reinforcement",
                    "skill": area,
                    "action": f"Added practice milestone for {area}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                adaptations.append(adaptation)
                
                # TODO: Actually add milestone to roadmap
        
        # Adjust pace
        if analysis.pace_assessment == "too_slow":
            adaptation = {
                "type": "extend_duration",
                "action": "Extended milestone durations by 20%",
                "timestamp": datetime.utcnow().isoformat()
            }
            adaptations.append(adaptation)
            
            # TODO: Update milestone durations
        
        elif analysis.pace_assessment == "too_fast":
            adaptation = {
                "type": "add_depth",
                "action": "Added intermediate challenges",
                "timestamp": datetime.utcnow().isoformat()
            }
            adaptations.append(adaptation)
        
        # Record adaptations
        roadmap.adaptations.extend(adaptations)
        roadmap.updated_at = datetime.utcnow()
        
        return roadmap
    
    async def suggest_resources_for_struggle(
        self,
        skill: str,
        user_level: str
    ) -> List[Dict]:
        """
        Suggest additional resources when user struggles with a skill.
        
        Uses scraper and LLM to find targeted help.
        """
        from app.services.orchestrator import orchestrator
        
        # Use orchestrator to aggregate resources
        resources = await orchestrator.aggregate_resources(
            query=f"Learn {skill} tutorial for {user_level}",
            user_profile={"skills": [], "experience_level": user_level},
            sources=["youtube", "stackoverflow", "github"]
        )
        
        return resources[:5]  # Top 5 resources


# Singleton instance
progress_service = ProgressService()
