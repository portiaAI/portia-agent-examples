#!/bin/bash

echo "Starting DVLA Chat Assistant..."
uv run streamlit run app.py --server.port 8501 --server.address localhost
