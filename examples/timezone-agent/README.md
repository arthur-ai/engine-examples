# Timezone Agent with OpenInference Tracing

A simple tutorial demonstrating how to set up OpenInference tracing with a LangChain agent and send traces to Arthur. This tutorial includes timezone conversion tools to demonstrate tool usage.

## What This Tutorial Covers

1. **Setting up OpenInference tracing** with Arthur endpoint
2. **Instrumenting a LangChain agent** with OpenInference
3. **Injecting Arthur task metadata** into traces
4. **Running a chat agent with timezone tools** that sends traces to Arthur

## Prerequisites

- Python 3.12+
- An [Arthur account](https://platform.arthur.ai/signup?utm_source=github&utm_medium=readme) with API access
- An [OpenAI API key](https://platform.openai.com/settings/organization/api-keys)
- A pre-created Arthur task (you should have the task ID ready)

## Setup

### 1. Install Dependencies

```bash
# From the multiagent-playground root directory
pip install -e .
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cd tutorial
cp env.example .env
```

Edit `.env` with your actual values:

```bash
# Arthur Configuration
ARTHUR_BASE_URL=https://app.arthur.ai  # or your self-hosted instance
ARTHUR_API_KEY=your_arthur_api_key_here
ARTHUR_TASK_ID=your_task_id_here # ensure that your task is marked as agentic: `is_agentic=True`

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Tutorial

```bash
python app.py
```

## Available Tools

The agent comes with two timezone-related tools:

### 1. Current Time Tool
Get the current time in any timezone or city.

**Examples:**
- "What is the time in Zurich right now?"
- "What time is it in California?"
- "Current time in EST"

### 2. Timezone Conversion Tool
Convert times between different timezones.

**Examples:**
- "What is 10pm EDT in California?"
- "Convert 2:30pm EST to Tokyo time"
- "What time is 9am in London when it's 3pm in New York?"

## Supported Timezones and Cities

The tools support a wide range of timezones and cities:

**US Timezones:** EST, EDT, CST, CDT, MST, MDT, PST, PDT
**US Cities/States:** California, New York, Chicago, Denver, etc.

**International Cities:** Zurich, London, Paris, Tokyo, Beijing, Sydney, etc.
**Countries:** Japan, Germany, France, Australia, Brazil, etc.

**Common Abbreviations:** UTC, GMT, JST, IST, CET, BST, etc.

## File Structure

```
tutorial/
├── app.py                    # Main application with agent setup
├── timezone_tools.py         # Timezone functions and LangChain tools
├── timezone_shortcuts.json   # Timezone shortcuts and mappings
├── requirements.txt          # Python dependencies
├── env.example              # Environment variables template
└── README.md                # This file
```

## How It Works

### 1. Setting Up Tracing

The tutorial sets up OpenTelemetry tracing and configures an OTLP exporter to send spans to Arthur. The LangChain agent is instrumented to automatically create spans for all interactions.

```python
def setup_tracing():
    # 1. Set up OpenTelemetry
    tracer_provider = trace_sdk.TracerProvider()
    trace_api.set_tracer_provider(tracer_provider)
    
    # 2. Configure OTLP exporter to send to Arthur
    arthur_base_url = os.getenv("ARTHUR_BASE_URL")
    bearer_token = os.getenv("ARTHUR_API_KEY")
    
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
```

### 2. Creating Tools

The tools are defined in `timezone_tools.py` using LangChain's `@tool` decorator:

```python
@tool
def get_current_time(timezone: str) -> str:
    """Get the current time in a specific timezone or city."""
    return current_time(timezone)

@tool
def convert_time_between_zones(time_str: str, from_timezone: str, to_timezone: str) -> str:
    """Convert a time from one timezone to another."""
    return convert_timezone(time_str, from_timezone, to_timezone)
```

### 3. Arthur Integration

The agent injects Arthur task metadata into all traces, allowing you to view and analyze the interactions in your Arthur dashboard.

### 4. Injecting Arthur Task Metadata

Arthur task metadata is automatically injected via the TracerProvider Resource during setup:

```python
def setup_tracing():
    # Create resource with Arthur task metadata
    arthur_task_id = os.getenv("ARTHUR_TASK_ID")
    resource = Resource.create({
        "arthur.task": arthur_task_id,
        "service.name": "multiagent-playground-tutorial"
    })
    
    tracer_provider = trace_sdk.TracerProvider(resource=resource)
    trace_api.set_tracer_provider(tracer_provider)
    # ... rest of setup
```

## Key Concepts

### OpenInference Instrumentation

- **LangChainInstrumentor**: Automatically instruments LangChain components to create spans
- **Resource**: Embeds metadata (like Arthur task ID) into all traces automatically
- **OTLPSpanExporter**: Sends spans to Arthur via OTLP protocol

### Arthur Integration

- **Task ID**: Links all traces to a specific Arthur task
- **Metadata**: Allows you to categorize and filter traces in Arthur
- **Real-time**: Spans are sent to Arthur as they're created

### Tool Usage

- **Tool Calls**: Each tool invocation creates a separate span in Arthur
- **Input/Output**: Tool inputs and outputs are captured in the traces
- **Error Handling**: Tool errors are also captured and visible in Arthur

## What You'll See

1. **Console Output**: The agent will respond to your questions and use tools when needed
2. **Arthur Dashboard**: Traces will appear in your Arthur task with:
   - LLM calls and responses
   - Tool invocations (timezone conversions)
   - Agent execution steps
   - Timing information

## Example Conversations

```
You: What time is it in Zurich right now?
Assistant: Let me check the current time in Zurich for you.
[Tool: get_current_time]
[Tool Result: 2024-12-19 15:30:45 ZURICH]
The current time in Zurich is 2024-12-19 15:30:45 ZURICH.

You: What is 10pm EDT in California?
Assistant: I'll convert 10pm EDT to California time for you.
[Tool: convert_time_between_zones]
[Tool Result: 2024-12-19 19:00:00 CALIFORNIA]
10pm EDT is 7:00 PM in California (PST).
```

## Troubleshooting

### Common Issues

1. **"ARTHUR_BASE_URL and ARTHUR_API_KEY must be set"**
   - Make sure your `.env` file exists and has the correct values

2. **"ARTHUR_TASK_ID must be set"**
   - Ensure you have created a task in Arthur and copied the task ID

3. **Connection errors**
   - Check that your Arthur URL is correct
   - Verify your API key is valid
   - Ensure network connectivity

4. **Tool errors**
   - Check that the timezone names are valid
   - Ensure time formats are correct (e.g., "10pm", "14:30")

## Next Steps

After running this tutorial, you can:

1. **Add more tools** to your agent and see how they appear in traces
2. **Customize metadata** to include additional context
3. **Scale up** to more complex agent architectures
4. **Analyze traces** in the Arthur dashboard for performance insights

## Resources

- [OpenInference Documentation](https://openinference.io/)
- [Arthur Documentation](https://docs.arthur.ai/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/) 