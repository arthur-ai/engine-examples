import {
  SensitiveDataEvaluatorConfig,
  SensitiveDataValidationResult
} from './types';

export class SensitiveDataEvaluator {
  private config: SensitiveDataEvaluatorConfig;

  constructor(config: SensitiveDataEvaluatorConfig) {
    this.config = {
      arthurBaseUrl: 'http://localhost:3030',
      enableDetailedFeedback: true,
      ...config
    };
  }

  private findValidationResult(
    ruleResults: Array<{ rule_type: string; result: string; details?: string }>, 
    ruleName: string
  ) {
    return ruleResults.find(rule => rule.rule_type === ruleName);
  }

  private detectSensitiveData(validationResult: SensitiveDataValidationResult): boolean {
    if (!validationResult.rule_results) {
      return false;
    }
    const sensitiveDataRule = this.findValidationResult(validationResult.rule_results, 'ModelSensitiveDataRule');
    if (sensitiveDataRule?.result.toLowerCase() === 'fail') {
      return true;
    }
    return false;
  }

  updateConfig(newConfig: Partial<SensitiveDataEvaluatorConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }


  async validatePrompt(prompt: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.arthurBaseUrl}/api/v2/tasks/${this.config.taskId}/validate_prompt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.arthurApiKey}`
        },
        body: JSON.stringify({
          prompt: prompt,
          task_id: this.config.taskId || 'default-task',
          conversation_id: this.config.conversationId || 'default-conversation',
          user_id: this.config.userId || 'default-user'
        })
      });

      if (!response.ok) {
        return false;
      }

      const validationResult: SensitiveDataValidationResult = await response.json();

      const hasSensitiveData = this.detectSensitiveData(validationResult);
      return !hasSensitiveData;

    } catch (error) {
      console.error('SensitiveDataEvaluator validation error:', error);
      return false;
    }
  }
} 