#!/usr/bin/env python3
"""
示例代码 - 用于测试 auto-document-generator

包含各种测试用例：
- 简单函数
- 带参数的函数
- 类和方法
- 装饰器
- 多种注释风格
"""


def simple_function():
    """A simple function without parameters."""
    return "Hello, World!"


def add_numbers(a: int, b: int) -> int:
    """Add two numbers together.
    
    Args:
        a (int): First number
        b (int): Second number
    
    Returns:
        int: Sum of a and b
    
    Examples:
        ```python
        result = add_numbers(1, 2)
        print(result)  # Output: 3
        ```
    """
    return a + b


def divide_numbers(a: float, b: float) -> float:
    """Divide two numbers.
    
    Args:
        a (float): Dividend
        b (float): Divisor
    
    Returns:
        float: Result of division
    
    Raises:
        ValueError: If b is zero
    
    Examples:
        ```python
        result = divide_numbers(10.0, 2.0)
        print(result)  # Output: 5.0
        ```
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def function_with_default(name: str, greeting: str = "Hello") -> str:
    """Create a greeting message.
    
    Args:
        name (str): Name to greet
        greeting (str, optional): Greeting word. Defaults to "Hello".
    
    Returns:
        str: Greeting message
    """
    return f"{greeting}, {name}!"


def function_with_args(*args, **kwargs):
    """Function with variable arguments.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        dict: Dictionary with args and kwargs
    """
    return {
        "args": args,
        "kwargs": kwargs
    }


class Calculator:
    """A simple calculator class.
    
    This class provides basic arithmetic operations.
    
    Attributes:
        precision (int): Number of decimal places for results
    
    Examples:
        ```python
        calc = Calculator()
        result = calc.add(1, 2)
        print(result)  # Output: 3
        ```
    """
    
    def __init__(self, precision: int = 2):
        """Initialize calculator.
        
        Args:
            precision (int, optional): Decimal precision. Defaults to 2.
        """
        self.precision = precision
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers.
        
        Args:
            a (float): First number
            b (float): Second number
        
        Returns:
            float: Sum of a and b
        """
        return round(a + b, self.precision)
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a.
        
        Args:
            a (float): Minuend
            b (float): Subtrahend
        
        Returns:
            float: Difference
        """
        return round(a - b, self.precision)
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers.
        
        Args:
            a (float): First number
            b (float): Second number
        
        Returns:
            float: Product
        """
        return round(a * b, self.precision)
    
    def divide(self, a: float, b: float) -> float:
        """Divide a by b.
        
        Args:
            a (float): Dividend
            b (float): Divisor
        
        Returns:
            float: Quotient
        
        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return round(a / b, self.precision)


class Person:
    """Person class with basic information.
    
    Attributes:
        name (str): Person's name
        age (int): Person's age
    """
    
    def __init__(self, name: str, age: int):
        """Initialize person.
        
        Args:
            name (str): Name
            age (int): Age
        """
        self.name = name
        self.age = age
    
    def introduce(self) -> str:
        """Introduce the person.
        
        Returns:
            str: Introduction message
        """
        return f"My name is {self.name} and I'm {self.age} years old."
    
    @staticmethod
    def is_adult(age: int) -> bool:
        """Check if age is adult.
        
        Args:
            age (int): Age to check
        
        Returns:
            bool: True if adult, False otherwise
        """
        return age >= 18
    
    @classmethod
    def create_adult(cls, name: str):
        """Create an adult person.
        
        Args:
            name (str): Name
        
        Returns:
            Person: Adult person instance
        """
        return cls(name, 18)


# Numpy 风格 docstring
def numpy_style_function(x, y):
    """
    Calculate the sum of two numbers.
    
    Parameters
    ----------
    x : int or float
        First number
    y : int or float
        Second number
    
    Returns
    -------
    int or float
        Sum of x and y
    
    Examples
    --------
    >>> numpy_style_function(1, 2)
    3
    """
    return x + y


# Sphinx 风格 docstring
def sphinx_style_function(a, b):
    """
    Multiply two numbers.
    
    :param a: First number
    :type a: int
    :param b: Second number
    :type b: int
    :return: Product of a and b
    :rtype: int
    """
    return a * b


# 装饰器示例
@staticmethod
def decorated_static_method():
    """A decorated static method."""
    pass


@property
def decorated_property(self):
    """A decorated property."""
    return None


# 带异常处理的函数
def safe_divide(a: int, b: int) -> float:
    """Safely divide two numbers with error handling.
    
    Args:
        a (int): Dividend
        b (int): Divisor
    
    Returns:
        float: Result of division
    
    Raises:
        TypeError: If inputs are not numbers
        ValueError: If divisor is zero
    
    Notes:
        This function includes comprehensive error handling.
    
    Warnings:
        Division by zero will raise an exception.
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    
    if b == 0:
        raise ValueError("Cannot divide by zero")
    
    return a / b
