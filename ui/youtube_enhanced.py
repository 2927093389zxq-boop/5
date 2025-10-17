"""
YouTube频道查询UI - 增强版
Enhanced YouTube Channel Query UI with video-to-text and OpenAI summarization
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


def render_youtube_query():
    """
    渲染YouTube频道查询界面，支持视频转文本和OpenAI总结
    Render YouTube channel query UI with video-to-text and OpenAI summarization
    """
    st.header("📺 YouTube频道深度分析")
    st.markdown("输入频道ID获取完整频道信息，包括所有视频内容分析和AI总结")
    
    # API密钥检查
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    col1, col2 = st.columns(2)
    with col1:
        if youtube_api_key:
            st.success("✅ YouTube API已配置")
        else:
            st.warning("⚠️ YouTube API未配置")
            st.info("请在.env文件中设置 YOUTUBE_API_KEY")
    
    with col2:
        if openai_api_key:
            st.success("✅ OpenAI API已配置")
        else:
            st.warning("⚠️ OpenAI API未配置")
            st.info("可选：设置 OPENAI_API_KEY 以启用AI总结")
    
    st.markdown("---")
    
    # 输入频道ID
    col1, col2 = st.columns([3, 1])
    with col1:
        channel_id = st.text_input(
            "频道ID", 
            placeholder="例如: UCuAXFkgsw1L7xaCfnd5JJOw",
            help="YouTube频道URL中的ID，通常在 /channel/ 后面"
        )
    
    with col2:
        st.write("")
        st.write("")
        max_videos = st.number_input("最大视频数", min_value=1, max_value=50, value=10)
    
    # 分析选项
    col1, col2, col3 = st.columns(3)
    with col1:
        analyze_videos = st.checkbox("分析所有视频", value=True)
    with col2:
        extract_transcripts = st.checkbox("提取视频文本", value=True)
    with col3:
        ai_summarize = st.checkbox("AI智能总结", value=openai_api_key is not None)
    
    if st.button("🔍 开始分析", type="primary"):
        if not channel_id:
            st.error("请输入频道ID")
            return
        
        if not youtube_api_key:
            st.error("请先配置YouTube API密钥")
            return
        
        with st.spinner("正在获取频道信息..."):
            try:
                # 1. 获取频道基础信息
                channel_stats = get_channel_statistics(channel_id)
                
                if 'error' in channel_stats:
                    st.error(f"获取频道信息失败: {channel_stats['error']}")
                    if 'note' in channel_stats:
                        st.info(channel_stats['note'])
                    return
                
                # 显示频道信息
                st.markdown("### 📊 频道统计信息")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("频道名称", channel_stats.get('title', 'N/A'))
                with col2:
                    subscriber_count = channel_stats.get('subscriber_count', 0)
                    st.metric("订阅数", f"{subscriber_count:,}")
                with col3:
                    video_count = channel_stats.get('video_count', 0)
                    st.metric("视频总数", f"{video_count:,}")
                with col4:
                    view_count = channel_stats.get('view_count', 0)
                    st.metric("总观看数", f"{view_count:,}")
                
                # 频道描述
                if channel_stats.get('description'):
                    with st.expander("📝 频道简介"):
                        st.write(channel_stats['description'])
                
                st.markdown("---")
                
                # 2. 获取视频列表
                if analyze_videos:
                    st.markdown("### 🎬 视频内容分析")
                    
                    with st.spinner(f"正在获取前{max_videos}个视频..."):
                        videos = get_channel_videos(channel_id, max_videos)
                        
                        if not videos:
                            st.warning("未找到视频")
                            return
                        
                        st.success(f"找到 {len(videos)} 个视频")
                        
                        # 显示视频列表
                        video_analysis_results = []
                        
                        for idx, video in enumerate(videos, 1):
                            with st.expander(f"🎥 {idx}. {video.get('title', 'Unknown')}", expanded=(idx == 1)):
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.markdown(f"**标题:** {video.get('title', 'N/A')}")
                                    st.markdown(f"**描述:** {video.get('description', 'N/A')[:200]}...")
                                    st.markdown(f"**发布时间:** {video.get('published_at', 'N/A')}")
                                
                                with col2:
                                    st.metric("观看次数", f"{video.get('view_count', 0):,}")
                                    st.metric("点赞数", f"{video.get('like_count', 0):,}")
                                    st.metric("评论数", f"{video.get('comment_count', 0):,}")
                                
                                # 提取视频文本
                                transcript_text = ""
                                if extract_transcripts:
                                    with st.spinner("正在提取视频文本..."):
                                        transcript = get_video_transcript(video['video_id'])
                                        
                                        if transcript and 'text' in transcript:
                                            transcript_text = transcript['text']
                                            st.markdown("#### 📄 视频文本内容")
                                            
                                            # 显示文本摘要
                                            word_count = len(transcript_text.split())
                                            st.caption(f"共 {word_count} 个词")
                                            
                                            # 可展开查看完整文本
                                            with st.expander("查看完整文本"):
                                                st.text_area("", transcript_text, height=300, key=f"transcript_{video['video_id']}")
                                        elif transcript and 'error' in transcript:
                                            st.info(f"无法获取文本: {transcript['error']}")
                                
                                # AI总结
                                if ai_summarize and openai_api_key and transcript_text:
                                    with st.spinner("AI正在生成总结..."):
                                        summary = generate_video_summary(
                                            video.get('title', ''),
                                            video.get('description', ''),
                                            transcript_text
                                        )
                                        
                                        if summary and 'summary' in summary:
                                            st.markdown("#### 🤖 AI智能总结")
                                            st.info(summary['summary'])
                                            
                                            # 保存分析结果
                                            video_analysis_results.append({
                                                'video_id': video['video_id'],
                                                'title': video.get('title'),
                                                'transcript_length': len(transcript_text),
                                                'ai_summary': summary['summary']
                                            })
                                        elif summary and 'error' in summary:
                                            st.warning(f"AI总结失败: {summary['error']}")
                        
                        # 保存分析结果
                        if video_analysis_results:
                            st.markdown("---")
                            if st.button("💾 保存完整分析结果"):
                                output_dir = "data/youtube"
                                os.makedirs(output_dir, exist_ok=True)
                                
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                output_file = f"{output_dir}/channel_{channel_id}_{timestamp}.json"
                                
                                full_results = {
                                    "channel_id": channel_id,
                                    "channel_stats": channel_stats,
                                    "videos_analyzed": len(video_analysis_results),
                                    "video_details": video_analysis_results,
                                    "analyzed_at": datetime.now().isoformat()
                                }
                                
                                with open(output_file, 'w', encoding='utf-8') as f:
                                    json.dump(full_results, f, ensure_ascii=False, indent=2)
                                
                                st.success(f"✅ 分析结果已保存: {output_file}")
                
            except Exception as e:
                st.error(f"分析失败: {e}")
                import traceback
                with st.expander("查看错误详情"):
                    st.code(traceback.format_exc())


def get_channel_statistics(channel_id: str) -> Dict[str, Any]:
    """获取频道统计信息 / Get channel statistics"""
    try:
        from googleapiclient.discovery import build
        
        youtube = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_API_KEY"))
        
        request = youtube.channels().list(
            part='statistics,snippet',
            id=channel_id
        )
        response = request.execute()
        
        if not response.get('items'):
            return {"error": "频道未找到"}
        
        item = response['items'][0]
        stats = item['statistics']
        snippet = item['snippet']
        
        return {
            "channel_id": channel_id,
            "title": snippet.get('title'),
            "description": snippet.get('description', ''),
            "subscriber_count": int(stats.get('subscriberCount', 0)),
            "video_count": int(stats.get('videoCount', 0)),
            "view_count": int(stats.get('viewCount', 0)),
            "published_at": snippet.get('publishedAt'),
            "fetched_at": datetime.now().isoformat()
        }
        
    except ImportError:
        return {
            "error": "Google API客户端未安装",
            "note": "运行: pip install google-api-python-client"
        }
    except Exception as e:
        logger.error(f"Error getting channel statistics: {e}")
        return {"error": str(e)}


def get_channel_videos(channel_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """获取频道所有视频 / Get all videos from channel"""
    try:
        from googleapiclient.discovery import build
        
        youtube = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_API_KEY"))
        
        # 获取上传播放列表ID
        channel_request = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        )
        channel_response = channel_request.execute()
        
        if not channel_response.get('items'):
            return []
        
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # 获取视频列表
        videos = []
        next_page_token = None
        
        while len(videos) < max_results:
            playlist_request = youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            )
            playlist_response = playlist_request.execute()
            
            for item in playlist_response.get('items', []):
                snippet = item['snippet']
                video_id = snippet['resourceId']['videoId']
                
                # 获取视频详细统计
                video_stats = get_video_statistics(video_id)
                
                videos.append({
                    'video_id': video_id,
                    'title': snippet.get('title'),
                    'description': snippet.get('description'),
                    'published_at': snippet.get('publishedAt'),
                    **video_stats
                })
            
            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break
        
        return videos[:max_results]
        
    except Exception as e:
        logger.error(f"Error getting channel videos: {e}")
        return []


def get_video_statistics(video_id: str) -> Dict[str, Any]:
    """获取视频统计信息 / Get video statistics"""
    try:
        from googleapiclient.discovery import build
        
        youtube = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_API_KEY"))
        
        request = youtube.videos().list(
            part='statistics',
            id=video_id
        )
        response = request.execute()
        
        if not response.get('items'):
            return {}
        
        stats = response['items'][0]['statistics']
        
        return {
            'view_count': int(stats.get('viewCount', 0)),
            'like_count': int(stats.get('likeCount', 0)),
            'comment_count': int(stats.get('commentCount', 0))
        }
        
    except Exception as e:
        logger.error(f"Error getting video statistics: {e}")
        return {}


# Constants for better maintenance
TRANSCRIPT_INSTALL_MESSAGE = "安装 youtube-transcript-api 以启用自动文本提取: pip install youtube-transcript-api"

def get_video_transcript(video_id: str) -> Dict[str, Any]:
    """
    提取视频文本（使用youtube-transcript-api或yt-dlp）
    Extract video transcript using youtube-transcript-api or yt-dlp
    """
    try:
        # 尝试使用 youtube-transcript-api
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh', 'en'])
            
            # 合并所有文本
            full_text = ' '.join([item['text'] for item in transcript_list])
            
            return {
                'video_id': video_id,
                'text': full_text,
                'source': 'youtube-transcript-api',
                'fetched_at': datetime.now().isoformat()
            }
            
        except ImportError:
            # 如果youtube-transcript-api未安装，尝试使用yt-dlp
            import subprocess
            import re
            
            # 验证video_id格式（只允许字母数字和-_字符）
            if not re.match(r'^[a-zA-Z0-9_-]+$', video_id):
                return {
                    'video_id': video_id,
                    'error': 'Invalid video ID format'
                }
            
            # 使用yt-dlp获取字幕（安全的方式）
            try:
                result = subprocess.run(
                    ['yt-dlp', '--skip-download', '--write-auto-sub', '--sub-lang', 'en', '--sub-format', 'vtt', 
                     f'https://www.youtube.com/watch?v={video_id}'],
                    capture_output=True,
                    text=True,
                    timeout=30  # 添加超时限制
                )
                
                if result.returncode == 0:
                    # 解析VTT文件
                    return {
                        'video_id': video_id,
                        'text': '字幕提取需要安装youtube-transcript-api: pip install youtube-transcript-api',
                        'source': 'yt-dlp',
                        'error': 'Manual VTT parsing required'
                    }
                else:
                    return {
                        'video_id': video_id,
                        'error': 'No transcript available or tools not installed'
                    }
            except subprocess.TimeoutExpired:
                return {
                    'video_id': video_id,
                    'error': 'Transcript extraction timed out'
                }
            except FileNotFoundError:
                return {
                    'video_id': video_id,
                    'error': 'yt-dlp not installed',
                    'note': TRANSCRIPT_INSTALL_MESSAGE
                }
                
    except Exception as e:
        logger.error(f"Error getting video transcript: {e}")
        return {
            'video_id': video_id,
            'error': str(e),
            'note': TRANSCRIPT_INSTALL_MESSAGE
        }


def generate_video_summary(title: str, description: str, transcript: str) -> Dict[str, Any]:
    """
    使用OpenAI生成视频总结
    Generate video summary using OpenAI
    """
    try:
        import openai
        
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # 限制文本长度以避免超过token限制
        max_transcript_length = 3000
        truncated_transcript = transcript[:max_transcript_length]
        
        prompt = f"""
请为以下YouTube视频生成一个简洁的中文总结（200字以内）：

标题: {title}

描述: {description[:300]}

视频文本内容:
{truncated_transcript}

请提供:
1. 视频主要内容概述（2-3句话）
2. 关键要点（3-5个要点）
3. 目标受众
4. 推荐理由
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一位专业的视频内容分析师，擅长提炼视频要点。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        summary = response.choices[0].message.content
        
        return {
            'summary': summary,
            'model': 'gpt-3.5-turbo',
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating video summary: {e}")
        return {'error': str(e)}
