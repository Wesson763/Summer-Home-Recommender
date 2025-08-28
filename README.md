# Summer Home Finder

An AI-powered property recommendation system built with Streamlit that helps users find their perfect summer getaway.

## Features

- **AI-Powered Recommendations**: Intelligent property matching based on user preferences
- **Dynamic Chatbot**: Conversational interface for location discovery
- **User Authentication**: Secure login system with password validation
- **Clean Design**: Beautiful, modern UI

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your OpenAI API key:
   - **Option 1**: Create `.streamlit/secrets.toml` in the project root with:
     ```toml
     OPENAI_API_KEY = "your_openai_api_key_here"
     ```
   - **Option 2**: Set environment variable: `export OPENAI_API_KEY="your_key_here"`
   - **Option 3**: Copy from scripts: `cp scripts/secrets.toml .streamlit/secrets.toml`
   - Get your API key from [OpenRouter](https://openrouter.ai/) (recommended) or [OpenAI Platform](https://platform.openai.com/api-keys)
4. Run the app: `python3 scripts/run_app.py`

## Important Security Notes

- **Never commit your actual API key to version control**
- The `.streamlit/` directory is already in `.gitignore`
- Use `secrets.toml.example` as a template for others

## Tech Stack

- **Frontend**: Streamlit
- **AI Chatbot**: OpenAI GPT models via OpenRouter
- **Backend**: Python
- **Data**: JSON-based property database

## Troubleshooting

### API Key Issues
If you get "API key not configured" errors:

1. **Verify API key format**: Make sure your key starts with `sk-or-v1-` (OpenRouter) or `sk-` (OpenAI)
2. **Test configuration**: Run `python3 test_api.py` to verify your setup
3. **Check permissions**: Ensure the secrets file is readable

### Common Errors
- **"Module not found"**: Run `pip install -r requirements.txt`
- **"Port already in use"**: Change port in `scripts/run_app.py` or kill existing processes
- **"Authentication failed"**: Check your API key and ensure it has sufficient credits

## 📁 Project Structure

```
Summer_Home_v2/
├── app/                    # Main application code
│   ├── main.py           # Streamlit app entry point
│   ├── models/           # Data models
│   ├── services/         # Business logic services
│   └── utils/            # Utility functions
├── .streamlit/           # Streamlit configuration
│   └── secrets.toml     # API keys (create this)
├── scripts/              # Utility scripts
│   └── run_app.py       # App launcher
└── requirements.txt      # Python dependencies
```
