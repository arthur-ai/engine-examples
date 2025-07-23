# LlamaIndex Integration Example with Sensitive Data Evaluation

This project demonstrates the integration of LlamaIndex with Arthur AI's sensitive data evaluation system. It provides a secure chat interface that validates user inputs for sensitive information before processing them through an LLM.

## Features

- **Sensitive Data Evaluation**: Validates user prompts using Arthur AI's sensitive data detection rules
- **LlamaIndex Integration**: Seamless integration with LlamaIndex for LLM-powered chat
- **Real-time Chat Interface**: Modern React-based chat UI with real-time message handling
- **Configurable Security**: Flexible configuration for sensitive data evaluation parameters

## Architecture

### SensitiveDataEvaluator

The `SensitiveDataEvaluator` class is the core component responsible for validating user inputs against sensitive data detection rules. It integrates with Arthur AI's API to perform real-time validation.

**Key Features:**
- Validates prompts against Arthur AI's sensitive data detection rules
- Configurable validation parameters (task ID, conversation ID, user ID)
- Automatic detection of sensitive data violations
- Graceful error handling

**Usage Example:**
```typescript
import { SensitiveDataEvaluator } from './utils/SensitiveDataEvaluator';

const evaluator = new SensitiveDataEvaluator({
  arthurApiKey: 'your-arthur-api-key',
  arthurBaseUrl: 'http://localhost:3030',
  taskId: 'your-task-id',
  conversationId: 'conversation-id',
  userId: 'user-id',
  enableDetailedFeedback: true
});

const isValid = await evaluator.validatePrompt(userMessage);
if (!isValid) {
  // Handle sensitive data detection
  return "Sensitive data detected in your message";
}
```

### LlamaIndexService

The `LlamaIndexService` class provides a secure wrapper around LlamaIndex functionality, integrating sensitive data evaluation before processing user requests.

**Key Features:**
- Automatic sensitive data validation before LLM processing
- Configurable LLM models (default: GPT-4o-mini)
- Integrated error handling and response management
- Support for conversation context tracking

**Usage Example:**
```typescript
import { LlamaIndexService } from './utils/LlamaIndex';

const service = new LlamaIndexService({
  openaiApiKey: 'your-openai-api-key',
  arthurApiKey: 'your-arthur-api-key',
  llmModel: 'gpt-4o-mini',
  arthurBaseUrl: 'http://localhost:3030'
}, true); // Enable sensitive data evaluation

const response = await service.chat({
  message: userMessage,
  taskId: 'task-id',
  conversationId: 'conversation-id',
  userId: 'user-id'
});
```

## Setup

### Prerequisites

- Node.js 18+ 
- Arthur AI account and API key
- OpenAI API key

### Environment Variables

Create a `.env.local` file with the following variables:

```env
OPENAI_API_KEY=your-openai-api-key
ARTHUR_AUTH_KEY=your-arthur-api-key
MODEL=gpt-4o-mini
LLM_MAX_TOKENS=4096
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
```

### Installation

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to access the chat interface.

## API Endpoints

### POST /api/chat

Handles chat requests with sensitive data validation.

**Request Body:**
```json
{
  "message": "User message",
  "taskId": "task-identifier",
  "conversationId": "conversation-identifier", 
  "userId": "user-identifier"
}
```

**Response:**
```json
{
  "response": {
    "message": "LLM response or error message"
  }
}
```

## Security Features

1. **Pre-processing Validation**: All user messages are validated for sensitive data before being sent to the LLM
2. **Configurable Rules**: Sensitive data detection rules can be configured through Arthur AI
3. **Context Tracking**: Each request includes task, conversation, and user context for better security monitoring
4. **Graceful Degradation**: System continues to function even if sensitive data evaluation fails

## Project Structure

```
src/
├── app/
│   ├── api/chat/route.ts          # Chat API endpoint
│   ├── settings.ts                # LlamaIndex configuration
│   └── page.tsx                   # Main chat interface
├── components/
│   └── Chat.tsx                   # Chat component
├── utils/
│   ├── SensitiveDataEvaluator.ts  # Sensitive data validation
│   ├── LlamaIndex.ts              # LlamaIndex service wrapper
│   └── types.ts                   # TypeScript type definitions
└── constants/
    └── mockUser.ts                # Mock user data
```

## Technologies Used

- **Next.js 14**: React framework with App Router
- **LlamaIndex**: LLM framework for document processing and chat
- **Arthur AI**: Sensitive data detection and validation
- **OpenAI**: LLM provider (GPT-4o-mini)
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Styling and UI components

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
