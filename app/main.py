from fastapi import FastAPI, Depends, HTTPException
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Template

Base.metadata.create_all(bind=engine)

app = FastAPI()

resource = Resource(attributes={
    SERVICE_NAME: "templates-service"
})

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(jaeger_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

SQLAlchemyInstrumentor().instrument()

FastAPIInstrumentor.instrument_app(app)

Instrumentator().instrument(app).expose(app)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class TemplateObj(BaseModel):
    title: str
    content: str


@app.post("/templates/")
async def create_template(doc: TemplateObj, db: Session = Depends(get_db)):
    template = Template(title=doc.title, content=doc.content)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@app.get("/templates/{template_id}")
async def read_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if template:
        return template
    raise HTTPException(status_code=404, detail="Template not found")


@app.get("/templates/")
async def read_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    templates = db.query(Template).offset(skip).limit(limit).all()
    return templates


@app.get("/__health")
async def check_health():
    return
