# DVLA Chat Agent

## Introduction

This example demonstrates how to create a specialized chat interface for a DVLA (Driver and Vehicle Licensing Agency) agent using Portia AI and Streamlit. The agent is focused on 3 specific DVLA services with intelligent conversation classification and task-specific workflows. It uses the [Portia SDK](https://github.com/portiaAI/portia-sdk-python) for AI agent capabilities and Streamlit for the chat interface.

## Features

- 🚗 **Specialized DVLA Services**: Focused on 3 core tasks only
- 🧠 **Smart Classification**: Automatically categorizes user requests
- 📋 **Instructions & How-To**: Search-powered answers for DVLA procedures
- 🆔 **License Applications**: Complete application processing with structured data collection
- 💷 **Vehicle Tax Payments**: Tax payment processing with realistic calculations
- 💬 **Conversation Context**: Maintains full conversation history
- 🤖 **AI-Powered Workflows**: Each task has a specialized agent workflow
- 🤔 **Interactive Clarifications**: Agent can ask follow-up questions during processing
- 🎛️ **User-Friendly Interface**: Clear prompts and helpful guidance

## Prerequisites

- A Portia AI API key: You can get one from [app.portialabs.ai](https://app.portialabs.ai) > API Keys.
- An LLM API key for a supported model (e.g Anthropic, OpenAI or Mistral)
- We use `uv` to manage dependencies. You can install it from [here](https://docs.astral.sh/uv/getting-started/installation/).

## Setup

1. Clone the repository and navigate to the `dvla-agent` folder.

2. **Create a `.env` file** with your API keys:
   ```bash
   # Create .env file with your API keys
   cat > .env << EOF
   # Portia API Configuration
   PORTIA_API_KEY=your_portia_api_key_here
   
   # LLM API Keys (choose one based on your preferred provider)
   # OpenAI
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Anthropic 
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   EOF
   ```

3. **Install dependencies**: `uv sync`

## Running the Chat App

You have several options to run the chat application:

### Option 1: Using the run script
```bash
./run_app.sh
```

### Option 2: Using uv directly
```bash
uv run streamlit run app.py
```

### Option 3: Using streamlit directly (if installed globally)
```bash
streamlit run app.py
```

The chat interface will open in your browser at `http://localhost:8501`.

## How the Agent Works

The DVLA agent uses a **classification-first approach** with specialized workflows for each task:

### 1. 🧠 Smart Classification
When you send a message, the agent first analyzes it and classifies it into one of these categories:
- **Instructions & How-To**: Questions about DVLA procedures
- **Driving License Application**: Requests to apply for a new license  
- **Vehicle Tax Payment**: Requests to pay vehicle tax
- **Other**: Queries that don't fit the above (politely redirected)

### 2. 📋 Instructions Workflow
If asking for instructions:
- **Search Step**: Uses search tool to find relevant DVLA information
- **Answer Generation**: Provides comprehensive, step-by-step guidance
- **Final Response**: Formatted answer with all necessary details

Example prompts:
- "How do I renew my driving license?"
- "What documents do I need to register a vehicle?"
- "How to change my address on my license?"

### 3. 🆔 License Application Workflow  
If applying for a driving license:
- **Data Collection**: Gathers all required information through conversation
- **Structured Processing**: Captures details in a standardized format
- **Application Submission**: Simulates processing with realistic timelines
- **Confirmation**: Provides reference number and next steps

Required information collected:
- Full name, date of birth, address
- Phone number and email
- License type (full, provisional, motorcycle, etc.)
- Previous license details (if replacing)

### 4. 💷 Vehicle Tax Workflow
If paying vehicle tax:
- **Vehicle Details**: Collects registration, make/model, fuel type
- **Tax Calculation**: Calculates realistic tax amounts based on vehicle type
- **Payment Processing**: Simulates 2-second processing time
- **Confirmation**: Provides payment reference and important notes

Required information collected:
- Vehicle registration number
- Make, model, and vehicle type
- Engine size and fuel type
- Tax period preference (6 or 12 months)
- Owner details

### 5. 🤔 Interactive Clarifications
The agent can ask follow-up questions at any point during processing:
- **Smart Questions**: If the agent needs more specific information, it will ask
- **Context Aware**: Questions are tailored to the specific task being processed
- **Seamless Flow**: Clarifications integrate naturally into the chat conversation
- **Visual Indicators**: UI shows when the agent is waiting for clarification

**How it works**:
1. During plan execution, if the agent needs clarification, it pauses
2. A clarification message appears in the chat (marked with 🤔)
3. The sidebar shows "Waiting for clarification" status
4. The chat input prompt changes to guide the user
5. Once you respond, the agent continues processing with your additional information

## Understanding the code

### Core Components

#### **`app.py`** - Main Application
The complete DVLA agent implementation including:

**Data Models**:
- `DVLAQueryType`: Enum for task classification
- `DrivingLicenseApplication`: Schema for license applications  
- `CarTaxPayment`: Schema for tax payment details
- `InstructionResponse`: Schema for instruction answers

**Processing Functions**:
- `process_driving_license_application()`: Simulates license processing (2s delay)
- `process_car_tax_payment()`: Calculates and processes tax payments (2s delay)  
- `send_final_answer()`: Formats and sends responses

**Plan Structure**:
- **Classification Step**: Categorizes user intent using react_agent_step
- **Conditional Branching**: Routes to appropriate workflow based on classification
- **Task-Specific Workflows**: Specialized processing for each of the 3 tasks

**Streamlit Interface**:
- **Chat UI**: Natural conversation interface with message history
- **Service Overview**: Visual cards showing the 3 supported services
- **Example Prompts**: Sidebar with helpful example queries for each service type
- **Session Management**: Persistent conversation state across interactions

#### **Technical Features**

- **Async Processing**: Non-blocking execution of Portia plans with async sleeps for simulations
- **Caching**: `@st.cache_resource` for performance optimization of Portia instances
- **Interactive Clarifications**: Custom `UserMessageClarificationHandler` integrates Portia's clarification system with Streamlit chat
- **Error Handling**: Graceful handling of plan execution failures and clarification errors
- **Structured Output**: Type-safe data collection and processing with Pydantic schemas
- **Search Integration**: React agents have direct access to search tools for dynamic information gathering
- **Session State Management**: Persistent conversation state and clarification handling across Streamlit reruns
