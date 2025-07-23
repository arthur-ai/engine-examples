// SensitiveDataEvaluator Types
export interface SensitiveDataEvaluatorConfig {
  arthurApiKey: string;
  arthurBaseUrl?: string;
  taskId?: string;
  conversationId?: string;
  userId?: string;
  enableDetailedFeedback?: boolean;
}

export interface SensitiveDataValidationResult {
  inference_id?: string;
  rule_results?: Array<{
    rule_type: string;
    result: string;
    details?: string;
  }>;
}

// Chat Types
export interface ChatRequest {
  message: string;
  taskId: string;
  conversationId: string;
  userId: string;
}

export interface ChatResponse {
  message: string;
}

// LlamaIndex Service Types
export interface LlamaIndexConfig {
  openaiApiKey: string;
  arthurApiKey: string;
  llmModel?: string;
  arthurBaseUrl?: string;
} 