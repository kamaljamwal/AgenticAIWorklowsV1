from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum

class AgentType(str, Enum):
    JIRA = "jira"
    GITHUB = "github"
    API = "api"
    FILESYSTEM = "filesystem"
    VIDEO = "video"
    S3 = "s3"
    URL = "url"

class QueryRequest(BaseModel):
    prompt: str
    max_results: Optional[int] = 10
    specific_sources: Optional[List[AgentType]] = None

class AgentResponse(BaseModel):
    agent_type: AgentType
    success: bool
    data: List[Dict[str, Any]]
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class WorkflowResponse(BaseModel):
    query: str
    agents_used: List[AgentType]
    results: List[AgentResponse]
    summary: str
    total_results: int
    execution_time: float

class JiraIssue(BaseModel):
    key: str
    summary: str
    description: Optional[str]
    status: str
    assignee: Optional[str]
    created: str
    updated: str
    priority: Optional[str]
    issue_type: str

class GitHubItem(BaseModel):
    type: str  # repository, issue, pull_request, commit
    name: str
    url: str
    description: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    author: Optional[str]
    language: Optional[str]

class FileSystemItem(BaseModel):
    path: str
    name: str
    type: str  # file, directory
    size: Optional[int]
    modified: str
    content_preview: Optional[str]

class VideoItem(BaseModel):
    title: str
    url: str
    duration: Optional[str]
    description: Optional[str]
    thumbnail: Optional[str]
    upload_date: Optional[str]
    view_count: Optional[int]

class S3Object(BaseModel):
    key: str
    size: int
    last_modified: str
    storage_class: str
    etag: str
    content_type: Optional[str]

class URLContent(BaseModel):
    url: str
    title: Optional[str]
    content: str
    content_type: str
    status_code: int
    last_accessed: str
