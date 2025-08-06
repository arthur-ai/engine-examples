from dotenv import load_dotenv
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor, ReadableSpan
from opentelemetry.trace import Span

from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

import os
import json

# Load environment variables from .env file
load_dotenv()
TASK_ID = os.getenv("TASK_ID")

class MetadataInjectorSpanProcessor(SpanProcessor):
    def __init__(self, task_id: str):
        self.task_id = task_id

    def on_start(self, span: Span, parent_context):
        # Check if 'metadata' is already present
        metadata_raw = span.attributes.get("metadata")
        if metadata_raw:
            try:
                # Parse the JSON string
                metadata_dict = json.loads(metadata_raw)
            except Exception:
                metadata_dict = {}
        else:
            metadata_dict = {}

        # Inject task_id
        metadata_dict["arthur.task"] = self.task_id

        # Write it back as a JSON string
        span.set_attribute("metadata", json.dumps(metadata_dict))

    def on_end(self, span: ReadableSpan):
        pass

# Set up the OpenTelemetry SDK tracer provider with an HTTP exporter.
# Change the endpoint if the collector is running at a different location.
otlp_span_exporter = OTLPSpanExporter(
    endpoint = "http://localhost:3030/v1/traces",
    headers = {
        "Authorization": f"Bearer {os.getenv('ARTHUR_ENGINE_API_KEY')}"
    }
)

# otlp_file_exporter = OTLPSpanExporter(
#     endpoint = "http://localhost:4318/v1/traces",
# )

trace_provider = TracerProvider()
trace_provider.add_span_processor(SimpleSpanProcessor(otlp_span_exporter))
# trace_provider.add_span_processor(SimpleSpanProcessor(otlp_file_exporter))
trace_provider.add_span_processor(MetadataInjectorSpanProcessor(TASK_ID))

# Call the instrumentor to instrument LangChain
LangChainInstrumentor().instrument(tracer_provider=trace_provider)