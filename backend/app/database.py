import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

class JSONDatabase:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.lock = threading.Lock()
        self._init_data_files()

    def _init_data_files(self):
        self.files = {
            "tenants": self.data_dir / "tenants.json",
            "users": self.data_dir / "users.json",
            "exploitations": self.data_dir / "exploitations.json",
            "parcelles": self.data_dir / "parcelles.json",
            "rendements": self.data_dir / "rendements.json",
            "meteo_data": self.data_dir / "meteo_data.json",
            "sol_qualite": self.data_dir / "sol_qualite.json",
            "intrants": self.data_dir / "intrants.json",
            "alertes": self.data_dir / "alertes.json",
            "rapports": self.data_dir / "rapports.json",
            "analyses_predictions": self.data_dir / "analyses_predictions.json",
            "audit_logs": self.data_dir / "audit_logs.json"
        }
        for file_path in self.files.values():
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump([], f)

    def _load_data(self, table: str) -> List[Dict]:
        with self.lock:
            try:
                with open(self.files[table], 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return []

    def _save_data(self, table: str, data: List[Dict]):
        with self.lock:
            with open(self.files[table], 'w') as f:
                json.dump(data, f, indent=2, default=str)

    def insert(self, table: str, record: Dict) -> Dict:
        data = self._load_data(table)
        if 'id' not in record:
            record['id'] = len(data) + 1
        record['created_at'] = datetime.utcnow().isoformat()
        record['updated_at'] = datetime.utcnow().isoformat()
        data.append(record)
        self._save_data(table, data)
        return record

    def update(self, table: str, record_id: int, updates: Dict) -> Optional[Dict]:
        data = self._load_data(table)
        for i, record in enumerate(data):
            if record.get('id') == record_id:
                updates['updated_at'] = datetime.utcnow().isoformat()
                data[i].update(updates)
                self._save_data(table, data)
                return data[i]
        return None

    def delete(self, table: str, record_id: int) -> bool:
        data = self._load_data(table)
        original_length = len(data)
        data = [r for r in data if r.get('id') != record_id]
        if len(data) < original_length:
            self._save_data(table, data)
            return True
        return False

    def get_by_id(self, table: str, record_id: int) -> Optional[Dict]:
        data = self._load_data(table)
        for record in data:
            if record.get('id') == record_id:
                return record
        return None

    def query(self, table: str, filters: Optional[Dict] = None, order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        data = self._load_data(table)
        if filters:
            filtered_data = []
            for record in data:
                match = True
                for key, value in filters.items():
                    if record.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_data.append(record)
            data = filtered_data
        if order_by:
            data.sort(key=lambda x: x.get(order_by, ''), reverse=True)
        if limit:
            data = data[:limit]
        return data

    def get_all(self, table: str) -> List[Dict]:
        return self._load_data(table)

db = JSONDatabase()

async def init_db():
    pass


def get_db():
    """Get database session - dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
