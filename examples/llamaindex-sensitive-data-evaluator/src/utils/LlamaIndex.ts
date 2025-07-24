import { OpenAI } from '@llamaindex/openai';
import { SensitiveDataEvaluator } from './SensitiveDataEvaluator';
import {
  LlamaIndexConfig,
  ChatRequest,
  ChatResponse,
  SensitiveDataEvaluatorConfig
} from './types';

export class LlamaIndexService {
  private config: LlamaIndexConfig;
  private chatEngine: { chat: (params: { message: string }) => Promise<{ message: string }> } | null = null;
  private sensitiveDataEvaluator?: SensitiveDataEvaluator;
  private useSensitiveDataEvaluator: boolean;

  constructor(config: LlamaIndexConfig, useSensitiveDataEvaluator: boolean = true) {
    this.config = {
      llmModel: 'gpt-4o-mini',
      arthurBaseUrl: 'http://localhost:3030',
      ...config
    };

    this.useSensitiveDataEvaluator = useSensitiveDataEvaluator;

    if (useSensitiveDataEvaluator) {
      this.initializeSensitiveDataEvaluator();
    }
  }

  private initializeSensitiveDataEvaluator() {
    if (!this.config.arthurApiKey) return;

    try {
      const sensitiveDataConfig: SensitiveDataEvaluatorConfig = {
        arthurApiKey: this.config.arthurApiKey,
        arthurBaseUrl: this.config.arthurBaseUrl,
        taskId: 'llamaindex-chat-task',
        conversationId: 'llamaindex-chat-conversation',
        userId: 'llamaindex-chat-user',
        enableDetailedFeedback: true
      };
      
      this.sensitiveDataEvaluator = new SensitiveDataEvaluator(sensitiveDataConfig);
    } catch {
      // Failed to initialize sensitive data evaluator
    }
  }

  private async getChatEngine() {
    if (!this.chatEngine) {
      try {
        const llm = new OpenAI({ 
          apiKey: this.config.openaiApiKey,
          model: this.config.llmModel
        });
        
        // Create a simple chat engine without any documents
        this.chatEngine = {
          async chat({ message }: { message: string }) {
            const response = await llm.chat({
              messages: [{ role: 'user', content: message }]
            });
            const content = typeof response.message.content === 'string' 
              ? response.message.content 
              : JSON.stringify(response.message.content);
            return { message: content };
          }
        };
      } catch (error) {
        throw error;
      }
    }
    return this.chatEngine;
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    try {
      // Validate incoming message using SensitiveDataEvaluator
      if (this.useSensitiveDataEvaluator && this.sensitiveDataEvaluator) {
        // Update evaluator config with current request context
        this.sensitiveDataEvaluator.updateConfig({
          taskId: request.taskId,
          conversationId: request.conversationId,
          userId: request.userId
        });

        const isValid = await this.sensitiveDataEvaluator.validatePrompt(request.message);
        
        if (!isValid) {
          return { 
            message: "Sensitive Data Evaluation has not passed"
          };
        }
      }

      // Get chat response from LlamaIndex
      const engine = await this.getChatEngine();
      const chatResponse = await engine?.chat({ message: request.message });

      if (!chatResponse?.message) {
        return { message: 'Failed to generate response from LLM.' };
      }

      return { 
        message: chatResponse.message
      };
    } catch {
      return { message: 'An error occurred while processing your request.' };
    }
  }
}
