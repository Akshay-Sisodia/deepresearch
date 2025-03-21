import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Function to check if a logger already has handlers to prevent duplicates
def has_handlers(logger):
    current = logger
    while current:
        if current.handlers:
            return True
        if not current.propagate:
            break
        current = current.parent
    return False

# Configure loggers only once using this function
def setup_loggers():
    # Reset root logger to prevent duplicate handlers
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    # Set root logger to INFO level for development
    root_logger.setLevel(logging.INFO)
    
    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create file handler with buffering
    log_file = os.path.join(logs_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(
        log_file,
        mode="a",
        encoding="utf-8",  # Explicitly use UTF-8 encoding for log files
        delay=True  # Delay file creation until first log
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler - set to INFO for development
    console_handler = logging.StreamHandler(
        stream=sys.stdout  # Use stdout for better Unicode support
    )
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create and configure specific loggers - all set to INFO for development
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    
    model_logger = logging.getLogger("model")
    model_logger.setLevel(logging.INFO)
    
    search_logger = logging.getLogger("search")
    search_logger.setLevel(logging.INFO)
    
    cache_logger = logging.getLogger("cache")
    cache_logger.setLevel(logging.INFO)
    
    session_logger = logging.getLogger("session")
    session_logger.setLevel(logging.INFO)
    
    ui_logger = logging.getLogger("ui")
    ui_logger.setLevel(logging.INFO)
    
    research_logger = logging.getLogger("research")
    research_logger.setLevel(logging.INFO)
    
    # Return the configured loggers
    return {
        "app": app_logger,
        "model": model_logger,
        "search": search_logger,
        "cache": cache_logger,
        "session": session_logger,
        "ui": ui_logger,
        "research": research_logger
    }

# Create loggers only if they don't already exist
if not hasattr(logging, "_deep_research_loggers_initialized"):
    loggers = setup_loggers()
    app_logger = loggers["app"]
    model_logger = loggers["model"]
    search_logger = loggers["search"]
    cache_logger = loggers["cache"]
    session_logger = loggers["session"]
    ui_logger = loggers["ui"]
    research_logger = loggers["research"]
    
    # Mark that we've initialized the loggers to prevent duplicate setup
    logging._deep_research_loggers_initialized = True
else:
    # Just get the existing loggers
    app_logger = logging.getLogger("app")
    model_logger = logging.getLogger("model")
    search_logger = logging.getLogger("search")
    cache_logger = logging.getLogger("cache")
    session_logger = logging.getLogger("session")
    ui_logger = logging.getLogger("ui")
    research_logger = logging.getLogger("research") 