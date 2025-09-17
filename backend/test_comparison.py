import unittest
import sys
import os

# Add the parent directory to the path so we can import the main module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import compare_texts, extract_with_regex

class TestComparison(unittest.TestCase):
    
    def test_basic_text_comparison(self):
        """Test basic text comparison without regex"""
        text1 = "line1\nline2\nline3"
        text2 = "line1\nline2 modified\nline3"
        
        result = compare_texts(text1, text2)
        
        # Check that we have differences
        self.assertTrue(len(result['diff']) > 0)
        self.assertEqual(result['stats']['lines_added'], 1)
        self.assertEqual(result['stats']['lines_removed'], 1)
    
    def test_regex_extraction(self):
        """Test regex pattern extraction"""
        text = "key1=value1\nkey2=value2\nother line"
        pattern = r'(\w+)=(\w+)'
        
        matches = extract_with_regex(text, pattern)
        
        # Should find 2 matches
        self.assertEqual(len(matches), 2)
        self.assertIn(('key1', 'value1'), matches)
        self.assertIn(('key2', 'value2'), matches)
    
    def test_comparison_with_regex(self):
        """Test comparison with regex extraction"""
        text1 = "key1=value1\nkey2=value2\nother line"
        text2 = "key1=value1\nkey2=value2_modified\nother line"
        pattern = r'(\w+)=(\w+)'
        
        result = compare_texts(text1, text2, regex_pattern=pattern)
        
        # Check that we have differences
        self.assertTrue(len(result['diff']) > 0)
    
    def test_filter_pattern(self):
        """Test filtering with regex pattern"""
        text1 = "key1=value1\nignore_this_line\nkey2=value2"
        text2 = "key1=value1\nignore_this_line\nkey2=value2_modified"
        filter_pattern = r'ignore_this_line'
        
        result = compare_texts(text1, text2, filter_pattern=filter_pattern)
        
        # Check that filtered lines are not in the diff
        diff_text = ''.join(result['diff'])
        self.assertNotIn('ignore_this_line', diff_text)
    
    def test_invalid_regex(self):
        """Test handling of invalid regex patterns"""
        text = "sample text"
        invalid_pattern = r'['  # Invalid regex
        
        with self.assertRaises(Exception):
            extract_with_regex(text, invalid_pattern)

if __name__ == '__main__':
    unittest.main()