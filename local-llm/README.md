# Local LLM Demo

A demo using Portia with local LLMs and Obsidian app.

## Overview

This project demonstrates how to use the Portia framework with local Large Language Models (LLMs) and integrate with Obsidian for knowledge management. It specifically uses Ollama with the Qwen model as the local LLM.

## Prerequisites

- Python 3.11 or higher
- Poetry (for dependency management)
- [Ollama](https://ollama.ai/) installed locally
- Qwen model pulled in Ollama

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd local-llm
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Install and set up Ollama:
   ```bash
   # Install Ollama from https://ollama.ai/
   
   # Pull the Qwen model (we're using the 4B version in this example)
   ollama pull qwen3:4b 
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   # Obsidian Configuration
   OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
   ```

## Running the Demo

To run the main script:

```bash
poetry run python main.py
```

Or activate the Poetry environment first and then run:

```bash
poetry shell
python main.py
```

## Features

- Integration with Ollama running the Qwen model locally
- Obsidian vault processing and knowledge extraction for a note.
- Visualization of the note's knowledge graph is then generated and saved to the Obsidian vault under `visualizations` folder.