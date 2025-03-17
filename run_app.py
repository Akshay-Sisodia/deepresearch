"""
Script to run the application with the font download.
"""

import os
import subprocess
import sys
import logging

# Set up basic logging if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('app_runner')

def main():
    """Run the application with the font download."""
    # Check if the fonts directory exists
    fonts_dir = os.path.join('.streamlit', 'fonts')
    if not os.path.exists(fonts_dir) or not os.listdir(fonts_dir):
        logger.info("Fonts not found. Downloading...")
        try:
            # Run the download_fonts.py script
            result = subprocess.run(
                [sys.executable, 'download_fonts.py'], 
                check=True, 
                capture_output=True, 
                text=True
            )
            logger.info("Font download completed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error downloading fonts: {e}")
            logger.error(f"STDOUT: {e.stdout if hasattr(e, 'stdout') else 'N/A'}")
            logger.error(f"STDERR: {e.stderr if hasattr(e, 'stderr') else 'N/A'}")
    
    # Run the Streamlit app
    logger.info("Starting the application...")
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'])
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main() 