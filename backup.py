import json
import os
import shutil
from datetime import datetime
from typing import Dict, List
import zipfile

class BackupManager:
    """Database backup and restore manager"""
    
    def __init__(self, db):
        self.db = db
        self.backup_dir = "backups"
        self.max_backups = 30  # Keep last 30 backups
        
        # Create backup directory if not exists
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self) -> Dict:
        """Create a complete backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Create backup directory
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup all JSON files
            backup_data = {}
            
            # Users
            if hasattr(self.db, 'users'):
                users_file = os.path.join(backup_path, "users.json")
                with open(users_file, 'w', encoding='utf-8') as f:
                    json.dump(self.db.users, f, indent=2, ensure_ascii=False)
                backup_data["users"] = len(self.db.users)
            
            # Payments
            if hasattr(self.db, 'payments'):
                payments_file = os.path.join(backup_path, "payments.json")
                with open(payments_file, 'w', encoding='utf-8') as f:
                    json.dump(self.db.payments, f, indent=2, ensure_ascii=False)
                backup_data["payments"] = len(self.db.payments)
            
            # Games
            if hasattr(self.db, 'games'):
                games_file = os.path.join(backup_path, "games.json")
                with open(games_file, 'w', encoding='utf-8') as f:
                    json.dump(self.db.games, f, indent=2, ensure_ascii=False)
                backup_data["games"] = len(self.db.games)
            
            # Shop
            if hasattr(self.db, 'shop'):
                shop_file = os.path.join(backup_path, "shop.json")
                with open(shop_file, 'w', encoding='utf-8') as f:
                    json.dump(self.db.shop, f, indent=2, ensure_ascii=False)
                backup_data["shop_items"] = len(self.db.shop.get("items", []))
            
            # Groups
            if hasattr(self.db, 'groups'):
                groups_file = os.path.join(backup_path, "groups.json")
                with open(groups_file, 'w', encoding='utf-8') as f:
                    json.dump(self.db.groups, f, indent=2, ensure_ascii=False)
                backup_data["groups"] = len(self.db.groups)
            
            # Create backup info file
            info = {
                "name": backup_name,
                "timestamp": datetime.now().isoformat(),
                "data": backup_data,
                "version": "1.0",
                "bot": "MARPD Ultra Pro Max"
            }
            
            info_file = os.path.join(backup_path, "backup_info.json")
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=2, ensure_ascii=False)
            
            # Create zip archive
            zip_path = f"{backup_path}.zip"
            self._create_zip(backup_path, zip_path)
            
            # Cleanup temporary directory
            shutil.rmtree(backup_path)
            
            # Clean old backups
            self._clean_old_backups()
            
            return {
                "success": True,
                "message": f"✅ Backup created: {backup_name}",
                "backup_name": backup_name,
                "file": zip_path,
                "stats": backup_data,
                "size": os.path.getsize(zip_path) if os.path.exists(zip_path) else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Backup failed: {str(e)}"
            }
    
    def _create_zip(self, source_dir: str, zip_path: str):
        """Create zip archive"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
    
    def _clean_old_backups(self):
        """Clean old backups keeping only max_backups"""
        try:
            # List all backup files
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.endswith('.zip'):
                    file_path = os.path.join(self.backup_dir, file)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # Sort by modification time (oldest first)
            backup_files.sort(key=lambda x: x[1])
            
            # Remove old backups
            while len(backup_files) > self.max_backups:
                oldest_file = backup_files.pop(0)[0]
                os.remove(oldest_file)
                print(f"🧹 Removed old backup: {os.path.basename(oldest_file)}")
                
        except Exception as e:
            print(f"⚠️ Error cleaning old backups: {e}")
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        try:
            for file in os.listdir(self.backup_dir):
                if file.endswith('.zip'):
                    file_path = os.path.join(self.backup_dir, file)
                    
                    # Extract backup info
                    info = self._get_backup_info(file_path)
                    
                    backups.append({
                        "name": file.replace('.zip', ''),
                        "file": file,
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "created": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                        "info": info
                    })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x["created"], reverse=True)
            
        except Exception as e:
            print(f"⚠️ Error listing backups: {e}")
        
        return backups
    
    def _get_backup_info(self, zip_path: str) -> Dict:
        """Get backup information from zip"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                if "backup_info.json" in zipf.namelist():
                    with zipf.open("backup_info.json") as f:
                        info = json.load(f)
                    return info
        except:
            pass
        
        # Return default info if cannot read
        return {
            "name": os.path.basename(zip_path).replace('.zip', ''),
            "timestamp": datetime.fromtimestamp(os.path.getmtime(zip_path)).isoformat()
        }
    
    def restore_backup(self, backup_name: str) -> Dict:
        """Restore from backup"""
        try:
            zip_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
            
            if not os.path.exists(zip_path):
                return {
                    "success": False,
                    "message": f"❌ Backup not found: {backup_name}"
                }
            
            # Create temporary directory for extraction
            temp_dir = os.path.join(self.backup_dir, "temp_restore")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract backup
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Restore data
            restore_stats = {}
            
            # Users
            users_file = os.path.join(temp_dir, "users.json")
            if os.path.exists(users_file):
                with open(users_file, 'r', encoding='utf-8') as f:
                    self.db.users = json.load(f)
                restore_stats["users"] = len(self.db.users)
            
            # Payments
            payments_file = os.path.join(temp_dir, "payments.json")
            if os.path.exists(payments_file):
                with open(payments_file, 'r', encoding='utf-8') as f:
                    self.db.payments = json.load(f)
                restore_stats["payments"] = len(self.db.payments)
            
            # Games
            games_file = os.path.join(temp_dir, "games.json")
            if os.path.exists(games_file):
                with open(games_file, 'r', encoding='utf-8') as f:
                    self.db.games = json.load(f)
                restore_stats["games"] = len(self.db.games)
            
            # Shop
            shop_file = os.path.join(temp_dir, "shop.json")
            if os.path.exists(shop_file):
                with open(shop_file, 'r', encoding='utf-8') as f:
                    self.db.shop = json.load(f)
                restore_stats["shop_items"] = len(self.db.shop.get("items", []))
            
            # Groups
            groups_file = os.path.join(temp_dir, "groups.json")
            if os.path.exists(groups_file):
                with open(groups_file, 'r', encoding='utf-8') as f:
                    self.db.groups = json.load(f)
                restore_stats["groups"] = len(self.db.groups)
            
            # Save restored data
            self.db._save_json("users.json", self.db.users)
            self.db._save_json("payments.json", self.db.payments)
            self.db._save_json("games.json", self.db.games)
            self.db._save_json("shop.json", self.db.shop)
            self.db._save_json("groups.json", self.db.groups)
            
            # Cleanup temporary directory
            shutil.rmtree(temp_dir)
            
            return {
                "success": True,
                "message": f"✅ Backup restored: {backup_name}",
                "backup_name": backup_name,
                "restored": restore_stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Restore failed: {str(e)}"
            }
    
    def delete_backup(self, backup_name: str) -> Dict:
        """Delete a backup"""
        try:
            zip_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
            
            if not os.path.exists(zip_path):
                return {
                    "success": False,
                    "message": f"❌ Backup not found: {backup_name}"
                }
            
            os.remove(zip_path)
            
            return {
                "success": True,
                "message": f"🗑️ Backup deleted: {backup_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Delete failed: {str(e)}"
            }
    
    def get_backup_stats(self) -> Dict:
        """Get backup statistics"""
        backups = self.list_backups()
        
        total_size = sum(b["size"] for b in backups)
        total_count = len(backups)
        
        return {
            "total_backups": total_count,
            "total_size": total_size,
            "oldest": backups[-1]["name"] if backups else None,
            "newest": backups[0]["name"] if backups else None,
            "backups": backups[:5]  # Last 5 backups
        }