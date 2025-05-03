"""Web interface for the Augment Adam assistant.

This module provides a web interface for the Augment Adam assistant using Gradio.

Version: 0.1.0
Created: 2023-05-01
"""

import logging
import os
import time
from typing import Dict, List, Optional, Tuple, Any, Callable

import gradio as gr

from augment_adam.context_engine import ContextEngine
from augment_adam.memory.core import MemoryManager
from augment_adam.ai_agent import create_agent

logger = logging.getLogger(__name__)


class WebInterface:
    """Web interface for the Augment Adam assistant."""

    def __init__(
        self,
        model_name: str = "llama3:8b",
        theme: str = "soft",
        title: str = "Augment Adam Assistant",
        description: str = "An open-source AI assistant focused on personal automation.",
        version: str = "0.1.0",
    ):
        """Initialize the web interface.

        Args:
            model_name: The name of the model to use.
            theme: The theme to use for the interface.
            title: The title of the interface.
            description: The description of the interface.
            version: The version of the interface.
        """
        self.model_name = model_name
        self.theme = theme
        self.title = title
        self.description = description
        self.version = version
        self.interface = None
        
        # Initialize components
        self.context_engine = ContextEngine()
        self.memory_manager = MemoryManager()
        self.agent = create_agent(model_name=model_name)
        
        # Chat history
        self.chat_history = []

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface.

        Returns:
            The Gradio interface.
        """
        with gr.Blocks(
            title=f"{self.title} v{self.version}",
            theme=self.theme,
            css=self._get_css(),
        ) as interface:
            gr.Markdown(f"# {self.title} v{self.version}")
            gr.Markdown(self.description)

            with gr.Tab("Chat"):
                chatbot = gr.Chatbot(
                    [],
                    elem_id="chatbot",
                    bubble_full_width=False,
                    height=600,
                    show_copy_button=True,
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        show_label=False,
                        placeholder="Type a message...",
                        container=False,
                        scale=9,
                    )
                    submit_btn = gr.Button("Send", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("Clear Chat")
                    
                # Set up event handlers
                submit_btn.click(
                    self._chat,
                    inputs=[msg, chatbot],
                    outputs=[msg, chatbot],
                )
                msg.submit(
                    self._chat,
                    inputs=[msg, chatbot],
                    outputs=[msg, chatbot],
                )
                clear_btn.click(
                    lambda: ([], []),
                    outputs=[chatbot, msg],
                )

            with gr.Tab("Context Engine"):
                gr.Markdown("## Context Engine")
                with gr.Row():
                    with gr.Column():
                        context_input = gr.Textbox(
                            label="Query",
                            placeholder="Enter a query to search the context...",
                            lines=3,
                        )
                        context_submit = gr.Button("Search")
                    
                    with gr.Column():
                        context_output = gr.Markdown(label="Results")
                
                context_submit.click(
                    self._search_context,
                    inputs=[context_input],
                    outputs=[context_output],
                )

            with gr.Tab("Memory"):
                gr.Markdown("## Memory System")
                with gr.Row():
                    with gr.Column():
                        memory_input = gr.Textbox(
                            label="Memory",
                            placeholder="Enter a memory to store...",
                            lines=3,
                        )
                        memory_submit = gr.Button("Store")
                    
                    with gr.Column():
                        memory_query = gr.Textbox(
                            label="Query",
                            placeholder="Search memories...",
                            lines=1,
                        )
                        memory_search = gr.Button("Search")
                        memory_results = gr.Markdown(label="Results")
                
                memory_submit.click(
                    self._store_memory,
                    inputs=[memory_input],
                    outputs=[memory_results],
                )
                memory_search.click(
                    self._search_memory,
                    inputs=[memory_query],
                    outputs=[memory_results],
                )

        self.interface = interface
        return interface

    def launch(
        self,
        host: str = "0.0.0.0",
        port: int = 7860,
        share: bool = False,
        debug: bool = False,
        **kwargs,
    ) -> None:
        """Launch the web interface.

        Args:
            host: The host to bind to.
            port: The port to bind to.
            share: Whether to create a public link.
            debug: Whether to enable debug mode.
            **kwargs: Additional arguments to pass to Gradio.
        """
        if self.interface is None:
            self.create_interface()

        self.interface.launch(
            server_name=host,
            server_port=port,
            share=share,
            debug=debug,
            **kwargs,
        )
    
    def _chat(self, message: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
        """Process a chat message.
        
        Args:
            message: The user message.
            history: The chat history.
            
        Returns:
            A tuple of (empty message, updated history).
        """
        if not message.strip():
            return "", history
        
        # Add user message to history
        history.append((message, None))
        
        try:
            # Process the message with the agent
            start_time = time.time()
            
            # Get context
            context = self.context_engine.search(message)
            
            # Get relevant memories
            memories = self.memory_manager.search(message)
            
            # Process with agent
            response = self.agent.process(
                message, 
                context=context,
                memories=memories
            )
            
            # Store the interaction in memory
            self.memory_manager.store({
                "user_message": message,
                "assistant_response": response,
                "timestamp": time.time()
            })
            
            # Log processing time
            processing_time = time.time() - start_time
            logger.info(f"Processed message in {processing_time:.2f}s")
            
            # Update history with assistant response
            history[-1] = (message, response)
            
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            history[-1] = (message, f"Error: {str(e)}")
        
        return "", history
    
    def _search_context(self, query: str) -> str:
        """Search the context engine.
        
        Args:
            query: The query to search for.
            
        Returns:
            The search results as markdown.
        """
        try:
            results = self.context_engine.search(query)
            if not results:
                return "No results found."
            
            # Format results as markdown
            markdown = "### Search Results\n\n"
            for i, result in enumerate(results):
                markdown += f"**Result {i+1}**\n\n"
                markdown += f"```\n{result}\n```\n\n"
            
            return markdown
        except Exception as e:
            logger.exception(f"Error searching context: {e}")
            return f"Error: {str(e)}"
    
    def _store_memory(self, memory: str) -> str:
        """Store a memory.
        
        Args:
            memory: The memory to store.
            
        Returns:
            A confirmation message.
        """
        try:
            if not memory.strip():
                return "Memory cannot be empty."
            
            self.memory_manager.store({
                "content": memory,
                "timestamp": time.time()
            })
            
            return "Memory stored successfully."
        except Exception as e:
            logger.exception(f"Error storing memory: {e}")
            return f"Error: {str(e)}"
    
    def _search_memory(self, query: str) -> str:
        """Search memories.
        
        Args:
            query: The query to search for.
            
        Returns:
            The search results as markdown.
        """
        try:
            results = self.memory_manager.search(query)
            if not results:
                return "No memories found."
            
            # Format results as markdown
            markdown = "### Memory Search Results\n\n"
            for i, result in enumerate(results):
                markdown += f"**Memory {i+1}**\n\n"
                markdown += f"Content: {result.get('content', 'No content')}\n\n"
                
                # Format timestamp
                timestamp = result.get('timestamp')
                if timestamp:
                    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
                    markdown += f"Time: {time_str}\n\n"
                
                markdown += "---\n\n"
            
            return markdown
        except Exception as e:
            logger.exception(f"Error searching memories: {e}")
            return f"Error: {str(e)}"
    
    def _get_css(self) -> str:
        """Get the CSS for the interface.
        
        Returns:
            The CSS as a string.
        """
        return """
        .gradio-container {
            max-width: 1200px !important;
        }
        
        #chatbot {
            height: 600px;
            overflow-y: auto;
        }
        
        .user-message {
            background-color: #e6f7ff;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            max-width: 80%;
            align-self: flex-end;
        }
        
        .assistant-message {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            max-width: 80%;
            align-self: flex-start;
        }
        
        .unknown-message {
            align-self: center;
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
        }
        """


def create_web_interface(
    model_name: str = "llama3:8b",
    theme: str = "soft",
    title: str = "Augment Adam Assistant",
    description: str = "An open-source AI assistant focused on personal automation.",
    version: str = "0.1.0",
) -> WebInterface:
    """Create a web interface.

    Args:
        model_name: The name of the model to use.
        theme: The theme to use for the interface.
        title: The title of the interface.
        description: The description of the interface.
        version: The version of the interface.

    Returns:
        The web interface.
    """
    return WebInterface(
        model_name=model_name,
        theme=theme,
        title=title,
        description=description,
        version=version,
    )


def launch_web_interface(
    host: str = "0.0.0.0",
    port: int = 7860,
    share: bool = False,
    debug: bool = False,
    model_name: str = "llama3:8b",
    theme: str = "soft",
    title: str = "Augment Adam Assistant",
    description: str = "An open-source AI assistant focused on personal automation.",
    version: str = "0.1.0",
    **kwargs,
) -> None:
    """Launch a web interface.

    Args:
        host: The host to bind to.
        port: The port to bind to.
        share: Whether to create a public link.
        debug: Whether to enable debug mode.
        model_name: The name of the model to use.
        theme: The theme to use for the interface.
        title: The title of the interface.
        description: The description of the interface.
        version: The version of the interface.
        **kwargs: Additional arguments to pass to Gradio.
    """
    interface = create_web_interface(
        model_name=model_name,
        theme=theme,
        title=title,
        description=description,
        version=version,
    )

    interface.launch(
        host=host,
        port=port,
        share=share,
        debug=debug,
        **kwargs,
    )
