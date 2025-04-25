"""Worker Agent Implementation.

This module provides an asynchronous worker agent implementation.
Worker agents are designed to run asynchronously and handle long-running tasks.

Version: 0.1.0
Created: 2025-04-30
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Union, Callable
import uuid

from augment_adam.models import ModelInterface
from augment_adam.ai_agent.base_agent import BaseAgent
from augment_adam.ai_agent.tools import Tool
from augment_adam.ai_agent.smc.potential import Potential

logger = logging.getLogger(__name__)


class WorkerAgent(BaseAgent):
    """Worker Agent implementation.
    
    This class provides an asynchronous worker agent implementation.
    Worker agents are designed to run asynchronously and handle long-running tasks.
    
    Attributes:
        name: Name of the agent
        description: Description of the agent
        model: The language model to use
        system_prompt: System prompt for the agent
        tools: List of tools available to the agent
        potentials: List of potentials for controlled generation
        output_format: Format for agent output (e.g., "text", "json")
        strict_output: Whether to enforce strict output format
        inference_settings: Settings for model inference
        task_queue: Queue of tasks to process
        results: Dictionary of task results
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        model: ModelInterface,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Tool]] = None,
        potentials: Optional[List[Potential]] = None,
        output_format: str = "text",
        strict_output: bool = False,
        max_concurrent_tasks: int = 5,
        **kwargs
    ):
        """Initialize the Worker Agent.
        
        Args:
            name: Name of the agent
            description: Description of the agent
            model: The language model to use
            system_prompt: System prompt for the agent
            tools: List of tools available to the agent
            potentials: List of potentials for controlled generation
            output_format: Format for agent output (e.g., "text", "json")
            strict_output: Whether to enforce strict output format
            max_concurrent_tasks: Maximum number of concurrent tasks
            **kwargs: Additional parameters for the agent
        """
        super().__init__(
            name=name,
            description=description,
            model=model,
            system_prompt=system_prompt,
            tools=tools,
            potentials=potentials,
            output_format=output_format,
            strict_output=strict_output,
            **kwargs
        )
        
        # Initialize task queue and results
        self.task_queue = asyncio.Queue()
        self.results = {}
        self.max_concurrent_tasks = max_concurrent_tasks
        self.running_tasks = set()
        self.is_running = False
        
        logger.info(f"Initialized Worker Agent '{name}' with max {max_concurrent_tasks} concurrent tasks")
    
    async def start(self) -> None:
        """Start the worker agent."""
        if self.is_running:
            logger.warning(f"Worker Agent '{self.name}' is already running")
            return
        
        self.is_running = True
        logger.info(f"Starting Worker Agent '{self.name}'")
        
        # Start task processor
        asyncio.create_task(self._process_tasks())
    
    async def stop(self) -> None:
        """Stop the worker agent."""
        if not self.is_running:
            logger.warning(f"Worker Agent '{self.name}' is not running")
            return
        
        self.is_running = False
        logger.info(f"Stopping Worker Agent '{self.name}'")
        
        # Wait for running tasks to complete
        if self.running_tasks:
            logger.info(f"Waiting for {len(self.running_tasks)} tasks to complete")
            await asyncio.gather(*self.running_tasks, return_exceptions=True)
    
    async def _process_tasks(self) -> None:
        """Process tasks from the queue."""
        while self.is_running:
            try:
                # Get task from queue
                task_id, user_input, context = await self.task_queue.get()
                
                # Create task
                task = asyncio.create_task(self._process_task(task_id, user_input, context))
                self.running_tasks.add(task)
                task.add_done_callback(lambda t: self.running_tasks.remove(t))
                
                # Wait if we have too many tasks
                while len(self.running_tasks) >= self.max_concurrent_tasks:
                    await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing tasks: {e}")
                await asyncio.sleep(1)
    
    async def _process_task(self, task_id: str, user_input: str, context: Optional[Dict[str, Any]]) -> None:
        """Process a single task.
        
        Args:
            task_id: ID of the task
            user_input: User input
            context: Additional context
        """
        try:
            # Update task status
            self.results[task_id]["status"] = "processing"
            self.results[task_id]["start_time"] = time.time()
            
            # Process input
            result = await self.process_async(user_input, context)
            
            # Update task result
            self.results[task_id]["status"] = "completed"
            self.results[task_id]["result"] = result
            self.results[task_id]["end_time"] = time.time()
            self.results[task_id]["processing_time"] = time.time() - self.results[task_id]["start_time"]
            
            logger.info(f"Completed task {task_id}")
        except Exception as e:
            # Update task status on error
            self.results[task_id]["status"] = "error"
            self.results[task_id]["error"] = str(e)
            self.results[task_id]["end_time"] = time.time()
            
            logger.error(f"Error processing task {task_id}: {e}")
    
    async def submit_task(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Submit a task to the worker agent.
        
        Args:
            user_input: User input
            context: Additional context
            
        Returns:
            Task ID
        """
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task result
        self.results[task_id] = {
            "status": "queued",
            "queue_time": time.time(),
            "user_input": user_input
        }
        
        # Add task to queue
        await self.task_queue.put((task_id, user_input, context))
        
        logger.info(f"Submitted task {task_id}")
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task status
        """
        if task_id not in self.results:
            return {"status": "not_found"}
        
        return self.results[task_id]
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all tasks.
        
        Returns:
            Dictionary mapping task IDs to task statuses
        """
        return self.results.copy()
    
    def clear_completed_tasks(self) -> int:
        """Clear completed tasks.
        
        Returns:
            Number of tasks cleared
        """
        completed_tasks = [
            task_id for task_id, task in self.results.items()
            if task["status"] in ["completed", "error"]
        ]
        
        for task_id in completed_tasks:
            del self.results[task_id]
        
        logger.info(f"Cleared {len(completed_tasks)} completed tasks")
        return len(completed_tasks)
    
    async def process_async(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process user input and generate a response asynchronously.
        
        Args:
            user_input: User input
            context: Additional context
            
        Returns:
            Response data
        """
        # Format prompt
        prompt = self._format_prompt(user_input)
        
        # Generate response
        start_time = time.time()
        
        # Prepare generation parameters
        params = {
            "prompt": prompt,
            "max_tokens": self.inference_settings["max_tokens"],
            "temperature": self.inference_settings["temperature"],
            "top_p": self.inference_settings["top_p"],
            "top_k": self.inference_settings["top_k"],
            "use_monte_carlo": self.inference_settings["use_monte_carlo"],
            "monte_carlo_particles": self.inference_settings["monte_carlo_particles"],
            "monte_carlo_potentials": self.potentials
        }
        
        # Generate response (run in thread pool to avoid blocking)
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(
            None, lambda: self.model.generate(**params)
        )
        
        # Parse output
        result = self._parse_output(output)
        
        # Execute tool calls if any
        tool_calls = result.get("tool_calls", [])
        if tool_calls:
            tool_results = await self._execute_tool_calls_async(tool_calls)
            result["tool_results"] = tool_results
            
            # If tools were called, generate a follow-up response
            if tool_results:
                # Format tool results
                tool_results_text = self._format_tool_results(tool_results)
                
                # Generate follow-up response
                follow_up_prompt = f"{prompt}\n\n{output}\n\n{tool_results_text}\n\nBased on the tool results, provide a final response:"
                
                follow_up_output = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate(
                        prompt=follow_up_prompt,
                        max_tokens=self.inference_settings["max_tokens"],
                        temperature=self.inference_settings["temperature"],
                        top_p=self.inference_settings["top_p"],
                        top_k=self.inference_settings["top_k"]
                    )
                )
                
                # Parse follow-up output
                follow_up_result = self._parse_output(follow_up_output)
                
                # Update result with follow-up response
                result["follow_up_response"] = follow_up_result.get("response")
                if "parsed_response" in follow_up_result:
                    result["follow_up_parsed_response"] = follow_up_result["parsed_response"]
        
        # Add processing time
        result["processing_time"] = time.time() - start_time
        
        return result
