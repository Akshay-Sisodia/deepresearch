# 🔍 Deep Research Assistant

<p align="center">
  <a href="https://deepresearchdemo.streamlit.app">
    <img src="https://img.shields.io/badge/DEMO-LIVE-00C7B7?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo">
  </a>
  <a href="https://github.com/Akshay-Sisodia/deepresearch/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/LICENSE-MIT-green?style=for-the-badge" alt="License">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/PYTHON-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  </a>
</p>

<p align="center">
  <b>AI-powered research assistant that transforms how you explore and understand any topic</b>
</p>

<p align="center">
  <i>Built with ❤️ for researchers, students, and curious minds</i>
</p>

<hr>

<div align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-live-demo">Demo</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-contributing">Contributing</a> •
  <a href="#-license">License</a>
</div>

<hr>

## ✨ What is Deep Research Assistant?

Deep Research Assistant is a powerful tool that combines advanced AI with intelligent web search to help you conduct comprehensive research on any topic. It processes information from multiple sources, analyzes content, and presents findings in an organized, easy-to-understand format.

<br>

## 🚀 Features

<div align="center">
<table>
<tr>
<td align="center" width="33%">
<img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/magnifying-glass.svg" width="40" height="40">
<br>
<b>Advanced Search</b>
<br>
<small>Intelligent web search powered by Serper API</small>
</td>
<td align="center" width="33%">
<img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/robot.svg" width="40" height="40">
<br>
<b>AI Analysis</b>
<br>
<small>Deep insights from state-of-the-art AI models</small>
</td>
<td align="center" width="33%">
<img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/comments.svg" width="40" height="40">
<br>
<b>Interactive Chat</b>
<br>
<small>Natural conversation interface</small>
</td>
</tr>
<tr>
<td align="center" width="33%">
<img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/chart-simple.svg" width="40" height="40">
<br>
<b>Structured Reports</b>
<br>
<small>Organized research findings</small>
</td>
<td align="center" width="33%">
<img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/floppy-disk.svg" width="40" height="40">
<br>
<b>History Management</b>
<br>
<small>Save and revisit research sessions</small>
</td>
<td align="center" width="33%">
<img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/mobile-screen.svg" width="40" height="40">
<br>
<b>Responsive Design</b>
<br>
<small>Beautiful interface on any device</small>
</td>
</tr>
</table>
</div>

<br>

## 🏁 Quick Start

### Prerequisites

- Python 3.8+
- OpenRouter API key
- Serper API key

<details>
<summary><b>📥 Installation</b></summary>
<br>

```bash
# Clone the repository
git clone https://github.com/Akshay-Sisodia/deepresearch.git
cd deepresearch

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```
</details>

<details>
<summary><b>▶️ Running the App</b></summary>
<br>

```bash
# Option 1: Direct run
streamlit run app.py

# Option 2: Using the run script (recommended)
python scripts/run_app.py
```
</details>

<br>

## 🌐 Live Demo

<div align="center">
  <a href="https://deepresearchdemo.streamlit.app">
    <img src="https://img.shields.io/badge/TRY_IT_NOW-deepresearchdemo.streamlit.app-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Try it now">
  </a>
</div>

<br>

## 🔧 Configuration

<details>
<summary><b>API Keys Setup</b></summary>
<br>

Create a `.streamlit/secrets.toml` file with your API keys:

```toml
OPENROUTER_API_KEY = "your-api-key-here"
SERPER_API_KEY = "your-api-key-here"
```
</details>

<details>
<summary><b>Streamlit Cloud Deployment</b></summary>
<br>

To deploy to Streamlit Cloud:

1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and select your forked repository
4. Set the main file path to `app.py`
5. Add your API keys in the Secrets section:
   ```toml
   OPENROUTER_API_KEY = "your-api-key-here"
   SERPER_API_KEY = "your-api-key-here"
   ```
6. Deploy the app

The app is already configured for Streamlit Cloud with:
- `runtime.txt` - Specifies Python version
- `Procfile` - Defines how to run the app
- `.streamlit/config.toml` - Configures Streamlit settings
- Health check endpoint for monitoring
</details>

<details>
<summary><b>Project Structure</b></summary>
<br>

```
deepresearch/
├── app.py                # Main Streamlit application
├── config.py             # Configuration settings
├── theme_config.py       # UI theme configuration
├── docs/                 # Documentation
│   ├── api.md            # API reference
│   ├── development.md    # Development guide
│   ├── installation.md   # Installation guide
│   └── usage.md          # Usage guide
├── modules/              # Core functionality modules
│   ├── chat/             # Chat interface components
│   ├── research/         # Research processing logic
│   ├── session/          # Session state management
│   └── ui/               # User interface components
├── scripts/              # Utility scripts
│   ├── check_api_keys.py # API key validation
│   ├── download_fonts.py # Font downloader
│   └── run_app.py        # Application runner
├── static/               # Static assets
│   └── css/              # CSS files
├── tests/                # Test suite
│   └── test_utils.py     # Tests for utilities
└── utils/                # Utility modules
    ├── cache.py          # Caching utilities
    ├── logger.py         # Logging configuration
    ├── model.py          # AI model integration
    └── search.py         # Search API integration
```
</details>

<br>

## 👥 Contributing

<details>
<summary><b>How to Contribute</b></summary>
<br>

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For more detailed information, see our [Development Guide](docs/development.md).
</details>

<br>

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<br>

## 🙏 Acknowledgments

<div align="center">
  <table>
    <tr>
      <td align="center">
        <a href="https://openrouter.ai/">
          <img src="https://img.shields.io/badge/OpenRouter-AI_Models-lightgrey?style=for-the-badge&logo=openai&logoColor=white" alt="OpenRouter">
        </a>
      </td>
      <td align="center">
        <a href="https://serper.dev/">
          <img src="https://img.shields.io/badge/Serper-Search_API-orange?style=for-the-badge&logo=google&logoColor=white" alt="Serper">
        </a>
      </td>
      <td align="center">
        <a href="https://streamlit.io/">
          <img src="https://img.shields.io/badge/Streamlit-Framework-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
        </a>
      </td>
    </tr>
  </table>
</div>

<hr>

<div align="center">
  <sub>Made with 💻 and ☕ by <a href="https://github.com/Akshay-Sisodia">Akshay Sisodia</a></sub>
</div> 