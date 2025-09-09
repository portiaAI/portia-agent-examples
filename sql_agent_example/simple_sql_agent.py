#!/usr/bin/env python3
"""
Simple SQL Agent Example

This example demonstrates the basic usage of Portia's SQL tools
to create an agent that can query a sample database.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from portia import Config, LLMProvider, Portia, ToolRegistry
from portia.open_source_tools.sql_tool import ListTablesTool, RunSQLTool, GetTableSchemasTool



def main():
    """Run the simple SQL agent example."""
    
    load_dotenv()
    # Set up the database path
    db_path = Path(__file__).parent / "sample_store.db"
    
    # Check if database exists
    if not db_path.exists():
        print(" Database not found!")
        print("Please run 'python setup_database.py' first to create the sample database.")
        return
    
    # Configure the SQL tools to use our database
    os.environ["SQLITE_DB_PATH"] = str(db_path)
    print(f"📊 Using database: {db_path}")
    google= os.getenv("GOOGLE_API_KEY")

    sql_tools = [
        ListTablesTool(),
        GetTableSchemasTool(),
        RunSQLTool(),
    ]

    tool_registry = ToolRegistry(sql_tools)
    config = Config.from_default(
        llm_provider= LLMProvider.GOOGLE,
        google_api_key= google,
        default_model= "google/gemini-2.0-flash",
    )
    
    # Create Portia agent with tools
    agent = Portia(
        config=config,
        tools=tool_registry,
    )
    
    # Example queries to demonstrate the agent
    queries = [
        "List all tables in the database",
        "Show me the first 5 users",
        "What products do we have in the Electronics category?",
        "How many orders are in each status?",
        "Show me the top 3 customers by number of orders",
    ]
    
    print("🤖 SQL Agent Ready!")
    print("=" * 60)
    
    # Process each query
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 50)
        
        try:
            # Run the query through the agent
            result = agent.run(query)
            print(f"📋 Result:\n{result}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Add separator between queries
        if i < len(queries):
            print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
