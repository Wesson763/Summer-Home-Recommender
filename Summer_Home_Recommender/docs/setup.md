# Setup Guide - Summer Home Finder

## Prerequisites
- Python 3.8+
- pip package manager
- Git

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/summer-home-finder.git
cd summer-home-finder
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
```

### 4. Run the Application
```bash
# Option 1: Using the launcher script
python scripts/run_app.py

# Option 2: Direct Streamlit command
streamlit run app/main.py

# Option 3: Using shell script (Unix/Mac)
./scripts/start_app.sh
```

### 5. Access the App
Open your browser to: http://localhost:8501

## Troubleshooting
- **Port already in use**: Change port in run_app.py
- **API key issues**: Verify your OpenAI API key in .env
- **Import errors**: Ensure you're in the project root directory
