"""Main entry point for the context engine worker."""

import asyncio
from context_engine.worker.task_processor import main

if __name__ == "__main__":
    asyncio.run(main())
