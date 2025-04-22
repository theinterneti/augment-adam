# Error Handling in Dukat

This document describes the error handling framework in Dukat, including custom exceptions, error classification, and resilience patterns.

## Overview

Dukat implements a comprehensive error handling framework that provides:

1. **Custom exceptions** for different error categories
2. **Error classification** to categorize errors by their nature
3. **Error wrapping** to preserve context and original errors
4. **Resilience patterns** like retry and circuit breaker
5. **Structured logging** for better debugging

## Error Categories

Errors in Dukat are categorized into the following types:

| Category | Description |
|----------|-------------|
| `UNKNOWN` | Default category for unclassified errors |
| `SYSTEM` | System-level errors (OS, hardware, etc.) |
| `NETWORK` | Network-related errors (connectivity, DNS, etc.) |
| `TIMEOUT` | Timeout errors |
| `RESOURCE` | Resource-related errors (memory, disk, etc.) |
| `DATABASE` | Database-related errors |
| `API` | API-related errors |
| `MODEL` | Model-related errors (LLM, embedding, etc.) |
| `PLUGIN` | Plugin-related errors |
| `VALIDATION` | Validation errors |
| `AUTHENTICATION` | Authentication errors |
| `AUTHORIZATION` | Authorization errors |
| `NOT_FOUND` | Resource not found errors |

## Custom Exceptions

Dukat provides a hierarchy of custom exceptions that extend from the base `DukatError` class:

```python
from dukat.core.errors import DukatError, ModelError, NetworkError

# Raising a custom error
raise ModelError("Failed to load model", original_error=original_exception)

# Catching custom errors
try:
    # Some operation
    pass
except ModelError as e:
    # Handle model errors
    pass
except NetworkError as e:
    # Handle network errors
    pass
except DukatError as e:
    # Handle all other Dukat errors
    pass
```

## Error Wrapping

Dukat provides utilities to wrap standard Python exceptions into Dukat's custom exceptions:

```python
from dukat.core.errors import wrap_error

try:
    # Some operation
    pass
except Exception as e:
    # Wrap the error
    error = wrap_error(
        e,
        message="Failed to perform operation",
        category=None,  # Auto-classify the error
        details={"operation": "load_model"},
    )
    
    # Re-raise the wrapped error
    raise error
```

## Resilience Patterns

### Retry Decorator

The retry decorator automatically retries a function when it fails with specified exceptions:

```python
from dukat.core.errors import retry

@retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
def fetch_data():
    # This function will be retried up to 3 times if it fails
    pass
```

### Circuit Breaker

The circuit breaker pattern prevents cascading failures by stopping operations when they consistently fail:

```python
from dukat.core.errors import CircuitBreaker

# Create a circuit breaker
circuit = CircuitBreaker(
    name="api_calls",
    failure_threshold=5,
    recovery_timeout=60.0,
)

# Use the circuit breaker as a decorator
@circuit
def call_api():
    # This function will be protected by the circuit breaker
    pass

# Or use it directly
try:
    result = circuit.call(some_function, *args, **kwargs)
except CircuitBreakerError:
    # Handle the case when the circuit is open
    pass
```

## Structured Logging

Dukat provides utilities for structured logging of errors:

```python
from dukat.core.errors import log_error

try:
    # Some operation
    pass
except Exception as e:
    # Log the error with context
    log_error(
        e,
        logger=logger,
        level=logging.ERROR,
        include_traceback=True,
        context={
            "operation": "load_model",
            "model_name": model_name,
        },
    )
```

## Best Practices

1. **Use custom exceptions**: Use Dukat's custom exceptions instead of standard Python exceptions.
2. **Wrap external exceptions**: Wrap exceptions from external libraries using `wrap_error`.
3. **Add context**: Always add context to errors to make debugging easier.
4. **Use resilience patterns**: Use retry and circuit breaker patterns for operations that might fail transiently.
5. **Log errors properly**: Use `log_error` to log errors with proper context.

## Example: Model Manager

The model manager in Dukat uses the error handling framework to provide robust error handling:

```python
from dukat.core.errors import (
    ModelError, NetworkError, TimeoutError, ResourceError,
    wrap_error, log_error, retry, CircuitBreaker
)

class ModelManager:
    # Create a circuit breaker for model generation
    _generate_circuit = CircuitBreaker(
        name="model_generation",
        failure_threshold=5,
        recovery_timeout=60.0,
    )
    
    @retry(max_attempts=3, delay=2.0, backoff_factor=2.0)
    def _load_model(self, model_name, ollama_host, api_key):
        try:
            # Load the model
            return load_model(model_name, ollama_host, api_key)
        except Exception as e:
            # Wrap the exception
            error = wrap_error(
                e,
                message=f"Failed to load model {model_name}",
                category=None,  # Auto-classify the error
                details={
                    "model_name": model_name,
                    "ollama_host": ollama_host,
                },
            )
            
            # Log the error
            log_error(error, logger=logger)
            
            # Re-raise the wrapped error
            raise error
    
    @retry(max_attempts=2, delay=1.0, backoff_factor=2.0)
    @_generate_circuit
    def generate_response(self, prompt, **kwargs):
        try:
            # Generate a response
            return generate(prompt, **kwargs)
        except Exception as e:
            # Handle the error
            # ...
```

## Testing Error Handling

Dukat provides utilities for testing error handling:

```python
from dukat.core.errors import DukatError, ModelError

def test_error_handling():
    # Test that errors are properly wrapped
    with pytest.raises(ModelError):
        # Operation that should raise a ModelError
        pass
    
    # Test that the retry decorator works
    mock_function = MagicMock(side_effect=[Exception, Exception, "success"])
    result = retry_function(mock_function)
    assert result == "success"
    assert mock_function.call_count == 3
    
    # Test that the circuit breaker works
    circuit = CircuitBreaker(name="test", failure_threshold=2)
    mock_function = MagicMock(side_effect=Exception)
    
    # First call should raise the original exception
    with pytest.raises(Exception):
        circuit.call(mock_function)
    
    # Second call should raise the original exception
    with pytest.raises(Exception):
        circuit.call(mock_function)
    
    # Third call should raise CircuitBreakerError
    with pytest.raises(CircuitBreakerError):
        circuit.call(mock_function)
```

## Conclusion

Dukat's error handling framework provides a robust foundation for building reliable applications. By using custom exceptions, error classification, and resilience patterns, Dukat can handle errors gracefully and provide a better user experience.
