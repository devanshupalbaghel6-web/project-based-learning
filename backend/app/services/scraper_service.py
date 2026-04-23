"""
Web Scraping Service

This service handles scraping resources from various platforms:
- GitHub repositories
- YouTube videos
- Reddit discussions
- Stack Overflow questions
- Google search results
- Documentation sites
"""

from typing import List, Dict, Optional
import httpx
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import json
from datetime import datetime
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class ScraperService:
    """Service for scraping web resources from multiple platforms"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        print("✅ ScraperService initialized")
    
    async def scrape_all_sources(
        self,
        query: str,
        sources: List[str],
        limit_per_source: int = 5
    ) -> List[Dict]:
        """
        Scrape from all specified sources in parallel.
        
        Args:
            query: Search query
            sources: List of sources ["github", "youtube", "reddit", "google", "stackoverflow"]
            limit_per_source: Max results per source
            
        Returns:
            Combined list of resources from all sources
        """
        tasks = []
        
        if "github" in sources:
            tasks.append(self.search_github(query, limit_per_source))
        if "youtube" in sources:
            tasks.append(self.search_youtube(query, limit_per_source))
        if "reddit" in sources:
            tasks.append(self.search_reddit(query, limit_per_source))
        if "google" in sources:
            tasks.append(self.search_google(query, limit_per_source))
        if "stackoverflow" in sources:
            tasks.append(self.search_stackoverflow(query, limit_per_source))
        
        # Execute all scraping tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and flatten results
        all_resources = []
        for result in results:
            if isinstance(result, list):
                all_resources.extend(result)
            elif isinstance(result, Exception):
                print(f"Scraping error: {result}")
        
        return all_resources
    
    async def search_github(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search GitHub for relevant repositories using GitHub API.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of repository details with metadata
        """
        try:
            headers = {}
            if settings.GITHUB_TOKEN:
                headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"
            
            # GitHub Search API
            url = f"https://api.github.com/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": limit
            }
            
            response = await self.client.get(url, params=params, headers=headers)
            
            if response.status_code != 200:
                print(f"GitHub API error: {response.status_code}")
                return []
            
            data = response.json()
            repositories = []
            
            for repo in data.get("items", [])[:limit]:
                repositories.append({
                    "source": "github",
                    "type": "repository",
                    "title": repo.get("full_name", ""),
                    "description": repo.get("description", ""),
                    "url": repo.get("html_url", ""),
                    "stars": repo.get("stargazers_count", 0),
                    "language": repo.get("language", ""),
                    "topics": repo.get("topics", []),
                    "updated_at": repo.get("updated_at", ""),
                    "author": repo.get("owner", {}).get("login", ""),
                    "license": repo.get("license", {}).get("name", "") if repo.get("license") else ""
                })
            
            return repositories
            
        except Exception as e:
            print(f"Error scraping GitHub: {e}")
            return []
    
    async def search_youtube(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search YouTube for tutorial videos using YouTube Data API v3.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of video details with metadata
        """
        try:
            if not settings.YOUTUBE_API_KEY:
                print("YouTube API key not configured")
                return []
            
            # YouTube Data API v3
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": limit,
                "order": "relevance",
                "key": settings.YOUTUBE_API_KEY
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code != 200:
                print(f"YouTube API error: {response.status_code}")
                return []
            
            data = response.json()
            videos = []
            
            for item in data.get("items", []):
                video_id = item.get("id", {}).get("videoId", "")
                snippet = item.get("snippet", {})
                
                videos.append({
                    "source": "youtube",
                    "type": "video",
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "published_at": snippet.get("publishedAt", ""),
                })
            
            return videos
            
        except Exception as e:
            print(f"Error scraping YouTube: {e}")
            return []
    
    async def search_reddit(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search Reddit for relevant discussions
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of Reddit posts
        """
        try:
            # Use Reddit's public JSON API (no auth needed for search)
            url = "https://www.reddit.com/search.json"
            params = {
                "q": query,
                "limit": limit,
                "sort": "relevance"
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code != 200:
                print(f"Reddit API error: {response.status_code}")
                return []
            
            data = response.json()
            posts = []
            
            for item in data.get("data", {}).get("children", []):
                post = item.get("data", {})
                
                posts.append({
                    "source": "reddit",
                    "type": "discussion",
                    "title": post.get("title", ""),
                    "description": post.get("selftext", "")[:500],
                    "url": f"https://www.reddit.com{post.get('permalink', '')}",
                    "subreddit": post.get("subreddit", ""),
                    "score": post.get("score", 0),
                    "num_comments": post.get("num_comments", 0),
                    "author": post.get("author", ""),
                    "created_at": datetime.fromtimestamp(post.get("created_utc", 0)).isoformat()
                })
            
            return posts
            
        except Exception as e:
            print(f"Error scraping Reddit: {e}")
            return []
    
    async def search_stackoverflow(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search Stack Overflow for Q&A using Stack Exchange API.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of questions and answers
        """
        try:
            # Stack Exchange API (no key needed for basic search)
            url = "https://api.stackexchange.com/2.3/search/advanced"
            params = {
                "q": query,
                "order": "desc",
                "sort": "relevance",
                "site": "stackoverflow",
                "pagesize": limit,
                "filter": "withbody"  # Include question body
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code != 200:
                print(f"StackOverflow API error: {response.status_code}")
                return []
            
            data = response.json()
            questions = []
            
            for item in data.get("items", []):
                questions.append({
                    "source": "stackoverflow",
                    "type": "qa",
                    "title": item.get("title", ""),
                    "description": BeautifulSoup(item.get("body", ""), "html.parser").get_text()[:500],
                    "url": item.get("link", ""),
                    "score": item.get("score", 0),
                    "answer_count": item.get("answer_count", 0),
                    "is_answered": item.get("is_answered", False),
                    "tags": item.get("tags", []),
                    "author": item.get("owner", {}).get("display_name", ""),
                    "created_at": datetime.fromtimestamp(item.get("creation_date", 0)).isoformat()
                })
            
            return questions
            
        except Exception as e:
            print(f"Error scraping StackOverflow: {e}")
            return []
    
    async def search_google(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search Google using Custom Search API.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of web pages
        """
        try:
            if not settings.GOOGLE_SEARCH_API_KEY or not settings.GOOGLE_SEARCH_ENGINE_ID:
                print("Google Custom Search API not configured")
                return []
            
            # Google Custom Search API
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": settings.GOOGLE_SEARCH_API_KEY,
                "cx": settings.GOOGLE_SEARCH_ENGINE_ID,
                "q": query,
                "num": min(limit, 10)  # Max 10 per request
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code != 200:
                reason = ""
                message = ""
                try:
                    error_payload = response.json().get("error", {})
                    message = str(error_payload.get("message", ""))[:300]
                    errors = error_payload.get("errors", [])
                    if errors and isinstance(errors, list):
                        first_error = errors[0]
                        reason = str(first_error.get("reason", ""))[:120]
                except Exception:
                    message = response.text[:300]
                logger.warning(
                    "Google CSE rejected request status=%s reason=%s message=%s query_len=%s",
                    response.status_code,
                    reason or "unknown",
                    message or "no message",
                    len(query or ""),
                )
                return []
            
            data = response.json()
            results = []
            
            for item in data.get("items", []):
                results.append({
                    "source": "google",
                    "type": "webpage",
                    "title": item.get("title", ""),
                    "description": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "display_url": item.get("displayLink", "")
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching Google: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Singleton instance
scraper_service = ScraperService()
