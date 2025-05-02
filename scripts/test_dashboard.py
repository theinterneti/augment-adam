#!/usr/bin/env python3
"""
Test Dashboard.

This module provides a simple dashboard for viewing test results.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

import aiohttp
from aiohttp import web
import jinja2

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logger = logging.getLogger("test_dashboard")


class TestDashboard:
    """Simple dashboard for viewing test results."""

    def __init__(
        self,
        report_dir: str = "reports/tests",
        template_dir: str = "templates/dashboard",
        host: str = "localhost",
        port: int = 8080,
    ):
        """Initialize the test dashboard.

        Args:
            report_dir: Directory containing test reports
            template_dir: Directory containing dashboard templates
            host: Host to bind the dashboard server
            port: Port to bind the dashboard server
        """
        self.report_dir = report_dir
        self.template_dir = template_dir
        self.host = host
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )

    def setup_routes(self):
        """Set up the dashboard routes."""
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/api/summary", self.handle_summary)
        self.app.router.add_get("/api/results", self.handle_results)
        self.app.router.add_get("/api/result/{result_id}", self.handle_result)
        self.app.router.add_static("/static", self.template_dir + "/static")

    async def handle_index(self, request):
        """Handle the index page request.

        Args:
            request: HTTP request

        Returns:
            HTTP response
        """
        template = self.jinja_env.get_template("index.html")
        summary = await self.get_summary()
        results = await self.get_results()
        html = template.render(summary=summary, results=results)
        return web.Response(text=html, content_type="text/html")

    async def handle_summary(self, request):
        """Handle the summary API request.

        Args:
            request: HTTP request

        Returns:
            HTTP response
        """
        summary = await self.get_summary()
        return web.json_response(summary)

    async def handle_results(self, request):
        """Handle the results API request.

        Args:
            request: HTTP request

        Returns:
            HTTP response
        """
        results = await self.get_results()
        return web.json_response(results)

    async def handle_result(self, request):
        """Handle the result API request.

        Args:
            request: HTTP request

        Returns:
            HTTP response
        """
        result_id = request.match_info["result_id"]
        result = await self.get_result(result_id)
        if result:
            return web.json_response(result)
        return web.Response(status=404, text="Result not found")

    async def get_summary(self) -> Dict[str, Any]:
        """Get the test summary.

        Returns:
            Summary dictionary
        """
        summary_file = os.path.join(self.report_dir, "summary.json")
        if os.path.exists(summary_file):
            try:
                with open(summary_file, "r") as f:
                    summary = json.load(f)
                return summary
            except Exception as e:
                logger.error(f"Error reading summary file: {e}", exc_info=True)
        return {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "last_updated": time.time(),
        }

    async def get_results(self) -> List[Dict[str, Any]]:
        """Get all test results.

        Returns:
            List of test result dictionaries
        """
        results = []
        try:
            for file in os.listdir(self.report_dir):
                if file.endswith(".json") and file != "summary.json":
                    result_file = os.path.join(self.report_dir, file)
                    try:
                        with open(result_file, "r") as f:
                            result = json.load(f)
                        result["id"] = file.replace(".json", "")
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error reading result file {file}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error reading results directory: {e}", exc_info=True)
        return sorted(results, key=lambda x: x.get("timestamp", 0), reverse=True)

    async def get_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific test result.

        Args:
            result_id: Result ID

        Returns:
            Test result dictionary
        """
        result_file = os.path.join(self.report_dir, f"{result_id}.json")
        if os.path.exists(result_file):
            try:
                with open(result_file, "r") as f:
                    result = json.load(f)
                result["id"] = result_id
                return result
            except Exception as e:
                logger.error(f"Error reading result file {result_id}: {e}", exc_info=True)
        return None

    async def start(self):
        """Start the dashboard server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info(f"Dashboard server started at http://{self.host}:{self.port}")
        return runner

    @staticmethod
    async def create_template_files(template_dir: str):
        """Create the dashboard template files.

        Args:
            template_dir: Directory to save the templates
        """
        os.makedirs(template_dir, exist_ok=True)
        os.makedirs(os.path.join(template_dir, "static"), exist_ok=True)

        # Create the index.html template
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Dashboard</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <header>
        <h1>Test Dashboard</h1>
    </header>
    <main>
        <section class="summary">
            <h2>Summary</h2>
            <div class="summary-stats">
                <div class="stat">
                    <span class="stat-value">{{ summary.total }}</span>
                    <span class="stat-label">Total</span>
                </div>
                <div class="stat passed">
                    <span class="stat-value">{{ summary.passed }}</span>
                    <span class="stat-label">Passed</span>
                </div>
                <div class="stat failed">
                    <span class="stat-value">{{ summary.failed }}</span>
                    <span class="stat-label">Failed</span>
                </div>
                <div class="stat skipped">
                    <span class="stat-value">{{ summary.skipped }}</span>
                    <span class="stat-label">Skipped</span>
                </div>
            </div>
            <div class="last-updated">
                Last updated: {{ summary.last_updated | timestamp_to_datetime }}
            </div>
        </section>
        <section class="results">
            <h2>Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Test</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    {% for result in results %}
                    <tr class="{{ 'passed' if result.success else 'failed' }}">
                        <td>{{ result.test_file }}</td>
                        <td>{{ 'Passed' if result.success else 'Failed' }}</td>
                        <td>{{ result.duration | format_duration }}</td>
                        <td>{{ result.timestamp | timestamp_to_datetime }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </section>
    </main>
    <footer>
        <p>Augment Adam Test Dashboard</p>
    </footer>
    <script src="/static/script.js"></script>
</body>
</html>
"""

        # Create the style.css file
        style_css = """body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}

header {
    background-color: #333;
    color: white;
    padding: 1rem;
    text-align: center;
}

main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
}

.summary {
    background-color: white;
    border-radius: 5px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.summary-stats {
    display: flex;
    justify-content: space-around;
    margin: 1rem 0;
}

.stat {
    text-align: center;
    padding: 1rem;
    border-radius: 5px;
    background-color: #f0f0f0;
    min-width: 100px;
}

.stat-value {
    font-size: 2rem;
    font-weight: bold;
    display: block;
}

.stat-label {
    font-size: 0.9rem;
    color: #666;
}

.passed {
    background-color: #dff0d8;
    color: #3c763d;
}

.failed {
    background-color: #f2dede;
    color: #a94442;
}

.skipped {
    background-color: #fcf8e3;
    color: #8a6d3b;
}

.last-updated {
    text-align: right;
    font-size: 0.8rem;
    color: #666;
}

.results {
    background-color: white;
    border-radius: 5px;
    padding: 1rem;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
}

th, td {
    padding: 0.5rem;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    background-color: #f5f5f5;
    font-weight: bold;
}

tr.passed td {
    background-color: #dff0d8;
}

tr.failed td {
    background-color: #f2dede;
}

footer {
    text-align: center;
    padding: 1rem;
    background-color: #333;
    color: white;
    margin-top: 2rem;
}
"""

        # Create the script.js file
        script_js = """document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh the page every 30 seconds
    setInterval(function() {
        location.reload();
    }, 30000);
});
"""

        # Write the files
        with open(os.path.join(template_dir, "index.html"), "w") as f:
            f.write(index_html)

        with open(os.path.join(template_dir, "static", "style.css"), "w") as f:
            f.write(style_css)

        with open(os.path.join(template_dir, "static", "script.js"), "w") as f:
            f.write(script_js)


async def main():
    """Run the test dashboard."""
    parser = argparse.ArgumentParser(description="Test dashboard")
    parser.add_argument("--report-dir", default="reports/tests", help="Directory containing test reports")
    parser.add_argument("--template-dir", default="templates/dashboard", help="Directory containing dashboard templates")
    parser.add_argument("--host", default="localhost", help="Host to bind the dashboard server")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind the dashboard server")
    parser.add_argument("--create-templates", action="store_true", help="Create the dashboard template files")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create the report directory if it doesn't exist
    os.makedirs(args.report_dir, exist_ok=True)

    # Create the template files if requested
    if args.create_templates:
        await TestDashboard.create_template_files(args.template_dir)
        logger.info(f"Created dashboard template files in {args.template_dir}")
        return

    # Create and start the dashboard
    dashboard = TestDashboard(
        report_dir=args.report_dir,
        template_dir=args.template_dir,
        host=args.host,
        port=args.port,
    )
    runner = await dashboard.start()

    # Keep the server running
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour
    except KeyboardInterrupt:
        logger.info("Stopping dashboard server")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
