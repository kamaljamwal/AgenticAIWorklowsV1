export interface SearchRequest {
  prompt: string;
  max_results: number;
}

export interface AgentResponse {
  agent_type: string;
  success: boolean;
  data: any[];
  error?: string;
}

export interface SearchResponse {
  query: string;
  agents_used: string[];
  results: AgentResponse[];
  summary: string;
  total_results: number;
  execution_time: number;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  searchResponse?: SearchResponse;
  isLoading?: boolean;
}

export interface FilePreview {
  file_info: {
    name: string;
    path: string;
    size: number;
    modified: number;
  };
  content: string;
}
