#!/usr/bin/env python3
"""
CLI Interface for Sequential Task Execution

This script provides a command-line interface for executing tasks defined in JSON files.
It uses the SequentialTaskExecutor class to process tasks sequentially.

Usage:
    python execute_tasks.py --task-file <file_path> [options]

Options:
    --api-endpoint ENDPOINT   LLM server API endpoint
    --api-key KEY             API key for authentication (optional)
    --model MODEL             The model to use for task execution
    --output-directory DIR              Output directory for saving results
    --verbose                 Enable verbose output with debug information

Example:
    python execute_tasks.py --task-file tasks.json --output-directory ./results --verbose
"""

import argparse
import sys
from ..sequential_task_executor import SequentialTaskExecutor
from ..colors import Colors
from ..output_printer import OutputPrinter
from ..file_helper import FileHelper
from ..config import Config
from pathlib import Path
from datetime import datetime

def main():
    """
    Main function to execute tasks from a JSON file.

    Sets up argument parsing, configures output directory,
    initializes task executor, and handles task execution.

    Returns:
        None: This function runs the task execution process and doesn't return a value

    Raises:
        SystemExit: If required arguments are missing or if task execution fails
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Executes tasks defined in a JSON file sequentially.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--task-file', '-tf',
        required=True,
        help='Path to the JSON file containing tasks'
    )

    parser.add_argument(
        '--api-endpoint',
        default=Config().api_endpoint,
        help=f"LLM server API endpoint. Default is {Config.DEFAULT_API_ENDPOINT}"
    )

    parser.add_argument(
        '--api-key',
        required=False,
        default=Config().api_key,
        help='API key for authentication (many local servers don\'t require this)'
    )

    parser.add_argument(
        '--model', '-m',
        default=Config().default_model,
        help=f'The model to use for task execution (default: {Config.DEFAULT_MODEL})'
    )
    
    parser.add_argument(
        '--temperature', '-t',
        default=Config().default_model_temperature,
        help=f'The temperature to use for task execution (default: {Config.DEFAULT_MODEL_TEMPERATURE})'
    )

    parser.add_argument(
        '--output-directory', '-o',
        required=False,
        default=None,
        help='Output directory to save the results to (defaults to: $HOME/.sokrates/tasks/results/YY-MM-DD_H-M)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with debug information'
    )

    # Parse arguments
    args = parser.parse_args()
    config = Config(verbose=args.verbose)
    
    if not args.task_file:
        OutputPrinter.print_error("You must provide a task file using --task-file or -tf")
        sys.exit(1)
    
    # prepare and configure target directory    
    target_directory = Config.create_and_return_task_execution_directory(args.output_directory)
    OutputPrinter.print_info("Writing results to directory", target_directory)
    
    # copy over task file for better reusability of the created directory
    task_file_name = Path(args.task_file).name
    task_file_copy_full_path  = Path(target_directory) / task_file_name
    FileHelper.copy_file(args.task_file,task_file_copy_full_path, verbose=args.verbose)

    # Initialize executor
    executor = SequentialTaskExecutor(
        api_endpoint=args.api_endpoint,
        api_key=args.api_key or Config.DEFAULT_API_KEY,
        model=args.model,
        temperature=args.temperature,
        output_dir=target_directory,
        verbose=args.verbose
    )

    try:
        # Execute tasks
        result = executor.execute_tasks_from_file(args.task_file)

        OutputPrinter.print_section("EXECUTION SUMMARY", Colors.BRIGHT_BLUE, "═")
        print(f"Task list: {task_file_copy_full_path}")
        print(f"Task result directory: {target_directory}")
        print(f"Total tasks: {result['total_tasks']}")
        print(f"Successful: {result['successful_tasks']}")
        print(f"Failed: {result['failed_tasks']}")

        if args.verbose:
            print("\nDetailed results:")
            for detail in result['details']:
                status_color = Colors.GREEN if detail['status'] == 'completed' else Colors.RED
                print(f"{detail['task_id']}: {detail['status']} - {detail['message']}")

    except Exception as e:
        OutputPrinter.print_error(f"Error executing tasks: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Process interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
        sys.exit(1)