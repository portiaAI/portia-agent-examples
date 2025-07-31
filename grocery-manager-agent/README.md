# Portia Grocery Store Agent

## Introduction
The Portia Grocery Store Agent is an automated shopping assistant that helps you manage your grocery shopping. It can:
- Extract your grocery list from Google Keep.
- Search for items on Morrisons website.
- Handle product alternatives when items aren't available
- Add items to your cart
- Provide a summary of your cart and total price

Currently supported:
- Notes App: Google Keep
- Grocery Store: Morrisons

## Prerequisites
- Python 3.11 or higher
- A Morrisons online account
- A Google account with access to Google Keep

## Setup
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd portia-agent-examples/grocery-manager-agent
   ```

2. Configure your environment:
   - Have your LLM API key and Portia API key in a .env file. Copy the `.env.example` file to `.env` and add your API keys to it.


### Running the agent
1. Start the agent:
   ```bash
   uv run main.py
   ```

2. Follow the prompts to:
   - Select your notes app (currently Google Keep only)
   - Select your grocery store (currently Morrisons only)
   - Log in to your accounts when prompted
   - Choose alternatives for products when needed
   - Review your cart and complete checkout

## Understanding the code
The project is structured into several key components:

### `main.py`
The entry point of the application that:
- Sets up the Portia instance with necessary tools
- Handles user preferences
- Orchestrates the shopping process

### `notes_agent.py`
Responsible for:
- Connecting to your notes app
- Extracting your grocery list
- Parsing the list into a format the shopping agent can use

### `shopping_agent.py`
Manages the shopping process by:
- Navigating the grocery store website
- Searching for products
- Handling login requirements
- Managing the shopping cart
- Processing each item in your list
- Providing cart summaries

### `grocery_tool.py`
A custom Portia tool that:
- Handles product alternatives
- Manages user choices
- Provides skip functionality for unwanted items

### Key Features
- Automated login handling
- Smart product alternative suggestions
- Skip option for unavailable items
- Cart summary
- Error handling and recovery
- User-friendly CLI interface
