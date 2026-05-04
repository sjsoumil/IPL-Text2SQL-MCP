# IPL Text2SQL MCP Server

A natural-language IPL cricket analytics system built with **MCP (Model Context Protocol)**, **LangChain SQL tools**, and a **ReAct agent** — ask questions in plain English and get answers from a full IPL database (2008–2026).

## Architecture

```
User Query (natural language)
        ↓
  ReAct Agent (react_client.py)
        ↓
  MCP Client (langchain-mcp-adapters)
        ↓
  MCP Server (text2sql_server.py)
        ↓
  LangChain SQL Toolkit → SQLite (ipl_insights.db)
```

## Database Schema

Six relational tables covering all IPL seasons (2008–2026):

| Table | Description |
|-------|-------------|
| `Team` | 10 IPL franchises (CSK, MI, RCB, KKR, SRH, DC, RR, PBKS, GT, LSG) |
| `Player` | 47 players — Kohli, Rohit, Dhoni, Bumrah, and more |
| `Season` | Season results, winners, MVPs, status (Completed / In Progress) |
| `Match` | Every match — venue, winner, win type/margin, Man of Match |
| `Batting` | Per-match batting stats — runs, balls, fours, sixes, strike rate |
| `Bowling` | Per-match bowling stats — overs, wickets, runs conceded, economy |

## MCP Tools Exposed

| Tool | Description |
|------|-------------|
| `sql_db_list_tables` | List all tables in the database |
| `sql_db_schema` | Fetch schema + sample rows for given tables |
| `sql_db_query_checker` | Validate SQL before execution |
| `sql_db_query` | Execute a SQL SELECT query |

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/sjsoumil/IPL-Text2SQL-MCP.git
cd IPL-Text2SQL-MCP
```

### 2. Install dependencies

```bash
pip install mcp langchain langchain-openai langchain-community langchain-mcp-adapters langgraph python-dotenv
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 4. Generate the database

```bash
python create_ipl_db.py
```

### 5. Start the MCP server

```bash
python text2sql_server.py
```

The server starts at `http://localhost:8010/mcp`.

### 6. Run the ReAct client

```bash
python react_client.py
```

## Example Questions

```
Who are the top 5 run-scorers of all time in the IPL?
Which team has won the most IPL titles?
Who leads the 2026 Orange Cap right now?
Show Virat Kohli's runs season by season.
Who took the most wickets in IPL 2025?
Which team has the best win percentage at home?
```

## Files

| File | Purpose |
|------|---------|
| `text2sql_server.py` | FastMCP server exposing SQL tools over HTTP |
| `react_client.py` | Interactive ReAct agent CLI client |
| `create_ipl_db.py` | Script to generate the `ipl_insights.db` SQLite database |

## Requirements

- Python 3.10+
- OpenAI API key (GPT-4.1-mini)
