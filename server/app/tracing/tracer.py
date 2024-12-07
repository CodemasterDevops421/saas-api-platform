from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

class TracingManager:
    def __init__(self):
        jaeger_exporter = JaegerExporter(
            agent_host_name="jaeger",
            agent_port=6831,
        )
        trace.set_tracer_provider(TracerProvider())
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        self.tracer = trace.get_tracer(__name__)

    def instrument_app(self, app):
        FastAPIInstrumentor.instrument_app(app)
        SQLAlchemyInstrumentor().instrument()
        RedisInstrumentor().instrument()

    def create_span(self, name: str, **attributes):
        return self.tracer.start_as_current_span(
            name, attributes=attributes
        )