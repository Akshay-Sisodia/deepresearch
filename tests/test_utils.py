"""
Tests for utility functions.
"""
import unittest
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import logger

class TestLogger(unittest.TestCase):
    """Test cases for the logger module."""
    
    def test_logger_initialization(self):
        """Test that the logger can be initialized."""
        from utils.logger import app_logger
        self.assertIsNotNone(app_logger)

if __name__ == '__main__':
    unittest.main() 