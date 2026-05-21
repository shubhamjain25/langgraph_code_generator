# App Generator Orchestrator - Usage Guide

## Simple Start

```python
from main import AppGeneratorOrchestrator

# Create orchestrator
orchestrator = AppGeneratorOrchestrator(thread_id="user_123")

# Run workflow
result = orchestrator.run(user_input="Build a todo app")

# Check result
if result["status"] == "completed":
    print("Success:", result["output"])
else:
    print("Failed:", result["error"])
```

## Initialization Parameters

```python
AppGeneratorOrchestrator(
    thread_id="session_001",      # Unique session ID
    recursion_limit=20,           # Max iterations (default: 20)
    enable_recovery=True,         # Auto-recover from checkpoints (default: True)
    debug=False                   # Show debug logs (default: False)
)
```

## Main Methods

### `run(user_input=None)` 
Executes the workflow. Handles checkpoint recovery automatically.

```python
result = orchestrator.run(user_input="Build a weather app")
# Returns: {"status": "completed"|"failed", "output": {...}, "error": "...", "timestamp": "..."}
```

### `get_status()`
Check current status without executing.

```python
status = orchestrator.get_status()
# Returns: {"status": "idle|running|completed|failed", "next_node": "...", "error": "..."}
```

### `approve()`
Approve current state and continue (for human review).

```python
result = orchestrator.approve()
```

### `rewind_with_feedback(feedback)`
Rewind and re-architect with user feedback.

```python
result = orchestrator.rewind_with_feedback("Use React instead of Vue")
```

### `reset()`
Reset the orchestrator.

```python
orchestrator.reset()
```

## Return Values

All execution methods return a dictionary:

```python
{
    "status": "completed",  # or "failed"
    "output": {...},        # Workflow result (if successful)
    "error": "...",         # Error message (if failed)
    "timestamp": "2026-05-22T10:30:45.123456"
}
```

## Use Cases

### Basic Execution
```python
orchestrator = AppGeneratorOrchestrator()
result = orchestrator.run()
```

### With Specific Thread ID
```python
orchestrator = AppGeneratorOrchestrator(thread_id="user_abc_123")
result = orchestrator.run(user_input="Build a chat app")
```

### Human Review Approval
```python
orchestrator = AppGeneratorOrchestrator()
orchestrator.run()
# ... user reviews output ...
result = orchestrator.approve()  # Continue with approval
```

### Rewind with Feedback
```python
orchestrator = AppGeneratorOrchestrator()
orchestrator.run()
# ... user wants changes ...
result = orchestrator.rewind_with_feedback("Make it mobile-first")
```

### With External Orchestrator (Airflow Example)
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from main import AppGeneratorOrchestrator

def run_generator(**context):
    orchestrator = AppGeneratorOrchestrator(
        thread_id=context["task_instance"].task_id
    )
    result = orchestrator.run(user_input="Build an API")
    
    if result["status"] != "completed":
        raise Exception(result["error"])
    
    return result["output"]

dag = DAG("app_generator")
task = PythonOperator(python_callable=run_generator, dag=dag)
```

### Status Monitoring
```python
orchestrator = AppGeneratorOrchestrator()
status = orchestrator.get_status()
print(f"Current status: {status['status']}")
print(f"Next node: {status['next_node']}")
```

## Error Handling

```python
orchestrator = AppGeneratorOrchestrator()
result = orchestrator.run()

if result["status"] == "failed":
    print(f"Error: {result['error']}")
    # Implement retry logic or notify user
```

## Production Tips

1. **Use unique thread IDs** - Each session should have a unique identifier
2. **Enable recovery** - Keep `enable_recovery=True` for production
3. **Handle errors** - Always check result["status"] before using output
4. **Monitor status** - Use `get_status()` periodically for health checks
5. **Debug mode** - Set `debug=False` in production

## Quick Reference

| Task | Code |
|------|------|
| Create | `AppGeneratorOrchestrator(thread_id="id")` |
| Run | `orchestrator.run(user_input="...")` |
| Status | `orchestrator.get_status()` |
| Approve | `orchestrator.approve()` |
| Feedback | `orchestrator.rewind_with_feedback("...")` |
| Reset | `orchestrator.reset()` |

