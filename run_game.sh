#!/bin/bash

# Set the Mistral API key
export LLM_API_KEY=oEZXrIHDSdpyNEylv3FnHBK60DFbtevU

# Set the ElevenLabs API key
export ELEVENLABS_API_KEY=sk_6c359493cb4634b304158913d8e26a1def45041b3c409862

# Activate virtual environment and run the game
source venv/bin/activate
python main.py
