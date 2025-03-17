"""
Script to download the Geist Mono font locally for the application.
"""

import os
import requests
import zipfile
import io
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('font_downloader')

def download_geist_mono():
    """Download Geist Mono font and save it to the .streamlit/fonts directory."""
    fonts_dir = os.path.join('.streamlit', 'fonts')
    os.makedirs(fonts_dir, exist_ok=True)
    
    font_url = "https://github.com/vercel/geist-font/releases/download/1.1.0/GeistMono-VF.zip"
    
    try:
        logger.info("Downloading Geist Mono font...")
        response = requests.get(font_url)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(fonts_dir)
        
        logger.info(f"Geist Mono font downloaded and extracted to {fonts_dir}")
        create_local_font_css(fonts_dir)
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading font: {e}")
        return False
    except zipfile.BadZipFile:
        logger.error("Downloaded file is not a valid zip file")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def create_local_font_css(fonts_dir):
    """Create a CSS file to use the local font."""
    css_content = """
@font-face {
    font-family: 'Geist Mono';
    src: url('fonts/GeistMono-Regular.woff2') format('woff2'),
         url('fonts/GeistMono-Regular.woff') format('woff');
    font-weight: normal;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'Geist Mono';
    src: url('fonts/GeistMono-Medium.woff2') format('woff2'),
         url('fonts/GeistMono-Medium.woff') format('woff');
    font-weight: 500;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'Geist Mono';
    src: url('fonts/GeistMono-SemiBold.woff2') format('woff2'),
         url('fonts/GeistMono-SemiBold.woff') format('woff');
    font-weight: 600;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'Geist Mono';
    src: url('fonts/GeistMono-Bold.woff2') format('woff2'),
         url('fonts/GeistMono-Bold.woff') format('woff');
    font-weight: bold;
    font-style: normal;
    font-display: swap;
}
"""
    
    css_path = os.path.join('.streamlit', 'local_fonts.css')
    try:
        with open(css_path, 'w') as f:
            f.write(css_content)
        logger.info(f"Local font CSS created at {css_path}")
    except Exception as e:
        logger.error(f"Error creating CSS file: {e}")

if __name__ == "__main__":
    download_geist_mono() 