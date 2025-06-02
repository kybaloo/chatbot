from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class Message(BaseModel):
    """Modèle pour représenter un message dans une conversation"""
    role: str  # "user" ou "assistant"
    content: str
    timestamp: datetime = None

    def __init__(self, **data):
        if "timestamp" not in data or data["timestamp"] is None:
            data["timestamp"] = datetime.now()
        super().__init__(**data)
    
    def to_dynamo_item(self) -> Dict[str, Any]:
        """Convertit le message en format DynamoDB"""
        return {
            "role": {"S": self.role},
            "content": {"S": self.content},
            "timestamp": {"S": self.timestamp.isoformat()}
        }
    
    @classmethod
    def from_dynamo_item(cls, item: Dict[str, Dict[str, str]]) -> "Message":
        """Crée un objet Message à partir d'un item DynamoDB"""
        return cls(
            role=item.get("role", {}).get("S", ""),
            content=item.get("content", {}).get("S", ""),
            timestamp=datetime.fromisoformat(item.get("timestamp", {}).get("S", datetime.now().isoformat()))
        )


class Conversation(BaseModel):
    """Modèle pour représenter une conversation complète"""
    conversation_id: str
    user_id: str
    username: Optional[str] = None
    messages: List[Message] = []
    created_at: datetime = None
    updated_at: datetime = None

    def __init__(self, **data):
        now = datetime.now()
        if "created_at" not in data or data["created_at"] is None:
            data["created_at"] = now
        if "updated_at" not in data or data["updated_at"] is None:
            data["updated_at"] = now
        if "messages" not in data:
            data["messages"] = []
        super().__init__(**data)
    
    def add_message(self, role: str, content: str) -> Message:
        """Ajoute un message à la conversation et met à jour le timestamp"""
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def to_dynamo_item(self) -> Dict[str, Any]:
        """Convertit la conversation en format DynamoDB"""
        return {
            "PK": {"S": f"USER#{self.user_id}"},
            "SK": {"S": f"CONV#{self.conversation_id}"},
            "conversation_id": {"S": self.conversation_id},
            "user_id": {"S": self.user_id},
            "username": {"S": self.username} if self.username else {"NULL": True},
            "messages": {"L": [{"M": msg.to_dynamo_item()} for msg in self.messages]},
            "created_at": {"S": self.created_at.isoformat()},
            "updated_at": {"S": self.updated_at.isoformat()},
            "ttl": {"N": str(int(self.updated_at.timestamp()) + (60 * 60 * 24 * 30))}  # TTL de 30 jours
        }
    
    @classmethod
    def from_dynamo_item(cls, item: Dict[str, Any]) -> "Conversation":
        """Crée un objet Conversation à partir d'un item DynamoDB"""
        messages = []
        if "messages" in item and "L" in item["messages"]:
            for msg_item in item["messages"]["L"]:
                if "M" in msg_item:
                    messages.append(Message.from_dynamo_item(msg_item["M"]))
        
        username = None
        if "username" in item and "S" in item["username"]:
            username = item["username"]["S"]

        return cls(
            conversation_id=item.get("conversation_id", {}).get("S", ""),
            user_id=item.get("user_id", {}).get("S", ""),
            username=username,
            messages=messages,
            created_at=datetime.fromisoformat(item.get("created_at", {}).get("S", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(item.get("updated_at", {}).get("S", datetime.now().isoformat()))
        )
