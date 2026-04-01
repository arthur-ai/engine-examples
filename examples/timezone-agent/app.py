"""
Simple OpenInference Tracing Tutorial with LangChain

This tutorial shows how to:
1. Set up OpenInference tracing with Arthur
2. Instrument a LangChain agent
3. Inject Arthur task metadata via TracerProvider Resource
4. Use timezone conversion tools
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Import our timezone tools from the combined module
from timezone_tools import get_current_time, convert_time_between_zones
from validate_env import validate_environment

# Load environment variables
load_dotenv()

def setup_tracing():
    """Set up OpenInference tracing with Arthur endpoint."""
    
    # 1. Set up OpenTelemetry with Arthur task metadata in Resource
    arthur_task_id = os.getenv("ARTHUR_TASK_ID")
    if not arthur_task_id:
        raise ValueError("ARTHUR_TASK_ID must be set in .env file")
    
    # Create resource with Arthur task metadata
    resource = Resource.create({
        "arthur.task": arthur_task_id,
        "service.name": "multiagent-playground-tutorial"
    })
    
    tracer_provider = trace_sdk.TracerProvider(resource=resource)
    trace_api.set_tracer_provider(tracer_provider)
    
    # 2. Configure OTLP exporter to send to Arthur
    arthur_base_url = os.getenv("ARTHUR_BASE_URL")
    bearer_token = os.getenv("ARTHUR_API_KEY")
    
    if not arthur_base_url or not bearer_token:
        raise ValueError("ARTHUR_BASE_URL and ARTHUR_API_KEY must be set in .env file")
    
    # Create OTLP exporter pointing to Arthur
    otlp_endpoint = f"{arthur_base_url}/v1/traces"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    
    otlp_exporter = OTLPSpanExporter(
        endpoint=otlp_endpoint,
        headers=headers
    )
    
    # 3. Add span processor to send spans to Arthur
    tracer_provider.add_span_processor(
        SimpleSpanProcessor(otlp_exporter)
    )
    
    # 4. Instrument LangChain
    LangChainInstrumentor().instrument()
    
    print(f"✅ Tracing set up successfully")
    print(f"   Endpoint: {otlp_endpoint}")
    print(f"   Task ID: {arthur_task_id}")

def create_simple_agent():
    """Create a LangChain agent with timezone tools."""
    
    # Initialize the model
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create tools list
    tools = [get_current_time, convert_time_between_zones]
    
    # Create a proper prompt template with system and user messages
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant with timezone conversion capabilities. 

You can:
1. Get the current time in any timezone or city using the get_current_time tool
2. Convert times between different timezones using the convert_time_between_zones tool

When users ask about times, use the appropriate tool to provide accurate information.
For example:
- "What time is it in Zurich?" -> use get_current_time
- "What is 10pm EDT in California?" -> use convert_time_between_zones

Always provide clear, helpful responses with the time information. Be conversational and helpful."""),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    
    # Create the agent with tools
    agent = create_openai_tools_agent(
        llm=model,
        tools=tools,
        prompt=prompt
    )
    
    # Create the executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )
    
    return agent_executor

def chat_with_agent(agent_executor, message: str):
    """Chat with the agent - Arthur task metadata is now embedded in TracerProvider Resource."""
    
    # Run the agent (Arthur task metadata is automatically included via Resource)
    result = agent_executor.invoke({
        "input": message
    })
    
    return result["output"]

def main():
    """Main function to run the tutorial."""
    
    print("🚀 OpenInference Tracing Tutorial")
    print("=" * 40)
    print("This agent helps you convert times between different timezones and cities.")
    print("All interactions are traced to Arthur for monitoring and analysis.")
    print()
    print("💡 Examples: 'What time is it in Tokyo?' or 'What is 3pm EST in London?'")
    print()
    
    try:
        # Validate environment first
        if not validate_environment():
            print("❌ Environment validation failed. Please check your .env file.")
            return
        
        # Set up tracing and create agent
        setup_tracing()
        agent = create_simple_agent()
        
        print("✅ Agent ready! Start chatting (type 'quit' to exit):")
        print("-" * 40)
        
        while True:
            user_input = input("\nYou: ")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            try:
                # Get response from agent with tracing
                response = chat_with_agent(agent, user_input)
                print(f"Assistant: {response}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("\nMake sure your .env file is configured correctly!")

if __name__ == "__main__":
    main()
