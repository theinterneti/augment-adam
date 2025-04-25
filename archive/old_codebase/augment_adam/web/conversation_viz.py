"""Conversation visualization for the Augment Adam web interface.

This module provides functionality for visualizing conversations in the Augment Adam web interface.

Version: 0.1.0
Created: 2025-04-26
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple, Callable, Union

import gradio as gr

from augment_adam.memory.working import Message
from augment_adam.core.assistant import Assistant

logger = logging.getLogger(__name__)


class ConversationVizUI:
    """UI component for visualizing conversations in the web interface."""

    def __init__(self, assistant: Optional[Assistant] = None):
        """Initialize the conversation visualization UI.

        Args:
            assistant: The assistant to use. If None, a new one will be created.
        """
        self.assistant = assistant
        self.conversation_history = []
        self.visualization_type = "timeline"

    def create_ui(self) -> Tuple[List[gr.Component], List[Callable]]:
        """Create the conversation visualization UI components.

        Returns:
            A tuple of (components, event_handlers).
        """
        # Visualization type selector
        viz_type = gr.Radio(
            label="Visualization Type",
            choices=["timeline", "tree", "stats"],
            value=self.visualization_type,
        )

        # Visualization display
        viz_display = gr.HTML(
            label="Conversation Visualization",
            value=self._get_visualization(self.visualization_type),
        )

        # Conversation statistics
        stats_display = gr.JSON(
            label="Conversation Statistics",
            value=self._get_conversation_stats(),
        )

        # Controls
        with gr.Row():
            refresh_button = gr.Button("Refresh")
            export_button = gr.Button("Export Visualization")

        # Export options
        export_format = gr.Radio(
            label="Export Format",
            choices=["HTML", "JSON", "Markdown"],
            value="HTML",
        )

        export_result = gr.File(
            label="Exported Visualization",
            interactive=False,
        )

        # Set up event handlers
        event_handlers = [
            viz_type.change(
                fn=self._change_visualization_type,
                inputs=[viz_type],
                outputs=[viz_display],
            ),
            refresh_button.click(
                fn=self._refresh_visualization,
                inputs=[viz_type],
                outputs=[viz_display, stats_display],
            ),
            export_button.click(
                fn=self._export_visualization,
                inputs=[viz_type, export_format],
                outputs=[export_result],
            ),
        ]

        components = [
            viz_type,
            viz_display,
            stats_display,
            refresh_button,
            export_button,
            export_format,
            export_result,
        ]

        return components, event_handlers

    def set_conversation_history(self, history: List[Dict[str, str]]) -> None:
        """Set the conversation history.

        Args:
            history: The conversation history.
        """
        self.conversation_history = history

    def set_assistant(self, assistant: Assistant) -> None:
        """Set the assistant.

        Args:
            assistant: The assistant to use.
        """
        self.assistant = assistant

    def _change_visualization_type(self, viz_type: str) -> str:
        """Change the visualization type.

        Args:
            viz_type: The visualization type.

        Returns:
            The updated visualization HTML.
        """
        self.visualization_type = viz_type
        return self._get_visualization(viz_type)

    def _refresh_visualization(self, viz_type: str) -> Tuple[str, Dict[str, Any]]:
        """Refresh the visualization.

        Args:
            viz_type: The visualization type.

        Returns:
            A tuple of (visualization_html, statistics).
        """
        # Update the conversation history if an assistant is available
        if self.assistant:
            self.conversation_history = []
            for message in self.assistant.get_messages():
                self.conversation_history.append({
                    "role": message.role,
                    "content": message.content,
                })

        return self._get_visualization(viz_type), self._get_conversation_stats()

    def _get_visualization(self, viz_type: str) -> str:
        """Get the visualization HTML.

        Args:
            viz_type: The visualization type.

        Returns:
            The visualization HTML.
        """
        if viz_type == "timeline":
            return self._get_timeline_visualization()
        elif viz_type == "tree":
            return self._get_tree_visualization()
        elif viz_type == "stats":
            return self._get_stats_visualization()
        else:
            return "<div>Unknown visualization type</div>"

    def _get_timeline_visualization(self) -> str:
        """Get a timeline visualization of the conversation.

        Returns:
            The timeline visualization HTML.
        """
        if not self.conversation_history:
            return "<div class='empty-viz'>No conversation history available</div>"

        html = "<div class='timeline-viz'>"

        # Add timeline header
        html += "<div class='timeline-header'>"
        html += "<div class='timeline-title'>Conversation Timeline</div>"
        html += f"<div class='timeline-subtitle'>{len(self.conversation_history)} messages</div>"
        html += "</div>"

        # Add timeline items
        html += "<div class='timeline-items'>"

        for i, message in enumerate(self.conversation_history):
            role = message["role"]
            content = message["content"]

            # Determine the CSS class based on the role
            if role == "user":
                item_class = "timeline-item-user"
                role_label = "You"
            elif role == "assistant":
                item_class = "timeline-item-assistant"
                role_label = "Augment Adam"
            elif role == "system":
                item_class = "timeline-item-system"
                role_label = "System"
            else:
                item_class = "timeline-item-unknown"
                role_label = role.capitalize()

            # Create the timeline item
            html += f"<div class='timeline-item {item_class}'>"
            html += f"<div class='timeline-item-header'>"
            html += f"<div class='timeline-item-role'>{role_label}</div>"
            html += f"<div class='timeline-item-number'>#{i+1}</div>"
            html += "</div>"
            html += f"<div class='timeline-item-content'>{content}</div>"
            html += "</div>"

        html += "</div>"  # End timeline items
        html += "</div>"  # End timeline viz

        # Add CSS styles
        html += """
        <style>
        .timeline-viz {
            font-family: Arial, sans-serif;
            max-width: 100%;
            margin: 0 auto;
        }
        .timeline-header {
            margin-bottom: 20px;
            text-align: center;
        }
        .timeline-title {
            font-size: 24px;
            font-weight: bold;
        }
        .timeline-subtitle {
            font-size: 16px;
            color: #666;
        }
        .timeline-items {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .timeline-item {
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .timeline-item-user {
            background-color: #e6f7ff;
            border-left: 5px solid #1890ff;
            margin-right: 20%;
        }
        .timeline-item-assistant {
            background-color: #f6ffed;
            border-left: 5px solid #52c41a;
            margin-left: 20%;
        }
        .timeline-item-system {
            background-color: #fff7e6;
            border-left: 5px solid #faad14;
        }
        .timeline-item-unknown {
            background-color: #f9f9f9;
            border-left: 5px solid #d9d9d9;
        }
        .timeline-item-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .timeline-item-role {
            font-weight: bold;
        }
        .timeline-item-number {
            color: #999;
        }
        .timeline-item-content {
            white-space: pre-wrap;
        }
        .empty-viz {
            text-align: center;
            padding: 50px;
            color: #999;
            font-style: italic;
        }
        </style>
        """

        return html

    def _get_tree_visualization(self) -> str:
        """Get a tree visualization of the conversation.

        Returns:
            The tree visualization HTML.
        """
        if not self.conversation_history:
            return "<div class='empty-viz'>No conversation history available</div>"

        html = "<div class='tree-viz'>"

        # Add tree header
        html += "<div class='tree-header'>"
        html += "<div class='tree-title'>Conversation Tree</div>"
        html += f"<div class='tree-subtitle'>{len(self.conversation_history)} messages</div>"
        html += "</div>"

        # Add tree structure
        html += "<div class='tree-container'>"
        html += "<ul class='tree'>"

        # Add root node
        html += "<li>"
        html += "<div class='tree-node tree-node-root'>Conversation</div>"
        html += "<ul>"

        # Group messages by role
        user_messages = [
            m for m in self.conversation_history if m["role"] == "user"]
        assistant_messages = [
            m for m in self.conversation_history if m["role"] == "assistant"]
        system_messages = [
            m for m in self.conversation_history if m["role"] == "system"]
        other_messages = [m for m in self.conversation_history if m["role"] not in [
            "user", "assistant", "system"]]

        # Add user branch
        if user_messages:
            html += "<li>"
            html += f"<div class='tree-node tree-node-user'>User ({len(user_messages)})</div>"
            html += "<ul>"
            for i, message in enumerate(user_messages):
                html += "<li>"
                html += f"<div class='tree-node tree-node-message'>{message['content'][:50]}...</div>"
                html += "</li>"
            html += "</ul>"
            html += "</li>"

        # Add assistant branch
        if assistant_messages:
            html += "<li>"
            html += f"<div class='tree-node tree-node-assistant'>Assistant ({len(assistant_messages)})</div>"
            html += "<ul>"
            for i, message in enumerate(assistant_messages):
                html += "<li>"
                html += f"<div class='tree-node tree-node-message'>{message['content'][:50]}...</div>"
                html += "</li>"
            html += "</ul>"
            html += "</li>"

        # Add system branch
        if system_messages:
            html += "<li>"
            html += f"<div class='tree-node tree-node-system'>System ({len(system_messages)})</div>"
            html += "<ul>"
            for i, message in enumerate(system_messages):
                html += "<li>"
                html += f"<div class='tree-node tree-node-message'>{message['content'][:50]}...</div>"
                html += "</li>"
            html += "</ul>"
            html += "</li>"

        # Add other branch
        if other_messages:
            html += "<li>"
            html += f"<div class='tree-node tree-node-other'>Other ({len(other_messages)})</div>"
            html += "<ul>"
            for i, message in enumerate(other_messages):
                html += "<li>"
                html += f"<div class='tree-node tree-node-message'>{message['content'][:50]}...</div>"
                html += "</li>"
            html += "</ul>"
            html += "</li>"

        html += "</ul>"  # End root node children
        html += "</li>"  # End root node
        html += "</ul>"  # End tree
        html += "</div>"  # End tree container
        html += "</div>"  # End tree viz

        # Add CSS styles
        html += """
        <style>
        .tree-viz {
            font-family: Arial, sans-serif;
            max-width: 100%;
            margin: 0 auto;
        }
        .tree-header {
            margin-bottom: 20px;
            text-align: center;
        }
        .tree-title {
            font-size: 24px;
            font-weight: bold;
        }
        .tree-subtitle {
            font-size: 16px;
            color: #666;
        }
        .tree-container {
            overflow: auto;
        }
        .tree {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .tree li {
            position: relative;
            padding-left: 30px;
            margin-bottom: 10px;
        }
        .tree li::before {
            content: '';
            position: absolute;
            top: 0;
            left: 10px;
            height: 100%;
            width: 1px;
            background-color: #ccc;
        }
        .tree li:last-child::before {
            height: 20px;
        }
        .tree li::after {
            content: '';
            position: absolute;
            top: 20px;
            left: 10px;
            width: 20px;
            height: 1px;
            background-color: #ccc;
        }
        .tree-node {
            display: inline-block;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 5px;
        }
        .tree-node-root {
            background-color: #f0f0f0;
            font-weight: bold;
        }
        .tree-node-user {
            background-color: #e6f7ff;
            border-left: 3px solid #1890ff;
        }
        .tree-node-assistant {
            background-color: #f6ffed;
            border-left: 3px solid #52c41a;
        }
        .tree-node-system {
            background-color: #fff7e6;
            border-left: 3px solid #faad14;
        }
        .tree-node-other {
            background-color: #f9f9f9;
            border-left: 3px solid #d9d9d9;
        }
        .tree-node-message {
            background-color: #f9f9f9;
            font-size: 0.9em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 300px;
        }
        .empty-viz {
            text-align: center;
            padding: 50px;
            color: #999;
            font-style: italic;
        }
        </style>
        """

        return html

    def _get_stats_visualization(self) -> str:
        """Get a statistical visualization of the conversation.

        Returns:
            The statistical visualization HTML.
        """
        if not self.conversation_history:
            return "<div class='empty-viz'>No conversation history available</div>"

        # Calculate statistics
        stats = self._get_conversation_stats()

        html = "<div class='stats-viz'>"

        # Add stats header
        html += "<div class='stats-header'>"
        html += "<div class='stats-title'>Conversation Statistics</div>"
        html += f"<div class='stats-subtitle'>{len(self.conversation_history)} messages</div>"
        html += "</div>"

        # Add stats cards
        html += "<div class='stats-cards'>"

        # Message count by role
        html += "<div class='stats-card'>"
        html += "<div class='stats-card-title'>Messages by Role</div>"
        html += "<div class='stats-card-content'>"
        html += "<div class='stats-bar-chart'>"

        # Calculate max count for scaling
        max_count = max(stats["message_counts"].values()
                        ) if stats["message_counts"] else 0

        for role, count in stats["message_counts"].items():
            # Determine the CSS class based on the role
            if role == "user":
                bar_class = "stats-bar-user"
            elif role == "assistant":
                bar_class = "stats-bar-assistant"
            elif role == "system":
                bar_class = "stats-bar-system"
            else:
                bar_class = "stats-bar-other"

            # Calculate the bar width as a percentage
            width = (count / max_count * 100) if max_count > 0 else 0

            html += f"<div class='stats-bar-item'>"
            html += f"<div class='stats-bar-label'>{role.capitalize()}</div>"
            html += f"<div class='stats-bar-container'>"
            html += f"<div class='stats-bar {bar_class}' style='width: {width}%;'></div>"
            html += f"<div class='stats-bar-value'>{count}</div>"
            html += f"</div>"
            html += f"</div>"

        html += "</div>"  # End stats bar chart
        html += "</div>"  # End stats card content
        html += "</div>"  # End stats card

        # Message length statistics
        html += "<div class='stats-card'>"
        html += "<div class='stats-card-title'>Message Length Statistics</div>"
        html += "<div class='stats-card-content'>"
        html += "<div class='stats-table'>"
        html += "<table>"
        html += "<tr><th>Role</th><th>Avg. Length</th><th>Min</th><th>Max</th></tr>"

        for role, lengths in stats["message_lengths"].items():
            if lengths:
                avg_length = sum(lengths) / len(lengths)
                min_length = min(lengths)
                max_length = max(lengths)

                html += f"<tr>"
                html += f"<td>{role.capitalize()}</td>"
                html += f"<td>{avg_length:.1f}</td>"
                html += f"<td>{min_length}</td>"
                html += f"<td>{max_length}</td>"
                html += f"</tr>"

        html += "</table>"
        html += "</div>"  # End stats table
        html += "</div>"  # End stats card content
        html += "</div>"  # End stats card

        # Response time statistics (if available)
        if stats.get("response_times"):
            html += "<div class='stats-card'>"
            html += "<div class='stats-card-title'>Response Time Statistics</div>"
            html += "<div class='stats-card-content'>"
            html += "<div class='stats-metrics'>"

            avg_time = stats["response_times"]["average"]
            min_time = stats["response_times"]["min"]
            max_time = stats["response_times"]["max"]

            html += f"<div class='stats-metric'>"
            html += f"<div class='stats-metric-value'>{avg_time:.2f}s</div>"
            html += f"<div class='stats-metric-label'>Average</div>"
            html += f"</div>"

            html += f"<div class='stats-metric'>"
            html += f"<div class='stats-metric-value'>{min_time:.2f}s</div>"
            html += f"<div class='stats-metric-label'>Minimum</div>"
            html += f"</div>"

            html += f"<div class='stats-metric'>"
            html += f"<div class='stats-metric-value'>{max_time:.2f}s</div>"
            html += f"<div class='stats-metric-label'>Maximum</div>"
            html += f"</div>"

            html += "</div>"  # End stats metrics
            html += "</div>"  # End stats card content
            html += "</div>"  # End stats card

        html += "</div>"  # End stats cards
        html += "</div>"  # End stats viz

        # Add CSS styles
        html += """
        <style>
        .stats-viz {
            font-family: Arial, sans-serif;
            max-width: 100%;
            margin: 0 auto;
        }
        .stats-header {
            margin-bottom: 20px;
            text-align: center;
        }
        .stats-title {
            font-size: 24px;
            font-weight: bold;
        }
        .stats-subtitle {
            font-size: 16px;
            color: #666;
        }
        .stats-cards {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
        }
        .stats-card {
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            padding: 20px;
            min-width: 300px;
            flex: 1;
        }
        .stats-card-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
        }
        .stats-bar-chart {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .stats-bar-item {
            display: flex;
            align-items: center;
        }
        .stats-bar-label {
            width: 100px;
            font-weight: bold;
        }
        .stats-bar-container {
            flex: 1;
            display: flex;
            align-items: center;
            height: 24px;
        }
        .stats-bar {
            height: 100%;
            border-radius: 4px;
            min-width: 2px;
        }
        .stats-bar-value {
            margin-left: 10px;
            font-weight: bold;
        }
        .stats-bar-user {
            background-color: #1890ff;
        }
        .stats-bar-assistant {
            background-color: #52c41a;
        }
        .stats-bar-system {
            background-color: #faad14;
        }
        .stats-bar-other {
            background-color: #d9d9d9;
        }
        .stats-table {
            width: 100%;
            overflow-x: auto;
        }
        .stats-table table {
            width: 100%;
            border-collapse: collapse;
        }
        .stats-table th, .stats-table td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .stats-table th {
            font-weight: bold;
            background-color: #f9f9f9;
        }
        .stats-metrics {
            display: flex;
            justify-content: space-around;
            text-align: center;
        }
        .stats-metric-value {
            font-size: 24px;
            font-weight: bold;
        }
        .stats-metric-label {
            color: #666;
            margin-top: 5px;
        }
        .empty-viz {
            text-align: center;
            padding: 50px;
            color: #999;
            font-style: italic;
        }
        </style>
        """

        return html

    def _get_conversation_stats(self) -> Dict[str, Any]:
        """Get statistics about the conversation.

        Returns:
            A dictionary of conversation statistics.
        """
        if not self.conversation_history:
            return {
                "message_counts": {},
                "message_lengths": {},
                "total_messages": 0,
            }

        # Count messages by role
        message_counts = {}
        message_lengths = {}

        for message in self.conversation_history:
            role = message["role"]
            content = message["content"]

            # Update message counts
            message_counts[role] = message_counts.get(role, 0) + 1

            # Update message lengths
            if role not in message_lengths:
                message_lengths[role] = []
            message_lengths[role].append(len(content))

        # Calculate response times (if timestamps are available)
        response_times = None
        if self.assistant and hasattr(self.assistant, "response_times"):
            times = self.assistant.response_times
            if times:
                response_times = {
                    "average": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "total": len(times),
                }

        return {
            "message_counts": message_counts,
            "message_lengths": message_lengths,
            "total_messages": len(self.conversation_history),
            "response_times": response_times,
        }

    def _export_visualization(self, viz_type: str, export_format: str) -> Optional[str]:
        """Export the visualization.

        Args:
            viz_type: The visualization type.
            export_format: The export format.

        Returns:
            The path to the exported file, or None if export failed.
        """
        try:
            # Generate the visualization content
            if export_format == "HTML":
                content = self._get_visualization(viz_type)
                filename = f"conversation_viz_{int(time.time())}.html"

                # Wrap in a complete HTML document
                content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Augment Adam Conversation Visualization</title>
                </head>
                <body>
                    {content}
                </body>
                </html>
                """

            elif export_format == "JSON":
                # Export the conversation history as JSON
                content = json.dumps({
                    "conversation": self.conversation_history,
                    "statistics": self._get_conversation_stats(),
                }, indent=2)
                filename = f"conversation_viz_{int(time.time())}.json"

            elif export_format == "Markdown":
                # Export the conversation as Markdown
                content = "# Augment Adam Conversation\n\n"

                for message in self.conversation_history:
                    role = message["role"]
                    content_text = message["content"]

                    if role == "user":
                        content += f"## User\n\n{content_text}\n\n"
                    elif role == "assistant":
                        content += f"## Assistant\n\n{content_text}\n\n"
                    elif role == "system":
                        content += f"## System\n\n{content_text}\n\n"
                    else:
                        content += f"## {role.capitalize()}\n\n{content_text}\n\n"

                # Add statistics
                content += "## Statistics\n\n"
                stats = self._get_conversation_stats()

                content += "### Message Counts\n\n"
                for role, count in stats["message_counts"].items():
                    content += f"- {role.capitalize()}: {count}\n"

                content += "\n### Message Lengths\n\n"
                content += "| Role | Avg. Length | Min | Max |\n"
                content += "|------|-------------|-----|-----|\n"

                for role, lengths in stats["message_lengths"].items():
                    if lengths:
                        avg_length = sum(lengths) / len(lengths)
                        min_length = min(lengths)
                        max_length = max(lengths)
                        content += f"| {role.capitalize()} | {avg_length:.1f} | {min_length} | {max_length} |\n"

                filename = f"conversation_viz_{int(time.time())}.md"

            else:
                return None

            # Save the content to a temporary file
            temp_path = f"/tmp/{filename}"
            with open(temp_path, "w") as f:
                f.write(content)

            return temp_path

        except Exception as e:
            logger.exception(f"Error exporting visualization: {str(e)}")
            return None


def create_visualization_tab(assistant: Optional[Assistant] = None) -> Tuple[gr.Tab, List[Callable], ConversationVizUI]:
    """Create a conversation visualization tab for the web interface.

    Args:
        assistant: The assistant to use. If None, a new one will be created.

    Returns:
        A tuple of (tab, event_handlers).
    """
    viz_ui = ConversationVizUI(assistant)

    with gr.Tab("Visualization") as tab:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## Conversation Visualization")
                gr.Markdown(
                    "Visualize and analyze your conversation with the assistant.")

                components, event_handlers = viz_ui.create_ui()

    return tab, event_handlers, viz_ui
