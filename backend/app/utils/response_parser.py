"""
LLM Response Parsers

Utilities to parse LLM text responses into structured data models.
"""

import re
from typing import List, Dict, Optional
import json


class ResponseParser:
    """Parser for LLM text responses"""

    @staticmethod
    def _clean_llm_text(value: str) -> str:
        """Normalize common markdown/label artifacts from model output."""
        cleaned = (value or "").strip()
        cleaned = cleaned.replace("**", "")
        cleaned = re.sub(r"^title\s*:\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^description\s*:\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned
    
    @staticmethod
    def parse_projects_list(llm_response: str) -> List[Dict]:
        """
        Parse LLM project recommendations into structured format.
        
        Expected format:
        1. Title
           Description: ...
           Tech Stack: ...
           Duration: ...
           Difficulty: ...
        """
        projects = []
        
        # Split by numbered list items
        pattern = r'(\d+)\.\s*(.+?)(?=\n\d+\.|$)'
        matches = re.findall(pattern, llm_response, re.DOTALL)
        
        for num, content in matches:
            project = {}
            
            # Extract title (first line)
            lines = content.strip().split('\n')
            project['title'] = ResponseParser._clean_llm_text(lines[0])
            
            # Extract other fields
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = ResponseParser._clean_llm_text(value)
                    
                    if key == 'description':
                        project['description'] = value
                    elif key in ['tech_stack', 'technologies', 'stack']:
                        # Parse comma-separated list
                        project['tech_stack'] = [
                            ResponseParser._clean_llm_text(t)
                            for t in re.split(r"[,\-|/]", value)
                            if ResponseParser._clean_llm_text(t)
                        ]
                    elif key in ['duration', 'estimated_time', 'time']:
                        project['estimated_duration'] = value
                    elif key == 'difficulty':
                        project['difficulty'] = value.lower()
            
            # Set defaults if missing
            project.setdefault('description', '')
            project.setdefault('tech_stack', [])
            project.setdefault('estimated_duration', 'unknown')
            project.setdefault('difficulty', 'intermediate')
            project.setdefault('status', 'not_started')
            
            projects.append(project)
        
        return projects
    
    @staticmethod
    def parse_roadmap(llm_response: str) -> Dict:
        """
        Parse LLM roadmap response into structured format.
        
        Expected format:
        MILESTONES:
        1. Title - Duration
           Description: ...
           Prerequisites: ...
        
        CHECKPOINTS:
        1. Checkpoint title
        """
        milestones = []
        checkpoints = []
        
        # Split response into sections
        if 'MILESTONES:' in llm_response:
            parts = llm_response.split('CHECKPOINTS:', 1)
            milestone_section = parts[0].replace('MILESTONES:', '').strip()
            checkpoint_section = parts[1].strip() if len(parts) > 1 else ''
            
            # Parse milestones
            milestone_pattern = r'(\d+)\.\s*(.+?)\s*-\s*(.+?)(?=\n\d+\.|$)'
            milestone_matches = re.findall(milestone_pattern, milestone_section, re.DOTALL)
            
            for order, content, duration in milestone_matches:
                milestone = {
                    'order': int(order),
                    'title': content.split('\n')[0].strip(),
                    'duration': duration.strip(),
                    'description': '',
                    'prerequisites': []
                }
                
                # Extract description and prerequisites
                lines = content.split('\n')
                for line in lines[1:]:
                    if 'Description:' in line:
                        milestone['description'] = line.split('Description:', 1)[1].strip()
                    elif 'Prerequisites:' in line:
                        prereqs = line.split('Prerequisites:', 1)[1].strip()
                        milestone['prerequisites'] = [p.strip() for p in prereqs.split(',')]
                
                milestones.append(milestone)
            
            # Parse checkpoints
            checkpoint_pattern = r'(\d+)\.\s*(.+?)(?=\n\d+\.|$)'
            checkpoint_matches = re.findall(checkpoint_pattern, checkpoint_section, re.DOTALL)
            
            for order, content in checkpoint_matches:
                checkpoints.append({
                    'order': int(order),
                    'title': content.strip(),
                    'deliverable': content.strip()
                })
        
        return {
            'milestones': milestones,
            'checkpoints': checkpoints
        }
    
    @staticmethod
    def parse_project_requirements(llm_response: str) -> Dict:
        """
        Parse project requirements from LLM response.
        
        Expected format:
        SKILLS: skill1, skill2, skill3
        TIME: X hours/days/weeks
        DIFFICULTY: beginner/intermediate/advanced
        PREREQUISITES: prereq1, prereq2
        """
        requirements = {
            'skills': [],
            'estimated_time': 'unknown',
            'difficulty': 'intermediate',
            'prerequisites': []
        }
        
        lines = llm_response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('SKILLS:'):
                skills_str = line.replace('SKILLS:', '').strip()
                requirements['skills'] = [s.strip() for s in skills_str.split(',') if s.strip()]
            
            elif line.startswith('TIME:'):
                requirements['estimated_time'] = line.replace('TIME:', '').strip()
            
            elif line.startswith('DIFFICULTY:'):
                difficulty = line.replace('DIFFICULTY:', '').strip().lower()
                if difficulty in ['beginner', 'intermediate', 'advanced']:
                    requirements['difficulty'] = difficulty
            
            elif line.startswith('PREREQUISITES:'):
                prereqs_str = line.replace('PREREQUISITES:', '').strip()
                requirements['prerequisites'] = [p.strip() for p in prereqs_str.split(',') if p.strip()]
        
        return requirements
    
    @staticmethod
    def extract_json_from_response(llm_response: str) -> Optional[Dict]:
        """
        Extract JSON from LLM response if present.
        
        Useful when LLM is asked to return structured data.
        """
        # Try to find JSON block
        json_pattern = r'```json\s*(\{.+?\})\s*```'
        match = re.search(json_pattern, llm_response, re.DOTALL)
        
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to parse the entire response as JSON
        try:
            return json.loads(llm_response)
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def parse_skills_list(text: str) -> List[str]:
        """
        Parse comma-separated list of skills from text.
        """
        # Remove common prefixes
        text = re.sub(r'^(Skills?:?|Technologies?:?|Stack:?)\s*', '', text, flags=re.IGNORECASE)
        
        # Split by commas and clean
        skills = [s.strip() for s in text.split(',')]
        
        # Remove empty strings and duplicates
        skills = list(dict.fromkeys([s for s in skills if s]))
        
        return skills
    
    @staticmethod
    def parse_onboarding_extraction(llm_response: str) -> Dict:
        """
        Parse extracted user information from onboarding conversation.
        
        Expected to extract:
        - experience_level
        - interests
        - primary_goal
        - time_commitment
        - current_skills
        """
        extracted = {
            'experience_level': 'beginner',
            'interests': [],
            'primary_goal': 'learn',
            'time_commitment': 'unknown',
            'current_skills': []
        }
        
        # Try JSON extraction first
        json_data = ResponseParser.extract_json_from_response(llm_response)
        if json_data:
            extracted.update(json_data)
            return ResponseParser.normalize_onboarding_extraction(extracted)
        
        # Fallback to text parsing
        lines = llm_response.lower().split('\n')
        
        for line in lines:
            if 'experience' in line or 'level' in line:
                if 'beginner' in line:
                    extracted['experience_level'] = 'beginner'
                elif 'intermediate' in line:
                    extracted['experience_level'] = 'intermediate'
                elif 'advanced' in line:
                    extracted['experience_level'] = 'advanced'
            
            elif 'goal' in line:
                if 'job' in line or 'career' in line:
                    extracted['primary_goal'] = 'career'
                elif 'portfolio' in line:
                    extracted['primary_goal'] = 'portfolio'
                elif 'learn' in line:
                    extracted['primary_goal'] = 'learn'
            
            elif 'interest' in line:
                # Try to extract interests
                if ':' in line:
                    interests_str = line.split(':', 1)[1]
                    extracted['interests'] = [i.strip() for i in interests_str.split(',')]
            
            elif 'time' in line or 'hours' in line:
                # Extract time commitment
                numbers = re.findall(r'\d+', line)
                if numbers:
                    hours = numbers[0]
                    if 'week' in line:
                        extracted['time_commitment'] = f"{hours} hours/week"
                    elif 'day' in line:
                        extracted['time_commitment'] = f"{hours} hours/day"
        
        return ResponseParser.normalize_onboarding_extraction(extracted)

    @staticmethod
    def normalize_onboarding_extraction(raw: Dict) -> Dict:
        """Enforce onboarding extraction contract and normalize values."""
        normalized = {
            "experience_level": "beginner",
            "interests": [],
            "primary_goal": "learn",
            "time_commitment": "unknown",
            "current_skills": [],
            "preferred_learning_style": "hands_on",
        }

        experience = str(raw.get("experience_level", "beginner")).lower().strip()
        if experience in {"beginner", "intermediate", "advanced"}:
            normalized["experience_level"] = experience

        goal = str(raw.get("primary_goal", "learn")).lower().strip()
        goal_map = {
            "learning": "learn",
            "learn": "learn",
            "portfolio": "portfolio",
            "career": "career",
            "job": "career",
            "exploration": "exploration",
            "explore": "exploration",
        }
        normalized["primary_goal"] = goal_map.get(goal, "learn")

        for key in ("interests", "current_skills"):
            values = raw.get(key, [])
            if isinstance(values, str):
                values = re.split(r"[,/|]", values)
            cleaned = []
            for item in values or []:
                token = ResponseParser._clean_llm_text(str(item)).lower()
                if token and token not in cleaned:
                    cleaned.append(token)
            normalized[key] = cleaned[:20]

        time_commitment = ResponseParser._clean_llm_text(str(raw.get("time_commitment", "unknown")))
        normalized["time_commitment"] = time_commitment.lower() if time_commitment else "unknown"

        style = ResponseParser._clean_llm_text(str(raw.get("preferred_learning_style", "hands_on"))).lower()
        normalized["preferred_learning_style"] = style or "hands_on"
        return normalized


# Singleton instance
response_parser = ResponseParser()
