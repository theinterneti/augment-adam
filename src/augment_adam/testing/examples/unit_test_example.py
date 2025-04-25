"""
Unit test example.

This module provides an example of a unit test.
"""

import unittest
from typing import Dict, List, Any

from augment_adam.testing.utils.case import TestCase
from augment_adam.utils.tagging import tag, TagCategory


class Calculator:
    """
    A simple calculator class for demonstration purposes.
    """
    
    def add(self, a: float, b: float) -> float:
        """
        Add two numbers.
        
        Args:
            a: The first number.
            b: The second number.
            
        Returns:
            The sum of the two numbers.
        """
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """
        Subtract one number from another.
        
        Args:
            a: The first number.
            b: The second number.
            
        Returns:
            The difference between the two numbers.
        """
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers.
        
        Args:
            a: The first number.
            b: The second number.
            
        Returns:
            The product of the two numbers.
        """
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """
        Divide one number by another.
        
        Args:
            a: The first number.
            b: The second number.
            
        Returns:
            The quotient of the two numbers.
            
        Raises:
            ZeroDivisionError: If the second number is zero.
        """
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        
        return a / b


@tag("testing.examples")
class CalculatorTest(TestCase):
    """
    Unit test for the Calculator class.
    """
    
    def setUp(self) -> None:
        """Set up the test case."""
        self.calculator = Calculator()
    
    def test_add(self) -> None:
        """Test the add method."""
        self.assertEqual(self.calculator.add(1, 2), 3)
        self.assertEqual(self.calculator.add(-1, 1), 0)
        self.assertEqual(self.calculator.add(0, 0), 0)
    
    def test_subtract(self) -> None:
        """Test the subtract method."""
        self.assertEqual(self.calculator.subtract(1, 2), -1)
        self.assertEqual(self.calculator.subtract(-1, 1), -2)
        self.assertEqual(self.calculator.subtract(0, 0), 0)
    
    def test_multiply(self) -> None:
        """Test the multiply method."""
        self.assertEqual(self.calculator.multiply(1, 2), 2)
        self.assertEqual(self.calculator.multiply(-1, 1), -1)
        self.assertEqual(self.calculator.multiply(0, 0), 0)
    
    def test_divide(self) -> None:
        """Test the divide method."""
        self.assertEqual(self.calculator.divide(1, 2), 0.5)
        self.assertEqual(self.calculator.divide(-1, 1), -1)
        self.assertEqual(self.calculator.divide(0, 1), 0)
    
    def test_divide_by_zero(self) -> None:
        """Test the divide method with a zero divisor."""
        with self.assertRaises(ZeroDivisionError):
            self.calculator.divide(1, 0)


if __name__ == "__main__":
    unittest.main()
