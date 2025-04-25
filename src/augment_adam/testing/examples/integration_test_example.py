"""
Integration test example.

This module provides an example of an integration test.
"""

import unittest
from typing import Dict, List, Any, Optional

from augment_adam.testing.utils.case import TestCase
from augment_adam.utils.tagging import tag, TagCategory


class Database:
    """
    A simple database class for demonstration purposes.
    """
    
    def __init__(self) -> None:
        """Initialize the database."""
        self.data: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the database.
        
        Args:
            key: The key to set.
            value: The value to set.
        """
        self.data[key] = value
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a value from the database.
        
        Args:
            key: The key to get.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The value for the key, or the default value if the key doesn't exist.
        """
        return self.data.get(key, default)
    
    def delete(self, key: str) -> None:
        """
        Delete a value from the database.
        
        Args:
            key: The key to delete.
        """
        if key in self.data:
            del self.data[key]
    
    def clear(self) -> None:
        """Clear the database."""
        self.data.clear()


class UserService:
    """
    A simple user service class for demonstration purposes.
    """
    
    def __init__(self, database: Database) -> None:
        """
        Initialize the user service.
        
        Args:
            database: The database to use.
        """
        self.database = database
    
    def create_user(self, user_id: str, name: str, email: str) -> Dict[str, Any]:
        """
        Create a user.
        
        Args:
            user_id: The user ID.
            name: The user name.
            email: The user email.
            
        Returns:
            The created user.
        """
        user = {
            "id": user_id,
            "name": name,
            "email": email,
        }
        
        self.database.set(f"user:{user_id}", user)
        
        return user
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user.
        
        Args:
            user_id: The user ID.
            
        Returns:
            The user, or None if the user doesn't exist.
        """
        return self.database.get(f"user:{user_id}")
    
    def update_user(self, user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update a user.
        
        Args:
            user_id: The user ID.
            name: The new user name, or None to keep the current name.
            email: The new user email, or None to keep the current email.
            
        Returns:
            The updated user, or None if the user doesn't exist.
        """
        user = self.get_user(user_id)
        
        if user is None:
            return None
        
        if name is not None:
            user["name"] = name
        
        if email is not None:
            user["email"] = email
        
        self.database.set(f"user:{user_id}", user)
        
        return user
    
    def delete_user(self, user_id: str) -> None:
        """
        Delete a user.
        
        Args:
            user_id: The user ID.
        """
        self.database.delete(f"user:{user_id}")


@tag("testing.examples")
class UserServiceTest(TestCase):
    """
    Integration test for the UserService class.
    """
    
    def setUp(self) -> None:
        """Set up the test case."""
        self.database = Database()
        self.user_service = UserService(self.database)
    
    def tearDown(self) -> None:
        """Tear down the test case."""
        self.database.clear()
    
    def test_create_user(self) -> None:
        """Test the create_user method."""
        user = self.user_service.create_user("1", "John Doe", "john@example.com")
        
        self.assertEqual(user["id"], "1")
        self.assertEqual(user["name"], "John Doe")
        self.assertEqual(user["email"], "john@example.com")
        
        # Check that the user was stored in the database
        stored_user = self.database.get("user:1")
        
        self.assertEqual(stored_user["id"], "1")
        self.assertEqual(stored_user["name"], "John Doe")
        self.assertEqual(stored_user["email"], "john@example.com")
    
    def test_get_user(self) -> None:
        """Test the get_user method."""
        # Create a user
        self.user_service.create_user("1", "John Doe", "john@example.com")
        
        # Get the user
        user = self.user_service.get_user("1")
        
        self.assertEqual(user["id"], "1")
        self.assertEqual(user["name"], "John Doe")
        self.assertEqual(user["email"], "john@example.com")
        
        # Get a non-existent user
        user = self.user_service.get_user("2")
        
        self.assertIsNone(user)
    
    def test_update_user(self) -> None:
        """Test the update_user method."""
        # Create a user
        self.user_service.create_user("1", "John Doe", "john@example.com")
        
        # Update the user
        user = self.user_service.update_user("1", name="Jane Doe")
        
        self.assertEqual(user["id"], "1")
        self.assertEqual(user["name"], "Jane Doe")
        self.assertEqual(user["email"], "john@example.com")
        
        # Check that the user was updated in the database
        stored_user = self.database.get("user:1")
        
        self.assertEqual(stored_user["id"], "1")
        self.assertEqual(stored_user["name"], "Jane Doe")
        self.assertEqual(stored_user["email"], "john@example.com")
        
        # Update a non-existent user
        user = self.user_service.update_user("2", name="Jane Doe")
        
        self.assertIsNone(user)
    
    def test_delete_user(self) -> None:
        """Test the delete_user method."""
        # Create a user
        self.user_service.create_user("1", "John Doe", "john@example.com")
        
        # Delete the user
        self.user_service.delete_user("1")
        
        # Check that the user was deleted from the database
        stored_user = self.database.get("user:1")
        
        self.assertIsNone(stored_user)
        
        # Delete a non-existent user
        self.user_service.delete_user("2")


if __name__ == "__main__":
    unittest.main()
