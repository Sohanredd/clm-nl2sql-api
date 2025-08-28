# scripts/easy_query.py
import duckdb
import pathlib
import pandas as pd
from datetime import datetime, timedelta
import re
from rich.console import Console
from rich.table import Table

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB   = ROOT / "db" / "fclm.duckdb"
con  = duckdb.connect(DB.as_posix())
console = Console()

QUERY_TEMPLATES = {
    "1": {
        "name": "Show failure counts by machine",
        "sql": """
            SELECT {machine_col} as machine, COUNT(*) as failure_count
            FROM {table}
            WHERE LOWER({status_col}) LIKE '%fail%'
               OR LOWER({status_col}) LIKE '%error%'
               OR LOWER({status_col}) LIKE '%reject%'
            GROUP BY {machine_col}
            ORDER BY failure_count DESC
        """
    },
    "2": {
        "name": "Show daily throughput last 30 days",
        "sql": """
            SELECT 
                DATE_TRUNC('day', {date_col}::TIMESTAMP) as day,
                COUNT(*) as count
            FROM {table}
            WHERE {date_col}::TIMESTAMP > CURRENT_DATE - INTERVAL '30 days'
            GROUP BY 1
            ORDER BY 1
        """
    },
    "3": {
        "name": "Show status distribution",
        "sql": """
            SELECT 
                {status_col} as status,
                COUNT(*) as count,
                (COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()) as percentage
            FROM {table}
            GROUP BY 1
            ORDER BY 2 DESC
        """
    },
    "4": {
        "name": "Show recent failures",
        "sql": """
            SELECT 
                {date_col} as timestamp,
                {machine_col} as machine,
                {status_col} as status
            FROM {table}
            WHERE LOWER({status_col}) LIKE '%fail%'
               OR LOWER({status_col}) LIKE '%error%'
               OR LOWER({status_col}) LIKE '%reject%'
            ORDER BY {date_col} DESC
            LIMIT 10
        """
    }
}

def find_column(table, *patterns):
    """Find column in table matching any of the patterns."""
    cols = con.execute(f"PRAGMA table_info('{table}')").fetchall()
    for col in cols:
        col_name = col[1].lower()
        for pattern in patterns:
            if pattern.lower() in col_name:
                return col[1]
    return None

def get_tables():
    """Get list of available tables."""
    return [t[0] for t in con.execute("SHOW TABLES").fetchall()]

def display_results(df):
    """Display results in a nice table format."""
    if len(df) == 0:
        console.print("[yellow]No results found[/]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    
    # Add columns
    for column in df.columns:
        table.add_column(str(column))
    
    # Add rows
    for _, row in df.iterrows():
        table.add_row(*[str(x) for x in row])
    
    console.print(table)

def main():
    console.print("[bold blue]📊 FCLM Easy Query Interface[/]")
    
    # Get available tables
    tables = get_tables()
    console.print("\n[bold]Available tables:[/]")
    for i, table in enumerate(tables, 1):
        console.print(f"{i}. {table}")
    
    while True:
        # Table selection
        table_idx = console.input("\n[bold green]Select table number (or 'exit'):[/] ")
        if table_idx.lower() in ('exit', 'quit'):
            break
        
        try:
            table = tables[int(table_idx) - 1]
        except (ValueError, IndexError):
            console.print("[red]Invalid table number[/]")
            continue
            
        # Query selection
        console.print("\n[bold]Available queries:[/]")
        for qid, details in QUERY_TEMPLATES.items():
            console.print(f"{qid}. {details['name']}")
            
        query_id = console.input("\n[bold green]Select query number:[/] ")
        if query_id not in QUERY_TEMPLATES:
            console.print("[red]Invalid query number[/]")
            continue
            
        # Dynamically determine which columns are needed for the selected query
        template_sql = QUERY_TEMPLATES[query_id]["sql"]
        needed = {}
        if "{status_col}" in template_sql:
            needed["status_col"] = find_column(table, "status", "result", "outcome")
        if "{machine_col}" in template_sql:
            needed["machine_col"] = find_column(table, "machine", "tool", "station")
        if "{date_col}" in template_sql:
            needed["date_col"] = find_column(table, "date", "time", "timestamp")

        missing = [k for k, v in needed.items() if v is None]
        if missing:
            console.print(f"[red]Required columns not found in table: {', '.join(missing)}[/]")
            continue

        # Execute query
        try:
            sql = template_sql.format(
                table=table,
                status_col=needed.get("status_col", ""),
                machine_col=needed.get("machine_col", ""),
                date_col=needed.get("date_col", "")
            )

            console.print("\n[bold]Results:[/]")
            df = con.execute(sql).fetchdf()
            display_results(df)

        except Exception as e:
            console.print(f"[red]Error:[/] {str(e)}")

        console.print("\n" + "─" * 80)

if __name__ == "__main__":
    main()
