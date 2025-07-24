import { NextRequest, NextResponse } from 'next/server';
import { initSettings } from '../../settings';
import { LlamaIndexService } from '../../../utils/LlamaIndex';

try {
  initSettings();
} catch {
  // Settings initialization failed
}

const llamaIndexService = new LlamaIndexService({
  openaiApiKey: process.env.OPENAI_API_KEY!,
  arthurApiKey: process.env.ARTHUR_AUTH_KEY!,
  llmModel: process.env.MODEL || 'gpt-4o-mini',
  arthurBaseUrl: 'http://localhost:3030',
});

export async function POST(req: NextRequest) {
  try {
    const { message, taskId, conversationId, userId } = await req.json();
    

    if (!message || !taskId || !conversationId || !userId) {
      return NextResponse.json({ 
        response: { 
          message: "Missing required parameters" 
        } 
      }, { status: 200 });
    }

    const response_data = await llamaIndexService.chat({
      message,
      taskId,
      conversationId,
      userId
    });

    return NextResponse.json({ 
      response: { 
        message: response_data.message
      } 
    }, { status: 200 });
  } catch {
    return NextResponse.json({ 
      response: { 
        message: "An error occurred while processing your request."
      } 
    }, { status: 200 });
  }
} 