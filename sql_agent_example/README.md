# SQL Agent Example

This example demonstrates how to create AI agents that can query and analyze SQL databases using Portia's new SQL tools. The example includes a complete setup with sample data and  simple agent implementations.

## 🚀 What This Example Demonstrates

- **Database Setup**: Create a realistic sample SQLite database from scratch
- **SQL Tools Integration**: Use all four Portia SQL tools:
  - `RunSQLTool`: Execute read-only SQL queries
  - `ListTablesTool`: Discover available tables
  - `GetTableSchemasTool`: Explore table structures
  - `CheckSQLTool`: Validate queries before execution
- **Agent Creation**: Build AI agents that can understand natural language queries about your data

## 📋 Prerequisites

- Python 3.11 or higher
- Portia AI SDK
- Required API keys (OpenAI, Anthropic, or other supported providers)

## 🛠️ Installation & Setup

1. **Clone or download this example**:
   ```bash
   cd sql_agent_example
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your AI provider API key**:
   ```bash
   # For OpenAI
   export OPENAI_API_KEY="your-openai-api-key"
   
   # Or for Anthropic
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   
   # Or for Google
   export GOOGLE_API_KEY="your-google-api-key"
   ```

4. **Create the sample database**:
   ```bash
   python setup_database.py
   ```

   This will create `sample_store.db` with realistic e-commerce data including:
   - **Users**: 10 sample users with demographics
   - **Products**: 10 products across different categories
   - **Orders**: 25 orders with various statuses
   - **Order Items**: Detailed order line items

## 📊 Sample Database Schema

The example creates a simple e-commerce database with these tables:

### Users Table
- `id`, `username`, `email`, `first_name`, `last_name`
- `age`, `city`, `country`, `created_at`, `is_active`

### Products Table  
- `id`, `name`, `category`, `price`, `cost`
- `stock_quantity`, `description`, `created_at`, `is_active`

### Orders Table
- `id`, `user_id`, `order_date`, `status`
- `total_amount`, `shipping_address`

### Order Items Table
- `id`, `order_id`, `product_id`, `quantity`, `unit_price`

## 🎯 Running the Examples

### 1. Simple Agent Example

Run predefined queries to see the agent in action:

```bash
python simple_sql_agent.py
```

This will demonstrate:
- Listing all tables
- Querying user data
- Filtering products by category
- Aggregating order statistics
- Finding top customers

## 🛡️ Security Features

The SQL tools include built-in security features:

- **Read-only Access**: Only SELECT queries are allowed
- **SQLite Authorizer**: Prevents any write operations at the database level
- **Query Validation**: Validates queries before execution
- **Safe PRAGMA Commands**: Only allows read-only PRAGMA operations

### Using Different Database Types
While this example uses SQLite, the SQL tools support a pluggable adapter architecture. You can create custom adapters for other databases:

```python
from portia.open_source_tools.sql_tool import SQLAdapter, RunSQLTool

class MyDatabaseAdapter(SQLAdapter):
    # Implement required methods for your database
    pass

# Use with any SQL tool
custom_tool = RunSQLTool(adapter=MyDatabaseAdapter())
```

## ⚠️ Important Notes

- The SQL tools are **read-only** by design for security
- All queries are validated before execution
- The agent automatically chooses the appropriate SQL tool based on your question
- Database connections are properly managed and closed

---

**Happy querying! 🎉**
