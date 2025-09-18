"""
Power BI Integration Agent API
- FastAPI app with CORS, API-key auth, and all required endpoints
"""
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Any
import logging
import os
import re
from services.nl2sql import nl2sql_with_guardrails
from services.db import safe_execute_select
from services.exporter import export_df

API_KEY = os.getenv("API_KEY", "demo-key")
OUTPUTS_DIR = "outputs"

app = FastAPI(title="Power BI Integration Agent")

# Enable CORS for Power BI Desktop
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple API-key header auth
def get_api_key(request: Request):
    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key

class NL2SQLRequest(BaseModel):
    question: str = Field(..., example="Show monthly failures by machine")

class NL2SQLResponse(BaseModel):
    sql: str
    rationale: str
    viz_hints: List[str]

class QueryRequest(BaseModel):
    sql: str

class QueryResponse(BaseModel):
    rows: List[Any]
    columns: List[str]

class PowerBIQueryRequest(BaseModel):
    question: str

class PowerBIQueryResponse(BaseModel):
    sql: str
    rationale: str
    viz_hints: List[str]
    rows: List[Any]
    columns: List[str]

class ExportRequest(BaseModel):
    question: str
    format: str = Field(..., regex="^(csv|parquet|xlsx)$")

class ExportResponse(BaseModel):
    path: str
    rowcount: int

class RefreshRequest(BaseModel):
    export_id: str

class RefreshResponse(BaseModel):
    path: str
    rowcount: int

@app.post("/nl2sql", response_model=NL2SQLResponse, tags=["nl2sql"])
def nl2sql_endpoint(req: NL2SQLRequest, api_key: str = Depends(get_api_key)):
    """Translate NL question to SQL with guardrails."""
    result = nl2sql_with_guardrails(req.question)
    return result

@app.post("/query", response_model=QueryResponse, tags=["query"])
def query_endpoint(req: QueryRequest, api_key: str = Depends(get_api_key)):
    """Execute SELECT-only SQL and return rows."""
    df = safe_execute_select(req.sql)
    return {"rows": df.to_dict(orient="records"), "columns": list(df.columns)}

@app.post("/powerbi/query", response_model=PowerBIQueryResponse, tags=["powerbi"])
def powerbi_query_endpoint(req: PowerBIQueryRequest, api_key: str = Depends(get_api_key)):
    """Power BI DirectQuery: NL→SQL→Query→rows."""
    nl2sql_result = nl2sql_with_guardrails(req.question)
    df = safe_execute_select(nl2sql_result["sql"])
    return {
        "sql": nl2sql_result["sql"],
        "rationale": nl2sql_result["rationale"],
        "viz_hints": nl2sql_result["viz_hints"],
        "rows": df.to_dict(orient="records"),
        "columns": list(df.columns)
    }

@app.post("/export", response_model=ExportResponse, tags=["export"])
def export_endpoint(req: ExportRequest, api_key: str = Depends(get_api_key)):
    """Export NL→SQL results to file."""
    nl2sql_result = nl2sql_with_guardrails(req.question)
    df = safe_execute_select(nl2sql_result["sql"])
    slug = re.sub(r"[^a-z0-9_]+", "_", req.question.lower())[:32]
    out_path = os.path.join(OUTPUTS_DIR, f"{slug}.{req.format}")
    export_df(df, out_path, req.format)
    return {"path": out_path, "rowcount": len(df)}

@app.post("/refresh", response_model=RefreshResponse, tags=["refresh"])
def refresh_endpoint(req: RefreshRequest, api_key: str = Depends(get_api_key)):
    """Re-run a saved export job by id/name."""
    # For demo, just re-export the file (real implementation would track jobs)
    # TODO: Implement job tracking and lookup
    raise HTTPException(status_code=501, detail="Not implemented")

# Add logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger = logging.getLogger("uvicorn.access")
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response
