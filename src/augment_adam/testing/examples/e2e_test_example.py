"""
End-to-end test example.

This module provides an example of an end-to-end test.
"""

import unittest
import json
from typing import Dict, List, Any, Optional
from unittest.mock import MagicMock, patch

from augment_adam.testing.utils.case import TestCase
from augment_adam.utils.tagging import tag, TagCategory


class ApiClient:
    """
    A simple API client class for demonstration purposes.
    """
    
    def __init__(self, base_url: str) -> None:
        """
        Initialize the API client.
        
        Args:
            base_url: The base URL for the API.
        """
        self.base_url = base_url
    
    def get(self, path: str) -> Dict[str, Any]:
        """
        Make a GET request to the API.
        
        Args:
            path: The path to request.
            
        Returns:
            The response from the API.
            
        Raises:
            Exception: If the request fails.
        """
        import requests
        
        response = requests.get(f"{self.base_url}{path}")
        
        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}")
        
        return response.json()
    
    def post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request to the API.
        
        Args:
            path: The path to request.
            data: The data to send.
            
        Returns:
            The response from the API.
            
        Raises:
            Exception: If the request fails.
        """
        import requests
        
        response = requests.post(f"{self.base_url}{path}", json=data)
        
        if response.status_code != 200 and response.status_code != 201:
            raise Exception(f"Request failed with status code {response.status_code}")
        
        return response.json()
    
    def put(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a PUT request to the API.
        
        Args:
            path: The path to request.
            data: The data to send.
            
        Returns:
            The response from the API.
            
        Raises:
            Exception: If the request fails.
        """
        import requests
        
        response = requests.put(f"{self.base_url}{path}", json=data)
        
        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}")
        
        return response.json()
    
    def delete(self, path: str) -> None:
        """
        Make a DELETE request to the API.
        
        Args:
            path: The path to request.
            
        Raises:
            Exception: If the request fails.
        """
        import requests
        
        response = requests.delete(f"{self.base_url}{path}")
        
        if response.status_code != 200 and response.status_code != 204:
            raise Exception(f"Request failed with status code {response.status_code}")


class UserApiClient:
    """
    A simple user API client class for demonstration purposes.
    """
    
    def __init__(self, api_client: ApiClient) -> None:
        """
        Initialize the user API client.
        
        Args:
            api_client: The API client to use.
        """
        self.api_client = api_client
    
    def create_user(self, name: str, email: str) -> Dict[str, Any]:
        """
        Create a user.
        
        Args:
            name: The user name.
            email: The user email.
            
        Returns:
            The created user.
        """
        return self.api_client.post("/users", {
            "name": name,
            "email": email,
        })
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user.
        
        Args:
            user_id: The user ID.
            
        Returns:
            The user.
        """
        return self.api_client.get(f"/users/{user_id}")
    
    def update_user(self, user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a user.
        
        Args:
            user_id: The user ID.
            name: The new user name, or None to keep the current name.
            email: The new user email, or None to keep the current email.
            
        Returns:
            The updated user.
        """
        data = {}
        
        if name is not None:
            data["name"] = name
        
        if email is not None:
            data["email"] = email
        
        return self.api_client.put(f"/users/{user_id}", data)
    
    def delete_user(self, user_id: str) -> None:
        """
        Delete a user.
        
        Args:
            user_id: The user ID.
        """
        self.api_client.delete(f"/users/{user_id}")
    
    def list_users(self) -> List[Dict[str, Any]]:
        """
        List all users.
        
        Returns:
            A list of users.
        """
        return self.api_client.get("/users")


@tag("testing.examples")
class UserApiClientTest(TestCase):
    """
    End-to-end test for the UserApiClient class.
    """
    
    @patch("requests.get")
    @patch("requests.post")
    @patch("requests.put")
    @patch("requests.delete")
    def setUp(self, mock_delete: MagicMock, mock_put: MagicMock, mock_post: MagicMock, mock_get: MagicMock) -> None:
        """
        Set up the test case.
        
        Args:
            mock_delete: Mock for requests.delete.
            mock_put: Mock for requests.put.
            mock_post: Mock for requests.post.
            mock_get: Mock for requests.get.
        """
        self.mock_delete = mock_delete
        self.mock_put = mock_put
        self.mock_post = mock_post
        self.mock_get = mock_get
        
        self.api_client = ApiClient("https://api.example.com")
        self.user_api_client = UserApiClient(self.api_client)
    
    def test_create_user(self) -> None:
        """Test the create_user method."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "1",
            "name": "John Doe",
            "email": "john@example.com",
        }
        
        self.mock_post.return_value = mock_response
        
        # Create a user
        user = self.user_api_client.create_user("John Doe", "john@example.com")
        
        # Check the user
        self.assertEqual(user["id"], "1")
        self.assertEqual(user["name"], "John Doe")
        self.assertEqual(user["email"], "john@example.com")
        
        # Check the request
        self.mock_post.assert_called_once_with(
            "https://api.example.com/users",
            json={
                "name": "John Doe",
                "email": "john@example.com",
            },
        )
    
    def test_get_user(self) -> None:
        """Test the get_user method."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "1",
            "name": "John Doe",
            "email": "john@example.com",
        }
        
        self.mock_get.return_value = mock_response
        
        # Get a user
        user = self.user_api_client.get_user("1")
        
        # Check the user
        self.assertEqual(user["id"], "1")
        self.assertEqual(user["name"], "John Doe")
        self.assertEqual(user["email"], "john@example.com")
        
        # Check the request
        self.mock_get.assert_called_once_with(
            "https://api.example.com/users/1",
        )
    
    def test_update_user(self) -> None:
        """Test the update_user method."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "1",
            "name": "Jane Doe",
            "email": "john@example.com",
        }
        
        self.mock_put.return_value = mock_response
        
        # Update a user
        user = self.user_api_client.update_user("1", name="Jane Doe")
        
        # Check the user
        self.assertEqual(user["id"], "1")
        self.assertEqual(user["name"], "Jane Doe")
        self.assertEqual(user["email"], "john@example.com")
        
        # Check the request
        self.mock_put.assert_called_once_with(
            "https://api.example.com/users/1",
            json={
                "name": "Jane Doe",
            },
        )
    
    def test_delete_user(self) -> None:
        """Test the delete_user method."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 204
        
        self.mock_delete.return_value = mock_response
        
        # Delete a user
        self.user_api_client.delete_user("1")
        
        # Check the request
        self.mock_delete.assert_called_once_with(
            "https://api.example.com/users/1",
        )
    
    def test_list_users(self) -> None:
        """Test the list_users method."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "1",
                "name": "John Doe",
                "email": "john@example.com",
            },
            {
                "id": "2",
                "name": "Jane Doe",
                "email": "jane@example.com",
            },
        ]
        
        self.mock_get.return_value = mock_response
        
        # List users
        users = self.user_api_client.list_users()
        
        # Check the users
        self.assertEqual(len(users), 2)
        
        self.assertEqual(users[0]["id"], "1")
        self.assertEqual(users[0]["name"], "John Doe")
        self.assertEqual(users[0]["email"], "john@example.com")
        
        self.assertEqual(users[1]["id"], "2")
        self.assertEqual(users[1]["name"], "Jane Doe")
        self.assertEqual(users[1]["email"], "jane@example.com")
        
        # Check the request
        self.mock_get.assert_called_once_with(
            "https://api.example.com/users",
        )


if __name__ == "__main__":
    unittest.main()
