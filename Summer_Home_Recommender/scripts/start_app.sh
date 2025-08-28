#!/bin/bash
cd /Users/wesson/Python/Projects/Python_Colloquium/Summer_Home
echo "🏖️ Starting Summer Home Finder..."
echo "📍 The app will open at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the application"
echo "-" * 50

# Skip the email prompt and start the app
printf "\n" | python3 -m streamlit run streamlit_app.py --server.headless true --server.port 8501
