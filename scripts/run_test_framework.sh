#!/bin/bash
# Run the test generation framework on a file or directory

set -e  # Exit on error

# Parse arguments
FILE=""
DIRECTORY=""
OUTPUT_DIR="reports"
GENERATE_TESTS=false
BATCH_MODE=false
PARALLEL=false

# Print usage
function print_usage {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --file FILE            Check a single file"
    echo "  --directory DIR        Check all files in a directory"
    echo "  --output-dir DIR       Directory to save reports (default: reports)"
    echo "  --generate-tests       Generate tests for files that pass the checks"
    echo "  --parallel             Run checks in parallel (batch mode only)"
    echo "  --help                 Print this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --file src/augment_adam/core/async_assistant.py"
    echo "  $0 --directory src/augment_adam/core --output-dir reports"
    echo "  $0 --directory src/augment_adam/core --generate-tests"
    echo "  $0 --directory src/augment_adam/core --parallel"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --file)
            FILE="$2"
            shift
            shift
            ;;
        --directory)
            DIRECTORY="$2"
            BATCH_MODE=true
            shift
            shift
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift
            shift
            ;;
        --generate-tests)
            GENERATE_TESTS=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --help)
            print_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Check that either --file or --directory is specified
if [[ -z "$FILE" && -z "$DIRECTORY" ]]; then
    echo "Error: Either --file or --directory must be specified"
    print_usage
    exit 1
fi

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Run the code quality checker
if [[ "$BATCH_MODE" == true ]]; then
    echo "Running code quality checks on all files in $DIRECTORY..."
    
    # Build the command
    CMD="python scripts/batch_code_quality_check.py --directory $DIRECTORY --output-dir $OUTPUT_DIR"
    
    # Add parallel flag if specified
    if [[ "$PARALLEL" == true ]]; then
        CMD="$CMD --parallel"
    fi
    
    # Run the command
    eval "$CMD"
    
    # Generate tests if requested
    if [[ "$GENERATE_TESTS" == true ]]; then
        echo "Generating tests for files that pass the checks..."
        
        # Find all report files
        REPORT_FILES=$(find "$OUTPUT_DIR" -name "*_report.md")
        
        # Loop through each report file
        for REPORT_FILE in $REPORT_FILES; do
            # Extract the file path from the report file name
            FILE_PATH=$(echo "$REPORT_FILE" | sed -e "s|$OUTPUT_DIR/||" -e "s|_report\.md$|.py|" -e "s|_|/|g")
            
            # Check if the file has no issues
            if ! grep -q "Issues: 0" "$REPORT_FILE"; then
                echo "Skipping $FILE_PATH (has issues)"
                continue
            fi
            
            echo "Generating tests for $FILE_PATH..."
            python scripts/generate_tests.py --file "$FILE_PATH"
        done
    fi
else
    echo "Running code quality check on $FILE..."
    python scripts/code_quality_checker.py --file "$FILE" --output "$OUTPUT_DIR/$(basename "$FILE" .py)_report.md"
    
    # Generate tests if requested
    if [[ "$GENERATE_TESTS" == true ]]; then
        # Check if the file has no issues
        if ! grep -q "Issues: 0" "$OUTPUT_DIR/$(basename "$FILE" .py)_report.md"; then
            echo "Skipping test generation (file has issues)"
        else
            echo "Generating tests for $FILE..."
            python scripts/generate_tests.py --file "$FILE"
        fi
    fi
fi

echo "Done!"
