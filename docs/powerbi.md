# Power BI Integration Guide

## How to Connect Power BI to FCLM Agent API

### 1. DirectQuery via Power Query (M)

```
let
    url = "http://localhost:8000/powerbi/query",
    body = Json.FromValue([question="Show monthly failures by machine"]),
    headers = ["Content-Type"="application/json", "X-API-Key"="demo-key"],
    response = Web.Contents(url, [Content=body, Headers=headers]),
    json = Json.Document(response),
    table = Table.FromRecords(json[rows])
in
    table
```

### 2. Export Data for Power BI Folder Connector
- Use the Streamlit Agent Demo page to export tables to CSV, Parquet, or XLSX in the `outputs/` folder.
- In Power BI Desktop, use the Folder connector to load exported files.

### 3. Scheduling Refresh
- Use Power BI Gateway to schedule refreshes from the `outputs/` folder.
- Use the `/refresh` API endpoint to automate file updates.

### 4. Example curl
```
curl -X POST http://localhost:8000/powerbi/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{"question": "Show monthly failures by machine"}'
```

### 5. Notes
- Only SELECT statements are allowed.
- Only whitelisted tables/columns are exposed.
- API-key required in header: `X-API-Key`
- For advanced integration, see the API docs and unit tests in `/tests/`.
