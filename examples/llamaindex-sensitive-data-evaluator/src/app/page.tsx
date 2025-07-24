import Chat from '../components/Chat'

export type CheckRulesBeforeSendResponseType = ({taskId, message, conversationId, userId}: {taskId: string, message: string, conversationId?: string, userId?: string}) => Promise<{message:string, inferenceId?:string}>

export default function Home() {
  return (
    <div className="grid grid-rows-[1fr] items-center justify-items-center min-h-screen max-h-screen p-8 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-[32px] items-center sm:items-start w-full">
        <div className="text-center mb-4 mx-auto">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">LlamaIndex Chat</h1>
          <p className="text-gray-600 text-sm">
            Start a conversation with LlamaIndex
          </p>
        </div>

        <Chat /> 
      </main>
      
    </div>
  );
}
