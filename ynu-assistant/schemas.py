from pydantic import BaseModel
from typing import Dict, Any, List, Union

class ChatMessage(BaseModel):
    role: str  # user/assistant
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: bool = False

class AgentResponse(BaseModel):
    type: str  # kg/vector/tool/open
    data: Union[List[Dict], str]
    metadata: Dict[str, Any] = {}