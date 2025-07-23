# LlamaIndex Integration with Sensitive Data Evaluation

This directory contains the core utilities for integrating LlamaIndex with Arthur's sensitive data detection capabilities. The implementation has been simplified to focus solely on sensitive data evaluation while maintaining a clean, efficient architecture.

## Overview

The integration provides:

- **Sensitive Data Validation**: Validates prompts using Arthur's API before processing
- **Simple Chat Flow**: Clean LlamaIndex chat with automatic sensitive data checking
- **Type Safety**: Full TypeScript support with proper interfaces
- **Error Handling**: Graceful handling of validation failures and API errors
- **Configurable**: Easy to configure for different environments and use cases

## Architecture

### Core Components

1. **`LlamaIndexService`** - Main service class that handles chat and integrates sensitive data validation
2. **`SensitiveDataEvaluator`** - Dedicated class for sensitive data validation using Arthur's API
3. **`types.ts`** - TypeScript interfaces and type definitions
4. **`Chat.tsx`** - React component for the chat interface

## LlamaIndexService Class

The `LlamaIndexService` class encapsulates all LlamaIndex API calls with configurable parameters for OpenAI API key, Arthur API key, and LLM model. It now includes **sensitive data validation** capabilities.

### Features

- **Configurable**: Pass OpenAI API key, Arthur API key, and LLM model as constructor parameters
- **Type Safe**: Full TypeScript support with proper interfaces
- **Error Handling**: Comprehensive error handling for validation failures
- **Sensitive Data Validation**: Built-in prompt validation using Arthur API
- **Flexible**: Easy to extend and customize for different use cases

### Configuration

```typescript
interface LlamaIndexConfig {
  openaiApiKey: string;        // Required: Your OpenAI API key
  arthurApiKey: string;        // Required: Your Arthur API key
  llmModel?: string;           // Optional: LLM model (default: 'gpt-4o-mini')
  arthurBaseUrl?: string;      // Optional: Arthur base URL (default: 'http://localhost:3030')
}
```

### Basic Usage

```typescript
import { LlamaIndexService } from './LlamaIndex';

// Create service instance
const service = new LlamaIndexService({
  openaiApiKey: process.env.OPENAI_API_KEY!,
  arthurApiKey: process.env.ARTHUR_AUTH_KEY!,
  llmModel: 'gpt-4o-mini',
  arthurBaseUrl: 'http://localhost:3030'
});

// Use the service
const response = await service.chat({
  message: "Hello, how are you?",
  taskId: "task-123",
  conversationId: "conv-456",
  userId: "user-789"
});

console.log(response.message);
```

### API Methods

#### `chat(request: ChatRequest): Promise<ChatResponse>`

Main method to handle chat requests with sensitive data validation.

**Parameters:**
```typescript
interface ChatRequest {
  message: string;              // User's message
  taskId: string;              // Task identifier
  conversationId: string;       // Conversation identifier
  userId: string;              // User identifier
}
```

**Returns:**
```typescript
interface ChatResponse {
  message: string;              // Response message or error message
}
```

### Sensitive Data Validation Flow

1. **User sends message** → Chat.tsx
2. **API receives request** → `/api/chat`
3. **LlamaIndexService validates** → `SensitiveDataEvaluator.validatePrompt()` returns boolean
4. **If false** → Returns "Sensitive Data Evaluation has not passed"
5. **If true** → Proceeds with LlamaIndex chat and returns response
6. **Chat.tsx displays** → Simple message text

## SensitiveDataEvaluator Class

The `SensitiveDataEvaluator` is a dedicated class that integrates Arthur's sensitive data detection capabilities. It provides simple, focused validation for sensitive data in prompts.

### Features

- **Simple Validation**: Returns boolean result (true = valid, false = sensitive data detected)
- **Arthur API Integration**: Uses Arthur's `/api/v2/tasks/{taskId}/validate_prompt` endpoint
- **Configurable**: Supports custom task IDs, conversation IDs, and user IDs
- **Error Handling**: Graceful handling of API failures and network errors
- **Type Safety**: Full TypeScript support with proper interfaces

### Configuration

```typescript
interface SensitiveDataEvaluatorConfig {
  arthurApiKey: string;           // Required: Arthur API key
  arthurBaseUrl?: string;         // Optional: Arthur base URL (default: 'http://localhost:3030')
  taskId?: string;                // Optional: Task identifier for Arthur
  conversationId?: string;         // Optional: Conversation identifier for Arthur
  userId?: string;                // Optional: User identifier for Arthur
  enableDetailedFeedback?: boolean; // Optional: Enable detailed feedback (default: true)
}
```

### Basic Usage

```typescript
import { SensitiveDataEvaluator } from './SensitiveDataEvaluator';

// Create evaluator
const evaluator = new SensitiveDataEvaluator({
  arthurApiKey: process.env.ARTHUR_AUTH_KEY!,
  arthurBaseUrl: 'http://localhost:3030',
  taskId: 'my-task',
  conversationId: 'my-conversation',
  userId: 'my-user',
  enableDetailedFeedback: true
});

// Validate a prompt
const isValid = await evaluator.validatePrompt("What is my social security number?");

if (isValid) {
  console.log("Prompt is safe to process");
} else {
  console.log("Sensitive data detected - block the request");
}
```

### API Methods

#### `validatePrompt(prompt: string): Promise<boolean>`

Validates a prompt using Arthur's API for sensitive data detection.

**Parameters:**
- `prompt: string` - The prompt to validate

**Returns:**
- `Promise<boolean>` - `true` if prompt is valid, `false` if sensitive data detected

#### `updateConfig(newConfig: Partial<SensitiveDataEvaluatorConfig>): void`

Updates the evaluator configuration.

### Sensitive Data Detection Logic

The evaluator checks for the `ModelSensitiveDataRule` in Arthur's validation results:

```typescript
private detectSensitiveData(validationResult: SensitiveDataValidationResult): boolean {
  if (!validationResult.rule_results) {
    return false;
  }

  // Check for ModelSensitiveDataRule violations
  const sensitiveDataResult = this.findValidationResult(validationResult.rule_results, 'ModelSensitiveDataRule');
  if (sensitiveDataResult?.result.toLowerCase() === 'fail') {
    console.log('Sensitive Data violation detected:', sensitiveDataResult);
    return true;
  }

  return false;
}
```

### Validation Rules

The evaluator integrates with Arthur's validation rules:

- **ModelSensitiveDataRule**: Detects sensitive data patterns in prompts
- **Configurable**: Additional rules can be added through Arthur's API configuration

## Chat Component

The `Chat.tsx` component provides a clean, simple chat interface that integrates with the LlamaIndex service.

### Features

- **Simple Interface**: Clean chat UI without evaluation complexity
- **Real-time Messaging**: Instant message display and loading states
- **Error Handling**: Graceful error display for failed requests
- **Responsive Design**: Works on desktop and mobile devices

### Usage

```typescript
import Chat from './components/Chat';

// Basic usage
<Chat />

// With callbacks
<Chat 
  onBeforeSend={async (data) => {
    console.log('Sending message:', data);
  }}
  onAfterReceive={async (response) => {
    console.log('Received response:', response);
    return response;
  }}
/>
```

## API Integration

### Chat API Route (`/api/chat`)

The API route provides a simple interface for chat requests:

```typescript
// Request
POST /api/chat
{
  "message": "Hello, how are you?",
  "taskId": "task-123",
  "conversationId": "conv-456",
  "userId": "user-789"
}

// Response
{
  "response": {
    "message": "Hello! I'm doing well, thank you for asking."
  }
}

// Error Response (Sensitive Data)
{
  "response": {
    "message": "Sensitive Data Evaluation has not passed"
  }
}
```

## Error Handling

The implementation handles various error scenarios:

- **Missing Parameters**: Returns "Missing required parameters"
- **Sensitive Data Detected**: Returns "Sensitive Data Evaluation has not passed"
- **API Errors**: Returns "An error occurred while processing your request"
- **Network Errors**: Graceful fallback with user-friendly messages

## Examples

### Example 1: Basic Service Usage

```typescript
import { LlamaIndexService } from './LlamaIndex';

const service = new LlamaIndexService({
  openaiApiKey: process.env.OPENAI_API_KEY!,
  arthurApiKey: process.env.ARTHUR_AUTH_KEY!
});

const response = await service.chat({
  message: "What is the weather like?",
  taskId: "weather-task",
  conversationId: "weather-conv",
  userId: "user-123"
});

console.log(response.message);
```

### Example 2: Standalone Sensitive Data Validation

```typescript
import { SensitiveDataEvaluator } from './SensitiveDataEvaluator';

const evaluator = new SensitiveDataEvaluator({
  arthurApiKey: process.env.ARTHUR_AUTH_KEY!,
  taskId: 'validation-task'
});

// Safe prompt
const safeResult = await evaluator.validatePrompt("What is the weather like?");
console.log(safeResult); // true

// Sensitive prompt
const sensitiveResult = await evaluator.validatePrompt("What is my SSN?");
console.log(sensitiveResult); // false
```

### Example 3: Error Handling

```typescript
try {
  const response = await service.chat({
    message: "What is my personal information?",
    taskId: "task-123",
    conversationId: "conv-456",
    userId: "user-789"
  });

  if (response.message.includes("Sensitive Data Evaluation has not passed")) {
    console.log("Request was blocked due to sensitive data");
  } else {
    console.log("Response:", response.message);
  }
} catch (error) {
  console.error("Chat error:", error);
}
```

## Migration from Enhanced Implementation

The codebase has been simplified from the previous enhanced implementation:

### Removed Components
- ❌ `EnhancedLlamaIndexService`
- ❌ `EnhancedChat` component
- ❌ `/api/chat-enhanced` route
- ❌ All evaluation types (correctness, faithfulness, relevancy)
- ❌ Complex evaluation display UI
- ❌ Response validation logic

### Simplified Flow
- ✅ **Before**: Complex validation objects with `isValid`, `blocked`, `reason`, `details`
- ✅ **After**: Simple boolean validation with clear pass/fail logic

- ✅ **Before**: Multiple evaluation types and complex UI
- ✅ **After**: Only sensitive data validation with simple message display

## Benefits

1. **Simplicity**: Clean, focused implementation with minimal complexity
2. **Performance**: Faster execution with fewer API calls
3. **Maintainability**: Easier to understand and modify
4. **Type Safety**: Full TypeScript support prevents runtime errors
5. **Security**: Robust sensitive data validation using Arthur's API
6. **User Experience**: Simple, intuitive chat interface
7. **Cost Effective**: Reduced API usage and processing overhead

## Best Practices

### Configuration
1. **Use Environment Variables**: Store API keys securely
2. **Set Appropriate Base URLs**: Use correct Arthur API endpoints
3. **Configure Task IDs**: For proper tracking and analytics
4. **Enable Detailed Feedback**: For better debugging and monitoring

### Usage
1. **Always Handle Errors**: Wrap service calls in try-catch blocks
2. **Validate Inputs**: Check for required parameters before processing
3. **Monitor Sensitive Data**: Track validation results in production
4. **Update Configurations**: Dynamically update configs as needed

### Integration
1. **Start Simple**: Use the basic service first
2. **Test Validation**: Verify sensitive data detection works correctly
3. **Monitor Performance**: Track API usage and response times
4. **Handle Failures**: Implement fallback mechanisms for API failures

## Contributing

This implementation demonstrates a clean, focused approach to integrating LlamaIndex with sensitive data validation. The code is designed to be:

- **Readable**: Clear, well-documented code
- **Maintainable**: Simple architecture with clear separation of concerns
- **Extensible**: Easy to add new features or modify existing ones
- **Testable**: Well-structured for unit and integration testing

The simplified approach makes it easier to understand, maintain, and extend the functionality while providing robust sensitive data protection. 