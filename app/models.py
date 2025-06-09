from pydantic import BaseModel
from typing import List, Optional

class Connection(BaseModel):
    name: str
    title: Optional[str]
    profile_url: str

class ConnectionResponse(BaseModel):
    connections: List[Connection]
    start: int
    count: int
