from mcp.server.fastmcp import FastMCP
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from dotenv import load_dotenv
import os
import traceback

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "ipl_insights.db")
PORT = int(os.getenv("PORT", "8010"))

if not os.path.exists(DB_PATH):
    print(f"WARNING: Database not found at {DB_PATH}")
    print("Run: python create_ipl_db.py")
else:
    print(f"Database found at {DB_PATH}")

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
sql_tools = sql_toolkit.get_tools()

print(f"Initialized {len(sql_tools)} LangChain SQL tools")

mcp = FastMCP(
    name="IPLText2SQLServer",
    instructions=(
        "IPL cricket analytics database covering all seasons 2008-2026. "
        "Tables: Team, Player, Season, Match, Batting, Bowling. "
        "Use the tools to list tables, inspect schemas, validate and execute SQL queries "
        "to answer questions about IPL players, teams, matches, and statistics."
    ),
    port=PORT,
)

tool_map = {t.name: t for t in sql_tools}


@mcp.tool()
async def sql_db_list_tables(tool_input: str = "") -> str:
    """List all available tables in the IPL database."""
    try:
        result = await tool_map["sql_db_list_tables"].ainvoke("")
        tables_str = result if isinstance(result, str) else ", ".join(result) if result else "No tables found"
        print(f"[list_tables] {tables_str}")
        return tables_str
    except Exception as e:
        error = f"Error listing tables: {str(e)}"
        print(f"[ERROR] {error}")
        traceback.print_exc()
        return error


@mcp.tool()
async def sql_db_schema(table_names: str) -> str:
    """
    Get the schema and sample rows for one or more tables.
    Input: comma-separated table names, e.g. "Batting, Player"
    Output: column definitions and sample rows for each table
    """
    try:
        cleaned = table_names.strip()
        print(f"[schema] Fetching schema for: '{cleaned}'")
        result = await tool_map["sql_db_schema"].ainvoke(cleaned)
        result_str = str(result)
        print(f"[schema] Returned {len(result_str)} chars")
        return result_str
    except Exception as e:
        error = f"Error getting schema: {str(e)}"
        print(f"[ERROR] {error}")
        traceback.print_exc()
        return error


@mcp.tool()
async def sql_db_query_checker(query: str) -> str:
    """
    Validate SQL query syntax and safety before execution.
    Input: SQL query string
    Output: validated/corrected query, or an error message
    """
    try:
        print(f"[checker] Validating: {query[:80]}...")
        result = await tool_map["sql_db_query_checker"].ainvoke(query)
        print(f"[checker] Valid")
        return str(result)
    except Exception as e:
        error = f"Query validation error: {str(e)}"
        print(f"[ERROR] {error}")
        traceback.print_exc()
        return error


@mcp.tool()
async def sql_db_query(query: str) -> str:
    """
    Execute a SQL SELECT query and return the results.
    Input: a valid SQL SELECT query
    Output: query results as a string
    """
    try:
        print(f"[query] Executing: {query[:80]}...")
        result = await tool_map["sql_db_query"].ainvoke(query)
        result_str = str(result)
        preview = result_str[:200] + "..." if len(result_str) > 200 else result_str
        print(f"[query] Result preview: {preview}")
        return result_str
    except Exception as e:
        error = f"Query execution error: {str(e)}"
        print(f"[ERROR] {error}")
        traceback.print_exc()
        return error


if __name__ == "__main__":
    print(f"\nStarting IPLText2SQLServer")
    print(f"  URL      : http://localhost:{PORT}/mcp")
    print(f"  Database : {DB_PATH}")
    print(f"  Tools    : {list(tool_map.keys())}\n")
    mcp.run(transport="streamable-http")
