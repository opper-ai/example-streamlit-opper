# Opper-powered Streamlit Chat App

This Streamlit application creates an interactive chat interface that leverages Opper's AI capabilities to answer questions about Opper documentation.

## Features

- Chat interface for asking questions about Opper
- Automatic retrieval of relevant information from Opper documentation
- Dynamic creation and querying of a documentation index
- Source attribution for answers
- Code detection and warning

## Setup

1. Install required packages:
   ```
   pip install streamlit opperai requests beautifulsoup4
   ```

2. Set the Opper API key as an environment variable:
   ```
   export OPPER_API_KEY=your_api_key_here
   ```

3. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## How it works

1. The app crawls Opper documentation to create an index (if not already existing).
2. User inputs are processed to determine if knowledge retrieval is necessary.
3. Relevant information is fetched from the index when needed.
4. Responses are generated using Opper's AI, incorporating the retrieved knowledge.
5. Code snippets in responses are detected and flagged with a warning.
6. Sources of information are provided for transparency.

## Note

Ensure you have the necessary permissions and comply with Opper's terms of service when using their API and documentation.
