# app.py
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from scripts import safe_query
import pandas as pd

app = FastAPI(
    title="FCLM NL→SQL API",
    description="Ask questions in natural language and get DuckDB results. Powered by FastAPI and Anthropic Claude.",
    version="1.0.0",
    contact={
        "name": "FCLM Analytics Team",
        "email": "support@fclm.com"
    }
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    explanation: str
    sql: str
    results: list
    columns: list

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return """
    <html>
        <head>
            <title>FCLM NL→SQL API</title>
            <style>
                body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6fa; color: #222; margin: 0; }
                .container { max-width: 700px; margin: 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 12px #0001; padding: 32px; }
                h1 { color: #3b82f6; }
                .desc { color: #555; margin-bottom: 24px; }
                .button { background: #3b82f6; color: #fff; padding: 12px 24px; border: none; border-radius: 6px; font-size: 1.1em; cursor: pointer; text-decoration: none; }
                .button:hover { background: #2563eb; }
                .footer { margin-top: 32px; color: #888; font-size: 0.95em; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>FCLM NL→SQL API</h1>
                <div class="desc">
                    <p>Welcome! This API lets you ask questions in plain English and get live answers from your DuckDB database using advanced AI.</p>
                    <ul>
                        <li>Try the <a class="button" href="/docs">Interactive API Docs</a></li>
                        <li>POST to <code>/query</code> with your question in JSON</li>
                        <li>See <a href="/schema">/schema</a> for available tables and columns</li>
                    </ul>
                </div>
                <div class="footer">
                    &copy; 2025 FCLM Analytics Team &mdash; <a href="mailto:support@fclm.com">Contact Support</a>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/schema", response_class=JSONResponse, tags=["Utility"])
def schema():
    """Get available tables and columns in the database."""
    return {"schema": safe_query.get_schema_info()}

@app.post("/query", response_model=QueryResponse, tags=["Query"])
def query_endpoint(req: QueryRequest):
    question = req.question
    try:
        sql, explanation = safe_query.natural_to_sql(question)
        if not sql.strip().lower().startswith("select"):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")
        df = safe_query.con.execute(sql).fetchdf()
        results = df.values.tolist()
        columns = list(df.columns)
        return QueryResponse(
            question=question,
            explanation=explanation,
            sql=sql,
            results=results,
            columns=columns
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Query failed",
                "message": str(e),
                "question": question
            }
        )

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="FCLM NL→SQL API Docs",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

if __name__ == "__main__":
    uvicorn.run("scripts.app:app", host="0.0.0.0", port=8000, reload=True)