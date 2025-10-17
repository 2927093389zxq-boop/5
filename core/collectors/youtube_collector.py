"""
YouTube data collector for channel statistics.
"""

from datetime import datetime
from typing import Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)


def fetch_channel_stats(channel_id: str) -> Dict[str, Any]:
    """
    Fetch statistics for a YouTube channel.
    
    Args:
        channel_id: YouTube channel ID
        
    Returns:
        Dictionary containing channel statistics
    """
    # Check if API key is available
    api_key = os.getenv("YOUTUBE_API_KEY")
    
    if not api_key:
        logger.warning("YouTube API key not configured")
        return {
            "channel_id": channel_id,
            "error": "YouTube API密钥未配置",
            "note": "请在.env文件中设置YOUTUBE_API_KEY",
            "fetched_at": datetime.now().isoformat()
        }
    
    try:
        # Try to use the Google API client if available
        from googleapiclient.discovery import build
        
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Fetch channel statistics
        request = youtube.channels().list(
            part='statistics,snippet',
            id=channel_id
        )
        response = request.execute()
        
        if not response.get('items'):
            return {
                "channel_id": channel_id,
                "error": "频道未找到",
                "fetched_at": datetime.now().isoformat()
            }
        
        item = response['items'][0]
        stats = item['statistics']
        snippet = item['snippet']
        
        return {
            "channel_id": channel_id,
            "title": snippet.get('title'),
            "description": snippet.get('description', '')[:200],
            "subscriber_count": int(stats.get('subscriberCount', 0)),
            "video_count": int(stats.get('videoCount', 0)),
            "view_count": int(stats.get('viewCount', 0)),
            "published_at": snippet.get('publishedAt'),
            "fetched_at": datetime.now().isoformat()
        }
        
    except ImportError:
        logger.error("Google API client not installed")
        return {
            "channel_id": channel_id,
            "error": "Google API客户端未安装",
            "note": "运行: pip install google-api-python-client",
            "fetched_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching YouTube stats: {e}")
        return {
            "channel_id": channel_id,
            "error": str(e),
            "fetched_at": datetime.now().isoformat()
        }
