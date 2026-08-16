export interface SourceDocument {
  file_name: string;
  candidate_name: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sourceDocuments?: SourceDocument[];
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  response: string;
  source_documents: SourceDocument[];
}

export interface ApiError {
  detail: string;
}
