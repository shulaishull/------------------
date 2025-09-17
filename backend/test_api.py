import unittest
import sys
import os
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import the main module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
    
    def test_login_endpoint(self):
        """Test the login endpoint with valid credentials"""
        # First, we need to ensure the default user exists
        # The default user 'admin' with password 'admin' should be created on init
        
        response = self.client.post("/auth/login?username=admin&password=admin")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
    
    def test_login_with_invalid_credentials(self):
        """Test the login endpoint with invalid credentials"""
        response = self.client.post("/auth/login?username=invalid&password=invalid")
        
        self.assertEqual(response.status_code, 401)
    
    def test_upload_file(self):
        """Test file upload endpoint"""
        # Create a simple test file
        test_content = "This is a test file content"
        
        response = self.client.post("/auth/login?username=admin&password=admin")
        
        self.assertEqual(response.status_code, 200)
        token = response.json()["access_token"]
        
        # Test uploading a text file
        files = {"file": ("test.txt", test_content, "text/plain")}
        response = self.client.post(
            "/upload",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("content", response.json())
        self.assertEqual(response.json()["content"], test_content)

if __name__ == '__main__':
    unittest.main()