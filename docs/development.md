# Development Guide

This guide is for developers who want to contribute to the Deep Research Assistant project.

## Development Environment Setup

### Prerequisites

- Python 3.8+
- Git
- A code editor (VS Code, PyCharm, etc.)
- OpenRouter API key
- Serper API key

### Setting Up for Development

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/deepresearch.git
   cd deepresearch
   ```
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Install development dependencies:
   ```bash
   pip install pytest pytest-cov black flake8
   ```
6. Set up environment variables as described in the [Installation Guide](installation.md)

## Project Structure

```
deepresearch/
├── app.py                # Main Streamlit application
├── config.py             # Configuration settings
├── theme_config.py       # UI theme configuration
├── docs/                 # Documentation
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

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Development branch
- Feature branches - `feature/your-feature-name`
- Bug fix branches - `fix/bug-description`

### Making Changes

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run tests to ensure everything works:
   ```bash
   pytest
   ```
4. Format your code:
   ```bash
   black .
   ```
5. Check for linting issues:
   ```bash
   flake8
   ```
6. Commit your changes:
   ```bash
   git commit -m "Add your meaningful commit message here"
   ```
7. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
8. Create a pull request on GitHub

## Testing

### Running Tests

```bash
pytest
```

### Running Tests with Coverage

```bash
pytest --cov=.
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with the prefix `test_`
- Use descriptive test method names
- Include docstrings explaining what each test does

## Code Style

This project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. We use:

- Black for code formatting
- Flake8 for linting

## Documentation

- Update documentation when you add or modify features
- Use docstrings for all functions, classes, and methods
- Follow the Google docstring format

## Continuous Integration

This project uses GitHub Actions for continuous integration. Each pull request will:

1. Run tests
2. Check code formatting
3. Check for linting issues

## Release Process

1. Update version number in relevant files
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. Tag the release with the version number

## Getting Help

If you need help with development, you can:

- Open an issue on GitHub
- Reach out to the maintainers
- Check the existing documentation and code comments