import os
import shutil
from typing import Optional, Dict
from datetime import datetime

class MediaHandler:
    """Media file handler"""
    
    def __init__(self):
        self.media_dir = "media"
        self.max_size_mb = 10  # Maximum file size in MB
        
        # Create media directory structure
        os.makedirs(os.path.join(self.media_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(self.media_dir, "documents"), exist_ok=True)
        os.makedirs(os.path.join(self.media_dir, "videos"), exist_ok=True)
        os.makedirs(os.path.join(self.media_dir, "audio"), exist_ok=True)
    
    async def save_image(self, file_content: bytes, filename: str) -> Optional[str]:
        """Save image file"""
        return await self._save_file(file_content, filename, "images")
    
    async def save_document(self, file_content: bytes, filename: str) -> Optional[str]:
        """Save document file"""
        return await self._save_file(file_content, filename, "documents")
    
    async def save_video(self, file_content: bytes, filename: str) -> Optional[str]:
        """Save video file"""
        return await self._save_file(file_content, filename, "videos")
    
    async def save_audio(self, file_content: bytes, filename: str) -> Optional[str]:
        """Save audio file"""
        return await self._save_file(file_content, filename, "audio")
    
    async def _save_file(self, file_content: bytes, filename: str, file_type: str) -> Optional[str]:
        """Save file with validation"""
        try:
            # Check file size
            file_size_mb = len(file_content) / (1024 * 1024)
            if file_size_mb > self.max_size_mb:
                print(f"⚠️ File too large: {file_size_mb:.2f} MB > {self.max_size_mb} MB")
                return None
            
            # Generate safe filename
            safe_filename = self._generate_safe_filename(filename)
            
            # Create full path
            file_path = os.path.join(self.media_dir, file_type, safe_filename)
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            print(f"✅ File saved: {file_path} ({file_size_mb:.2f} MB)")
            return file_path
            
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return None
    
    def _generate_safe_filename(self, original_filename: str) -> str:
        """Generate safe filename"""
        # Remove unsafe characters
        safe_name = "".join(c for c in original_filename if c.isalnum() or c in '._- ').rstrip()
        
        # Add timestamp to avoid collisions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(safe_name)
        
        if not ext:
            ext = ".dat"
        
        return f"{name}_{timestamp}{ext}"
    
    async def get_file_info(self, file_path: str) -> Optional[Dict]:
        """Get file information"""
        if not os.path.exists(file_path):
            return None
        
        try:
            stats = os.stat(file_path)
            
            return {
                "path": file_path,
                "size": stats.st_size,
                "size_mb": stats.st_size / (1024 * 1024),
                "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "type": self._get_file_type(file_path)
            }
        except Exception as e:
            print(f"❌ Error getting file info: {e}")
            return None
    
    def _get_file_type(self, file_path: str) -> str:
        """Get file type from extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        audio_exts = ['.mp3', '.wav', '.ogg', '.m4a']
        doc_exts = ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx']
        
        if ext in image_exts:
            return "image"
        elif ext in video_exts:
            return "video"
        elif ext in audio_exts:
            return "audio"
        elif ext in doc_exts:
            return "document"
        else:
            return "unknown"
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ File deleted: {file_path}")
                return True
        except Exception as e:
            print(f"❌ Error deleting file: {e}")
        
        return False
    
    async def cleanup_old_files(self, days_old: int = 30):
        """Cleanup files older than specified days"""
        try:
            deleted_count = 0
            
            for root, dirs, files in os.walk(self.media_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check file age
                    file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_age.days > days_old:
                        os.remove(file_path)
                        deleted_count += 1
            
            print(f"🧹 Cleaned up {deleted_count} old files (older than {days_old} days)")
            return deleted_count
            
        except Exception as e:
            print(f"❌ Error cleaning up files: {e}")
            return 0
    
    async def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        stats = {
            "total_size": 0,
            "file_count": 0,
            "by_type": {
                "images": {"count": 0, "size": 0},
                "videos": {"count": 0, "size": 0},
                "audio": {"count": 0, "size": 0},
                "documents": {"count": 0, "size": 0}
            }
        }
        
        try:
            for root, dirs, files in os.walk(self.media_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    try:
                        file_size = os.path.getsize(file_path)
                        file_type = self._get_file_type(file_path)
                        
                        stats["total_size"] += file_size
                        stats["file_count"] += 1
                        
                        if file_type in stats["by_type"]:
                            stats["by_type"][file_type]["count"] += 1
                            stats["by_type"][file_type]["size"] += file_size
                    except:
                        continue
            
            # Convert sizes to MB
            stats["total_size_mb"] = stats["total_size"] / (1024 * 1024)
            
            for file_type in stats["by_type"]:
                stats["by_type"][file_type]["size_mb"] = stats["by_type"][file_type]["size"] / (1024 * 1024)
            
        except Exception as e:
            print(f"❌ Error getting storage stats: {e}")
        
        return stats