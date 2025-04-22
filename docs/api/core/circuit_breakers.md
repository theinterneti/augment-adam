# Circuit Breakers

The circuit breaker pattern prevents cascading failures by failing fast when a dependency is unavailable.

## Overview

The circuit breaker pattern provides the following capabilities:

- Detect failures in external dependencies
- Fail fast when a dependency is unavailable
- Automatically recover when a dependency becomes available again
- Track failure and success statistics

## Components

### CircuitBreaker

The main class for implementing the circuit breaker pattern.

```python
from dukat.core.circuit_breaker import CircuitBreaker, CircuitBreakerState

# Create a circuit breaker
breaker = CircuitBreaker(
    name="api_service",
    failure_threshold=5,
    timeout_seconds=60.0,
    half_open_max_calls=1,
    excluded_exceptions={ValueError},
)

# Use the circuit breaker
if breaker.allow_request():
    try:
        # Make the request
        result = await make_api_request()
        
        # Record success
        breaker.success()
        
        return result
    except Exception as e:
        # Record failure
        breaker.failure(e)
        
        # Re-raise the exception
        raise
else:
    # Circuit is open, fail fast
    raise CircuitBreakerError("Circuit breaker is open")
```

### CircuitBreakerState

Enum representing the state of a circuit breaker.

```python
from dukat.core.circuit_breaker import CircuitBreakerState

# Circuit breaker states
CircuitBreakerState.CLOSED    # Normal operation, requests pass through
CircuitBreakerState.OPEN      # Circuit is open, requests fail fast
CircuitBreakerState.HALF_OPEN # Testing if the service is back online
```

### CircuitBreakerError

Exception raised when a circuit breaker is open.

```python
from dukat.core.errors import CircuitBreakerError

try:
    # Make a request through a circuit breaker
    result = await make_request_with_circuit_breaker()
except CircuitBreakerError as e:
    # Handle the circuit breaker error
    logger.error(f"Circuit breaker error: {e}")
```

### Decorator

The circuit breaker pattern can also be applied as a decorator.

```python
from dukat.core.circuit_breaker import circuit_breaker

@circuit_breaker(
    name="api_service",
    failure_threshold=5,
    timeout_seconds=60.0,
    excluded_exceptions={ValueError},
)
async def make_api_request():
    # Make the request
    return await api_client.get("/endpoint")
```

## Integration with AsyncAssistant

The AsyncAssistant class provides circuit breakers for common dependencies:

```python
from dukat.core.async_assistant import get_async_assistant

# Create an async assistant
assistant = await get_async_assistant(
    model_name="llama3:8b",
)

# Get circuit breaker statistics
stats = await assistant.get_queue_stats()
circuit_breakers = stats["circuit_breakers"]

# Check circuit breaker state
model_breaker = circuit_breakers["model"]
if model_breaker["state"] == "open":
    logger.warning("Model circuit breaker is open")
```

## Examples

See the `examples/async_processing.py` file for a complete example of using circuit breakers.

## Best Practices

1. **Failure Threshold**: Set an appropriate failure threshold based on the dependency's reliability.
2. **Timeout**: Set an appropriate timeout based on how long it typically takes for the dependency to recover.
3. **Excluded Exceptions**: Exclude exceptions that should not count as failures.
4. **Monitoring**: Monitor circuit breaker states to detect issues early.
5. **Fallbacks**: Implement fallbacks for when a circuit breaker is open.
