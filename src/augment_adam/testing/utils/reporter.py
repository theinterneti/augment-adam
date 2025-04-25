"""
Test reporter utilities.

This module provides utilities for test reporters, including a base test reporter class
and specialized test reporter classes for different types of reports.
"""

import os
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Set, Union, Callable, Type, TextIO

from augment_adam.utils.tagging import tag, TagCategory
from augment_adam.testing.utils.result import TestResult


@tag("testing.utils")
class TestReporter:
    """
    Base class for test reporters.
    
    This class provides functionality for reporting test results.
    
    Attributes:
        metadata: Additional metadata for the test reporter.
        stream: The stream to write output to.
    
    TODO(Issue #13): Add support for test reporter dependencies
    TODO(Issue #13): Implement test reporter analytics
    """
    
    def __init__(
        self,
        stream: Optional[TextIO] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the test reporter.
        
        Args:
            stream: The stream to write output to.
            metadata: Additional metadata for the test reporter.
        """
        self.stream = stream
        self.metadata = metadata or {}
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set metadata for the test reporter.
        
        Args:
            key: The key for the metadata.
            value: The value for the metadata.
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata for the test reporter.
        
        Args:
            key: The key for the metadata.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def report(self, result: TestResult) -> None:
        """
        Report test results.
        
        Args:
            result: The test result to report.
        """
        pass


@tag("testing.utils")
class TextReporter(TestReporter):
    """
    Reporter for text output.
    
    This class provides a reporter for text output.
    
    Attributes:
        metadata: Additional metadata for the test reporter.
        stream: The stream to write output to.
    
    TODO(Issue #13): Add support for text reporter dependencies
    TODO(Issue #13): Implement text reporter analytics
    """
    
    def report(self, result: TestResult) -> None:
        """
        Report test results as text.
        
        Args:
            result: The test result to report.
        """
        if self.stream is None:
            return
        
        # Get the summary
        summary = result.get_summary()
        
        # Write the summary
        self.stream.write("\n")
        self.stream.write(f"Ran {summary['total']} tests in {summary['total_time']:.3f}s\n")
        self.stream.write("\n")
        
        if summary['failure'] > 0 or summary['error'] > 0:
            self.stream.write("FAILED")
        else:
            self.stream.write("OK")
        
        details = []
        
        if summary['failure'] > 0:
            details.append(f"failures={summary['failure']}")
        
        if summary['error'] > 0:
            details.append(f"errors={summary['error']}")
        
        if summary['skip'] > 0:
            details.append(f"skipped={summary['skip']}")
        
        if details:
            self.stream.write(f" ({', '.join(details)})")
        
        self.stream.write("\n")
        self.stream.write(f"Success rate: {summary['success_rate']:.2f}%\n")
        
        # Write the failures
        if result.failures:
            self.stream.write("\n")
            self.stream.write("FAILURES:\n")
            
            for test, err in result.failures:
                self.stream.write(f"\n{result.getDescription(test)}\n")
                self.stream.write(f"{err}\n")
        
        # Write the errors
        if result.errors:
            self.stream.write("\n")
            self.stream.write("ERRORS:\n")
            
            for test, err in result.errors:
                self.stream.write(f"\n{result.getDescription(test)}\n")
                self.stream.write(f"{err}\n")
        
        self.stream.flush()


@tag("testing.utils")
class JsonReporter(TestReporter):
    """
    Reporter for JSON output.
    
    This class provides a reporter for JSON output.
    
    Attributes:
        metadata: Additional metadata for the test reporter.
        stream: The stream to write output to.
        file_path: The path to the JSON file.
    
    TODO(Issue #13): Add support for JSON reporter dependencies
    TODO(Issue #13): Implement JSON reporter analytics
    """
    
    def __init__(
        self,
        stream: Optional[TextIO] = None,
        metadata: Optional[Dict[str, Any]] = None,
        file_path: Optional[str] = None
    ) -> None:
        """
        Initialize the JSON reporter.
        
        Args:
            stream: The stream to write output to.
            metadata: Additional metadata for the test reporter.
            file_path: The path to the JSON file.
        """
        super().__init__(stream, metadata)
        self.file_path = file_path
    
    def report(self, result: TestResult) -> None:
        """
        Report test results as JSON.
        
        Args:
            result: The test result to report.
        """
        # Get the summary
        summary = result.get_summary()
        
        # Create the report
        report = {
            "summary": summary,
            "failures": [
                {
                    "test": result.getDescription(test),
                    "error": err,
                }
                for test, err in result.failures
            ],
            "errors": [
                {
                    "test": result.getDescription(test),
                    "error": err,
                }
                for test, err in result.errors
            ],
            "skipped": [
                {
                    "test": result.getDescription(test),
                    "reason": reason,
                }
                for test, reason in result.skipped
            ],
            "timings": {
                result.getDescription(test): time
                for test, time in result.timings.items()
            },
        }
        
        # Write the report to the stream
        if self.stream is not None:
            json.dump(report, self.stream, indent=2)
            self.stream.flush()
        
        # Write the report to a file
        if self.file_path is not None:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
            
            # Write the report
            with open(self.file_path, "w") as f:
                json.dump(report, f, indent=2)


@tag("testing.utils")
class XmlReporter(TestReporter):
    """
    Reporter for XML output.
    
    This class provides a reporter for XML output.
    
    Attributes:
        metadata: Additional metadata for the test reporter.
        stream: The stream to write output to.
        file_path: The path to the XML file.
    
    TODO(Issue #13): Add support for XML reporter dependencies
    TODO(Issue #13): Implement XML reporter analytics
    """
    
    def __init__(
        self,
        stream: Optional[TextIO] = None,
        metadata: Optional[Dict[str, Any]] = None,
        file_path: Optional[str] = None
    ) -> None:
        """
        Initialize the XML reporter.
        
        Args:
            stream: The stream to write output to.
            metadata: Additional metadata for the test reporter.
            file_path: The path to the XML file.
        """
        super().__init__(stream, metadata)
        self.file_path = file_path
    
    def report(self, result: TestResult) -> None:
        """
        Report test results as XML.
        
        Args:
            result: The test result to report.
        """
        # Get the summary
        summary = result.get_summary()
        
        # Create the root element
        root = ET.Element("testsuites")
        root.set("tests", str(summary["total"]))
        root.set("failures", str(summary["failure"]))
        root.set("errors", str(summary["error"]))
        root.set("time", str(summary["total_time"]))
        
        # Create the testsuite element
        testsuite = ET.SubElement(root, "testsuite")
        testsuite.set("name", "augment_adam")
        testsuite.set("tests", str(summary["total"]))
        testsuite.set("failures", str(summary["failure"]))
        testsuite.set("errors", str(summary["error"]))
        testsuite.set("skipped", str(summary["skip"]))
        testsuite.set("time", str(summary["total_time"]))
        
        # Add the test cases
        for test, time in result.timings.items():
            # Create the testcase element
            testcase = ET.SubElement(testsuite, "testcase")
            testcase.set("name", test)
            testcase.set("time", str(time))
            
            # Check if the test failed
            for t, err in result.failures:
                if result.getDescription(t) == test:
                    # Create the failure element
                    failure = ET.SubElement(testcase, "failure")
                    failure.set("message", err.split("\n")[0])
                    failure.text = err
            
            # Check if the test had an error
            for t, err in result.errors:
                if result.getDescription(t) == test:
                    # Create the error element
                    error = ET.SubElement(testcase, "error")
                    error.set("message", err.split("\n")[0])
                    error.text = err
            
            # Check if the test was skipped
            for t, reason in result.skipped:
                if result.getDescription(t) == test:
                    # Create the skipped element
                    skipped = ET.SubElement(testcase, "skipped")
                    skipped.set("message", reason)
        
        # Create the XML string
        xml_string = ET.tostring(root, encoding="unicode")
        
        # Write the XML to the stream
        if self.stream is not None:
            self.stream.write(xml_string)
            self.stream.flush()
        
        # Write the XML to a file
        if self.file_path is not None:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
            
            # Write the XML
            with open(self.file_path, "w") as f:
                f.write(xml_string)


@tag("testing.utils")
class HtmlReporter(TestReporter):
    """
    Reporter for HTML output.
    
    This class provides a reporter for HTML output.
    
    Attributes:
        metadata: Additional metadata for the test reporter.
        stream: The stream to write output to.
        file_path: The path to the HTML file.
        title: The title of the HTML report.
    
    TODO(Issue #13): Add support for HTML reporter dependencies
    TODO(Issue #13): Implement HTML reporter analytics
    """
    
    def __init__(
        self,
        stream: Optional[TextIO] = None,
        metadata: Optional[Dict[str, Any]] = None,
        file_path: Optional[str] = None,
        title: str = "Test Report"
    ) -> None:
        """
        Initialize the HTML reporter.
        
        Args:
            stream: The stream to write output to.
            metadata: Additional metadata for the test reporter.
            file_path: The path to the HTML file.
            title: The title of the HTML report.
        """
        super().__init__(stream, metadata)
        self.file_path = file_path
        self.title = title
    
    def report(self, result: TestResult) -> None:
        """
        Report test results as HTML.
        
        Args:
            result: The test result to report.
        """
        # Get the summary
        summary = result.get_summary()
        
        # Create the HTML
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"    <title>{self.title}</title>",
            "    <style>",
            "        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }",
            "        h1 { color: #333; }",
            "        h2 { color: #666; }",
            "        table { border-collapse: collapse; width: 100%; }",
            "        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "        th { background-color: #f2f2f2; }",
            "        tr:nth-child(even) { background-color: #f9f9f9; }",
            "        .success { color: green; }",
            "        .failure { color: red; }",
            "        .error { color: red; }",
            "        .skip { color: orange; }",
            "        .details { margin-top: 10px; padding: 10px; background-color: #f5f5f5; border-radius: 5px; }",
            "    </style>",
            "</head>",
            "<body>",
            f"    <h1>{self.title}</h1>",
            "    <h2>Summary</h2>",
            "    <table>",
            "        <tr>",
            "            <th>Total</th>",
            "            <th>Success</th>",
            "            <th>Failure</th>",
            "            <th>Error</th>",
            "            <th>Skip</th>",
            "            <th>Success Rate</th>",
            "            <th>Total Time</th>",
            "        </tr>",
            "        <tr>",
            f"            <td>{summary['total']}</td>",
            f"            <td class=\"success\">{summary['success']}</td>",
            f"            <td class=\"failure\">{summary['failure']}</td>",
            f"            <td class=\"error\">{summary['error']}</td>",
            f"            <td class=\"skip\">{summary['skip']}</td>",
            f"            <td>{summary['success_rate']:.2f}%</td>",
            f"            <td>{summary['total_time']:.3f}s</td>",
            "        </tr>",
            "    </table>",
        ]
        
        # Add the failures
        if result.failures:
            html.extend([
                "    <h2>Failures</h2>",
                "    <table>",
                "        <tr>",
                "            <th>Test</th>",
                "            <th>Error</th>",
                "        </tr>",
            ])
            
            for test, err in result.failures:
                html.extend([
                    "        <tr>",
                    f"            <td>{result.getDescription(test)}</td>",
                    f"            <td><pre>{err}</pre></td>",
                    "        </tr>",
                ])
            
            html.append("    </table>")
        
        # Add the errors
        if result.errors:
            html.extend([
                "    <h2>Errors</h2>",
                "    <table>",
                "        <tr>",
                "            <th>Test</th>",
                "            <th>Error</th>",
                "        </tr>",
            ])
            
            for test, err in result.errors:
                html.extend([
                    "        <tr>",
                    f"            <td>{result.getDescription(test)}</td>",
                    f"            <td><pre>{err}</pre></td>",
                    "        </tr>",
                ])
            
            html.append("    </table>")
        
        # Add the skipped tests
        if result.skipped:
            html.extend([
                "    <h2>Skipped</h2>",
                "    <table>",
                "        <tr>",
                "            <th>Test</th>",
                "            <th>Reason</th>",
                "        </tr>",
            ])
            
            for test, reason in result.skipped:
                html.extend([
                    "        <tr>",
                    f"            <td>{result.getDescription(test)}</td>",
                    f"            <td>{reason}</td>",
                    "        </tr>",
                ])
            
            html.append("    </table>")
        
        # Add the timings
        html.extend([
            "    <h2>Timings</h2>",
            "    <table>",
            "        <tr>",
            "            <th>Test</th>",
            "            <th>Time</th>",
            "        </tr>",
        ])
        
        for test, time in sorted(result.timings.items(), key=lambda x: x[1], reverse=True):
            html.extend([
                "        <tr>",
                f"            <td>{test}</td>",
                f"            <td>{time:.3f}s</td>",
                "        </tr>",
            ])
        
        html.append("    </table>")
        
        # Add the footer
        html.extend([
            "</body>",
            "</html>",
        ])
        
        # Join the HTML
        html_string = "\n".join(html)
        
        # Write the HTML to the stream
        if self.stream is not None:
            self.stream.write(html_string)
            self.stream.flush()
        
        # Write the HTML to a file
        if self.file_path is not None:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
            
            # Write the HTML
            with open(self.file_path, "w") as f:
                f.write(html_string)
