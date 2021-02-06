import unittest

# From command line: 
"""
python -m unittest discover -v
"""

# From test.py:
if __name__ == "__main__":    
    loader = unittest.TestLoader()
    start_dir = "decorate/tests"
    suite = loader.discover(start_dir)

    runner = unittest.TextTestRunner()
    runner.run(suite)
