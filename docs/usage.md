# Usage Guide

This guide explains how to use the Deep Research Assistant effectively.

## Getting Started

After [installing](installation.md) the application, you can start it by running:

```bash
streamlit run app.py
```

Or use the provided run script:

```bash
python scripts/run_app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Main Interface

The Deep Research Assistant has a clean, intuitive interface with the following components:

1. **Sidebar** - For chat management and settings
2. **Main Content Area** - For research and chat interactions
3. **Research Results** - Where search results and AI analysis are displayed

## Conducting Research

### Starting a New Research Session

1. Enter your research topic or question in the input field
2. Click "Research" to begin the research process
3. The system will search the web and analyze the results

### Interacting with Research Results

- **View Sources**: Click on source links to view the original content
- **Ask Follow-up Questions**: Use the chat interface to ask follow-up questions
- **Generate Reports**: Request structured reports on specific aspects of your research

## Chat Features

### Managing Chat History

- **Save Chats**: Your research sessions are automatically saved
- **Load Previous Chats**: Access your previous research from the sidebar
- **Delete Chats**: Remove unwanted research sessions

### Chat Commands

You can use special commands in the chat:

- `/search [query]` - Perform a new search
- `/report` - Generate a structured report on the current topic
- `/clear` - Clear the current chat
- `/help` - Show available commands

## Advanced Features

### Customizing Search

You can customize your search by:

- Specifying time ranges
- Focusing on specific domains
- Excluding certain sources

### Exporting Results

Research results can be exported in various formats:

- Markdown
- PDF
- Text

To export, click the "Export" button in the research results section.

## Tips for Effective Research

1. **Be Specific**: The more specific your research question, the better the results
2. **Use Follow-up Questions**: Refine your research with targeted follow-up questions
3. **Combine Topics**: Connect different research areas for deeper insights
4. **Save Important Sessions**: Bookmark or save important research sessions for future reference

## Troubleshooting

If you encounter issues while using the application:

1. Check your internet connection
2. Verify your API keys are still valid
3. Restart the application
4. Check the logs for error messages

For more help, please open an issue on the [GitHub repository](https://github.com/Akshay-Sisodia/deepresearch/issues).