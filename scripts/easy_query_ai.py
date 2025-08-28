# scripts/easy_query_ai.py
import duckdb
import pathlib
import pandas as pd
from rich.console import Console
from rich.table import Table
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB   = ROOT / "db" / "fclm.duckdb"
con  = duckdb.connect(DB.as_posix())
console = Console()

def get_schema_info():
    """Get schema information for all tables."""
    tables = con.execute("SHOW TABLES").fetchall()
    schema = []
    for t in tables:
        table_name = t[0]
        columns = con.execute(f"PRAGMA table_info('{table_name}')").fetchall()
        col_info = [f"{c[1]} {c[2]}" for c in columns]
        schema.append(f"Table {table_name}:\n  " + "\n  ".join(col_info))
    return "\n\n".join(schema)

def find_column(table, *patterns):
    """Find column in table matching any of the patterns."""
    cols = con.execute(f"PRAGMA table_info('{table}')").fetchall()
    for col in cols:
        col_name = col[1].lower()
        for pattern in patterns:
            if pattern.lower() in col_name:
                return col[1]
    return None

def natural_to_sql(query):
    """Convert natural language to SQL using pattern matching and templates."""
    tables = con.execute("SHOW TABLES").fetchall()
    if not tables:
        return None
        
    # Default to first table if no specific table mentioned
    table = tables[0][0]
    for t in tables:
        if t[0].lower() in query.lower():
            table = t[0]
            break
    
    # Find relevant columns
    status_col = find_column(table, "status", "result", "outcome", "defect")
    date_col = find_column(table, "date", "time", "timestamp")
    machine_col = find_column(table, "machine", "tool", "station")
    
    # Pattern matching for common query types
    query = query.lower()
    
    if any(word in query for word in ["fail", "error", "reject", "defect"]):
        if "count" in query or "number" in query:
            if machine_col:
                return f"""
                    SELECT {machine_col} as machine, COUNT(*) as failure_count
                    FROM {table}
                    WHERE LOWER({status_col}) LIKE '%fail%'
                       OR LOWER({status_col}) LIKE '%error%'
                       OR LOWER({status_col}) LIKE '%reject%'
                    GROUP BY {machine_col}
                    ORDER BY failure_count DESC
                """
            else:
                return f"""
                    SELECT {status_col} as status, COUNT(*) as count
                    FROM {table}
                    WHERE LOWER({status_col}) LIKE '%fail%'
                       OR LOWER({status_col}) LIKE '%error%'
                       OR LOWER({status_col}) LIKE '%reject%'
                    GROUP BY {status_col}
                    ORDER BY count DESC
                """
    
    if "daily" in query or "per day" in query or "by day" in query:
        if date_col:
            return f"""
                SELECT 
                    DATE_TRUNC('day', {date_col}::TIMESTAMP) as day,
                    COUNT(*) as count
                FROM {table}
                GROUP BY 1
                ORDER BY 1 DESC
                LIMIT 30
            """
    
    if "status" in query and "distribution" in query or "count" in query:
        if status_col:
            return f"""
                SELECT 
                    {status_col} as status,
                    COUNT(*) as count,
                    (COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()) as percentage
                FROM {table}
                GROUP BY 1
                ORDER BY 2 DESC
            """
    
    if "recent" in query:
        cols = [date_col] if date_col else []
        cols += [machine_col] if machine_col else []
        cols += [status_col] if status_col else []
        
        if cols:
            return f"""
                SELECT {', '.join(cols)}
                FROM {table}
                ORDER BY {date_col} DESC
                LIMIT 10
            """
    
    # Default to showing all columns and some sample rows
    return f"""
        SELECT *
        FROM {table}
        LIMIT 5
    """

def display_results(df):
    """Display results in a nice table format."""
    if len(df) == 0:
        console.print("[yellow]No results found[/]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    for column in df.columns:
        table.add_column(str(column))
    for _, row in df.iterrows():
        table.add_row(*[str(x) for x in row])
    console.print(table)

def main():
    console.print("[bold blue]🔍 FCLM Smart Query Interface[/]")
    console.print("\nAsk questions in plain English. Examples:")
    console.print("- Show me failure counts by machine")
    console.print("- Show daily production numbers")
    console.print("- What's the status distribution?")
    console.print("- Show recent records")
    console.print("- Show me the last 5 rows")
    console.print("\nTip: Include specific table names in your question to query different tables\n")
    
    while True:
        question = console.input("\n[bold green]Question (or 'exit'):[/] ")
        if question.lower() in ('exit', 'quit'):
            break
            
        try:
            sql = natural_to_sql(question)
            if sql:
                console.print("\n[bold blue]Generated SQL:[/]")
                console.print(sql)
                console.print("\n[bold blue]Results:[/]")
                
                results = con.execute(sql).fetchdf()
                display_results(results)
                
        except Exception as e:
            console.print(f"[red]Error:[/] {str(e)}")
            
        console.print("\n" + "─" * 80)

if __name__ == "__main__":
    main()
