"""Web interface for the Dukat assistant.

This module provides a web interface for the Dukat assistant using Gradio.

Version: 0.1.0
Created: 2025-04-23
"""

import asyncio
import logging
import os
import time
from typing import Dict, List, Optional, Tuple, Any, Callable

import gradio as gr

from dukat.core.assistant import Assistant
from dukat.core.model_manager import ModelManager
from dukat.memory.working import Message
from dukat.config import Config
from dukat.web.plugin_manager import create_plugin_tab

logger = logging.getLogger(__name__)


class WebInterface:
    """Web interface for the Dukat assistant."""

    def __init__(
        self,
        assistant: Optional[Assistant] = None,
        model_name: str = "llama3:8b",
        theme: str = "soft",
        title: str = "Dukat Assistant",
        description: str = "An open-source AI assistant focused on personal automation.",
        version: str = "0.1.0",
    ):
        """Initialize the web interface.

        Args:
            assistant: The assistant to use. If None, a new one will be created.
            model_name: The name of the model to use.
            theme: The theme to use for the interface.
            title: The title of the interface.
            description: The description of the interface.
            version: The version of the interface.
        """
        self.assistant = assistant or Assistant(model_name=model_name)
        self.model_name = model_name
        self.theme = theme
        self.title = title
        self.description = description
        self.version = version

        self.interface = None
        self.conversation_history = []
        self.config = Config()

    def _format_message(self, message: Dict[str, str]) -> str:
        """Format a message for display.

        Args:
            message: The message to format.

        Returns:
            The formatted message.
        """
        role = message["role"]
        content = message["content"]

        if role == "user":
            return f"<div class='user-message'><strong>You:</strong> {content}</div>"
        elif role == "assistant":
            return f"<div class='assistant-message'><strong>Dukat:</strong> {content}</div>"
        elif role == "system":
            return f"<div class='system-message'><strong>System:</strong> {content}</div>"
        else:
            return f"<div class='unknown-message'><strong>{role.capitalize()}:</strong> {content}</div>"

    def _format_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Format a conversation for display.

        Args:
            messages: The messages in the conversation.

        Returns:
            The formatted conversation.
        """
        formatted_messages = [self._format_message(
            message) for message in messages]
        return "<div class='conversation'>" + "".join(formatted_messages) + "</div>"

    def _user_input_callback(
        self,
        message: str,
        history: List[Tuple[str, str]],
        system_prompt: str,
    ) -> Tuple[str, List[Tuple[str, str]], str]:
        """Callback for user input.

        Args:
            message: The user's message.
            history: The conversation history.
            system_prompt: The system prompt.

        Returns:
            A tuple of (empty string, updated history, formatted conversation).
        """
        if not message.strip():
            return "", history, self._format_conversation(self.conversation_history)

        # Add the user message to the conversation history
        user_message = {"role": "user", "content": message}
        self.conversation_history.append(user_message)

        # Add the message to the assistant's working memory
        self.assistant.add_message(Message(role="user", content=message))

        # Generate a response
        response = self.assistant.generate_response(
            system_prompt=system_prompt)

        # Add the assistant's response to the conversation history
        assistant_message = {"role": "assistant", "content": response}
        self.conversation_history.append(assistant_message)

        # Update the history for Gradio
        history.append((message, response))

        # Return the updated state
        return "", history, self._format_conversation(self.conversation_history)

    def _clear_conversation_callback(
        self,
        history: List[Tuple[str, str]],
    ) -> Tuple[List[Tuple[str, str]], str]:
        """Callback for clearing the conversation.

        Args:
            history: The conversation history.

        Returns:
            A tuple of (empty history, empty conversation).
        """
        self.conversation_history = []
        self.assistant.clear_messages()
        return [], self._format_conversation(self.conversation_history)

    def _save_conversation_callback(
        self,
        save_path: str,
    ) -> str:
        """Callback for saving the conversation.

        Args:
            save_path: The path to save the conversation to.

        Returns:
            A message indicating the result.
        """
        if not self.conversation_history:
            return "No conversation to save."

        if not save_path:
            save_path = f"conversation_{int(time.time())}.json"

        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(
                os.path.abspath(save_path)), exist_ok=True)

            # Save the conversation
            self.assistant.save_conversation(save_path)

            return f"Conversation saved to {save_path}"
        except Exception as e:
            logger.exception(f"Error saving conversation: {str(e)}")
            return f"Error saving conversation: {str(e)}"

    def _load_conversation_callback(
        self,
        load_path: str,
    ) -> Tuple[List[Tuple[str, str]], str]:
        """Callback for loading a conversation.

        Args:
            load_path: The path to load the conversation from.

        Returns:
            A tuple of (updated history, formatted conversation).
        """
        if not load_path:
            return [], "No file selected."

        try:
            # Load the conversation
            self.assistant.load_conversation(load_path)

            # Update the conversation history
            self.conversation_history = []
            for message in self.assistant.get_messages():
                self.conversation_history.append({
                    "role": message.role,
                    "content": message.content,
                })

            # Update the history for Gradio
            history = []
            for i in range(0, len(self.conversation_history), 2):
                if i + 1 < len(self.conversation_history):
                    user_message = self.conversation_history[i]["content"]
                    assistant_message = self.conversation_history[i + 1]["content"]
                    history.append((user_message, assistant_message))

            return history, self._format_conversation(self.conversation_history)
        except Exception as e:
            logger.exception(f"Error loading conversation: {str(e)}")
            return [], f"Error loading conversation: {str(e)}"

    def _change_model_callback(
        self,
        model_name: str,
    ) -> str:
        """Callback for changing the model.

        Args:
            model_name: The name of the model to use.

        Returns:
            A message indicating the result.
        """
        try:
            # Create a new model manager
            model_manager = ModelManager(model_name=model_name)

            # Update the assistant's model manager
            self.assistant.model_manager = model_manager
            self.model_name = model_name

            return f"Model changed to {model_name}"
        except Exception as e:
            logger.exception(f"Error changing model: {str(e)}")
            return f"Error changing model: {str(e)}"

    def _get_available_models_callback(self) -> List[str]:
        """Callback for getting available models.

        Returns:
            A list of available models.
        """
        try:
            # Get available models
            models = self.assistant.model_manager.get_available_models()
            return models
        except Exception as e:
            logger.exception(f"Error getting available models: {str(e)}")
            return ["llama3:8b"]  # Default model

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

            # Create tabs for different sections
            with gr.Tabs() as tabs:
                # Chat tab
                with gr.Tab("Chat") as chat_tab:
                    with gr.Row():
                        with gr.Column(scale=3):
                            # Chat interface
                            chatbot = gr.Chatbot(
                                label="Conversation",
                                height=500,
                            )

                            # Conversation display
                            conversation_display = gr.HTML(
                                label="Formatted Conversation",
                                value=self._format_conversation(
                                    self.conversation_history),
                            )

                            # User input
                            with gr.Row():
                                user_input = gr.Textbox(
                                    label="Your message",
                                    placeholder="Type your message here...",
                                    lines=3,
                                )
                                send_button = gr.Button(
                                    "Send", variant="primary")

                        with gr.Column(scale=1):
                            # System prompt
                            system_prompt = gr.Textbox(
                                label="System Prompt",
                                placeholder="Instructions for the assistant...",
                                lines=3,
                                value=self.config.get(
                                    "system_prompt", "You are Dukat, an open-source AI assistant focused on personal automation."),
                            )

                            # Model selection
                            model_dropdown = gr.Dropdown(
                                label="Model",
                                choices=self._get_available_models_callback(),
                                value=self.model_name,
                            )
                            change_model_button = gr.Button("Change Model")
                            model_status = gr.Textbox(
                                label="Model Status",
                                value=f"Using model: {self.model_name}",
                            )

                            # Conversation management
                            with gr.Row():
                                clear_button = gr.Button("Clear Conversation")
                                refresh_button = gr.Button("Refresh Models")

                            # Save/load conversation
                            save_path = gr.Textbox(
                                label="Save Path",
                                placeholder="Path to save conversation...",
                                value="",
                            )
                            save_button = gr.Button("Save Conversation")
                            save_status = gr.Textbox(
                                label="Save Status",
                                value="",
                            )

                            load_path = gr.Textbox(
                                label="Load Path",
                                placeholder="Path to load conversation...",
                                value="",
                            )
                            load_button = gr.Button("Load Conversation")

                # Plugin tab
                plugin_tab, plugin_event_handlers = create_plugin_tab()

            # Set up event handlers for chat tab
            send_button.click(
                fn=self._user_input_callback,
                inputs=[user_input, chatbot, system_prompt],
                outputs=[user_input, chatbot, conversation_display],
            )

            user_input.submit(
                fn=self._user_input_callback,
                inputs=[user_input, chatbot, system_prompt],
                outputs=[user_input, chatbot, conversation_display],
            )

            clear_button.click(
                fn=self._clear_conversation_callback,
                inputs=[chatbot],
                outputs=[chatbot, conversation_display],
            )

            save_button.click(
                fn=self._save_conversation_callback,
                inputs=[save_path],
                outputs=[save_status],
            )

            load_button.click(
                fn=self._load_conversation_callback,
                inputs=[load_path],
                outputs=[chatbot, conversation_display],
            )

            change_model_button.click(
                fn=self._change_model_callback,
                inputs=[model_dropdown],
                outputs=[model_status],
            )

            refresh_button.click(
                fn=lambda: gr.update(
                    choices=self._get_available_models_callback()),
                inputs=[],
                outputs=[model_dropdown],
            )

            self.interface = interface
            return interface

    def launch(
        self,
        host: str = "127.0.0.1",
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

    def _get_css(self) -> str:
        """Get the CSS for the interface.

        Returns:
            The CSS.
        """
        return """
        .conversation {
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding: 10px;
            border-radius: 5px;
            background-color: #f9f9f9;
            max-height: 500px;
            overflow-y: auto;
        }

        .user-message {
            align-self: flex-end;
            background-color: #dcf8c6;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .assistant-message {
            align-self: flex-start;
            background-color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .system-message {
            align-self: center;
            background-color: #f0f0f0;
            padding: 5px 10px;
            border-radius: 10px;
            max-width: 80%;
            font-style: italic;
            color: #666;
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
    title: str = "Dukat Assistant",
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
    host: str = "127.0.0.1",
    port: int = 7860,
    share: bool = False,
    debug: bool = False,
    model_name: str = "llama3:8b",
    theme: str = "soft",
    title: str = "Dukat Assistant",
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
