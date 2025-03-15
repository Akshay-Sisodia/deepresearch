# Deep Research Assistant 🔍

A powerful Streamlit-based research assistant that helps users conduct deep research on any topic using AI-powered search and analysis.

## Features

- 🔍 Advanced web search capabilities
- 🤖 AI-powered research analysis
- 💬 Interactive chat interface
- 📊 Structured research reports
- 🔐 User authentication
- 💾 Chat history management
- 📱 Responsive design

## Prerequisites

- Python 3.8+
- OpenAI API key
- Serper API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/deepresearch.git
cd deepresearch
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` with your API keys and configuration.

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Log in with your credentials and start researching!

## Project Structure

```
deepresearch/
├── app.py              # Main Streamlit application
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── utils/             # Utility modules
│   ├── search.py      # Search API integration
│   ├── cache.py       # Caching utilities
│   ├── model.py       # AI model integration
│   └── logger.py      # Logging configuration
├── static/            # Static assets
├── templates/         # HTML templates
└── .env              # Environment variables
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the GPT models
- Serper for the search API
- Streamlit for the amazing web framework 