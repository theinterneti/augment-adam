"""Web server for Augment Adam.

This module provides a FastAPI server that serves the Augment Adam web interface.

Version: 0.1.0
Created: 2023-05-01
"""

import logging
import os
import argparse
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from augment_adam.web.interface import WebInterface, create_web_interface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Augment Adam Web Server",
    description="Web server for Augment Adam",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global web interface instance
web_interface = None


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint that redirects to the Gradio interface."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Augment Adam</title>
        <meta http-equiv="refresh" content="0;url=/ui" />
    </head>
    <body>
        <p>Redirecting to the Augment Adam interface...</p>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/info")
async def get_info():
    """Get information about the server."""
    return {
        "name": "Augment Adam Web Server",
        "version": "0.1.0",
        "description": "Web server for Augment Adam",
        "ui_path": "/ui"
    }


def create_app(
    model_name: str = "llama3:8b",
    theme: str = "soft",
    title: str = "Augment Adam Assistant",
    description: str = "An open-source AI assistant focused on personal automation.",
    version: str = "0.1.0",
) -> FastAPI:
    """Create the FastAPI app with the web interface.
    
    Args:
        model_name: The name of the model to use.
        theme: The theme to use for the interface.
        title: The title of the interface.
        description: The description of the interface.
        version: The version of the interface.
        
    Returns:
        The FastAPI app.
    """
    global web_interface
    
    # Create the web interface
    web_interface = create_web_interface(
        model_name=model_name,
        theme=theme,
        title=title,
        description=description,
        version=version,
    )
    
    # Create the interface
    interface = web_interface.create_interface()
    
    # Mount the Gradio app
    app.mount("/ui", interface)
    
    return app


def start_server(
    host: str = "0.0.0.0",
    port: int = 8080,
    model_name: str = "llama3:8b",
    theme: str = "soft",
    title: str = "Augment Adam Assistant",
    description: str = "An open-source AI assistant focused on personal automation.",
    version: str = "0.1.0",
):
    """Start the web server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        model_name: The name of the model to use.
        theme: The theme to use for the interface.
        title: The title of the interface.
        description: The description of the interface.
        version: The version of the interface.
    """
    # Create the app
    create_app(
        model_name=model_name,
        theme=theme,
        title=title,
        description=description,
        version=version,
    )
    
    # Start the server
    logger.info(f"Starting web server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


def main():
    """Main entry point for the web server."""
    parser = argparse.ArgumentParser(description="Augment Adam Web Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--model", default="llama3:8b", help="Model to use")
    parser.add_argument("--theme", default="soft", help="Theme to use")
    parser.add_argument("--title", default="Augment Adam Assistant", help="Title of the interface")
    parser.add_argument("--description", default="An open-source AI assistant focused on personal automation.", help="Description of the interface")
    parser.add_argument("--version", default="0.1.0", help="Version of the interface")
    
    args = parser.parse_args()
    
    start_server(
        host=args.host,
        port=args.port,
        model_name=args.model,
        theme=args.theme,
        title=args.title,
        description=args.description,
        version=args.version,
    )


if __name__ == "__main__":
    main()
