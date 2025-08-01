#!/usr/bin/env python3
"""
Python Script to Utilize LLM via REST Endpoint (OpenAI Compatible API)

This script sends text prompts to a locally running LLM server (e.g., LM Studio) 
that provides an OpenAI-compatible REST API. It processes the response as markdown.
It accepts a text prompt and a refinement prompt file as command line arguments.

Requirements:
- Python 3.7 or later
- openai library: pip install openai
- A locally running LLM server with OpenAI-compatible API (e.g., LM Studio)

# General usage:
ENDPOINT="http://localhost:1234/v1"
MODELS="deepseek-r1-distill-qwen-7b,qwen3-4b"
INPUT_FILE="input.md"
REFINEMENT_INSTRUCTIONS_FILE="refinement.md"
OUTPUT_FILE="improved.md"
uv run python refine-prompt.py --api-endpoint "$ENDPOINT"  --models "$MODELS" --input-file $INPUT_FILE  "$REFINEMENT_INSTRUCTIONS_FILE" --verbose --max-tokens 10000 --output $OUTPUT_FILE
"""

import sys
import argparse
from pathlib import Path
import time
from openai import OpenAI
from .. import LLMApi, PromptRefiner, Colors, FileHelper, Config
from ..output_printer import OutputPrinter

# TODO:
# - Improve extraction of generated prompts (remove "think" tags).
# Feature: Allow sending the refined prompt to other LLMs.
# - allow specifying an output directory for the generated prompts (create it if not present)
# Add a parameter to specify the wait time after model unloading (default: 0 seconds).

def validate_endpoint_url(url):
    """
    Basic validation for API endpoint URL.
    
    Args:
        url (str): API endpoint URL
        
    Returns:
        bool: True if URL seems valid
    """
    return url.startswith(('http://', 'https://')) and len(url.strip()) > 8


def main():
    """Main function to handle command line arguments and orchestrate the process."""
    
    # Print beautiful header
    OutputPrinter.print_header("🤖 sokrates PROMPT REFINER 🚀", Colors.BRIGHT_CYAN, 60)
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Send prompts to LLM server with OpenAI-compatible API and get markdown output',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using input file instead of command line prompt
  python script.py --input-file "initial_prompt.txt" \\
    --refinement-prompt-file refinement.txt \\
    --api-endpoint "http://localhost:1234/v1" \\
    --api-key "lm-studio"

  # LM Studio default endpoint with command line prompt
  python script.py --text-prompt "What is machine learning?" \\
    --refinement-prompt-file refinement.txt \\
    --api-endpoint "http://localhost:1234/v1" \\
    --api-key "lm-studio"

  # Using input file with output file
  python refine-prompt.py --input-file "complex_prompt.txt" \\
    --refinement-prompt-file prompts/refinement.txt \\
    --api-endpoint "http://localhost:11434/v1" \\
    --api-key "" \\
    --models "llama2,phi4" \\
    --output "detailed_response.md"

  # Local server with custom settings and output to file
  python refine-prompt.py --text-prompt "Write a summary" \\
    --refinement-prompt-file refinement.txt \\
    --api-endpoint "http://192.168.1.100:8080/v1" \\
    --api-key "my-local-token" \\
    --models "custom-model" \\
    --max-tokens 500 \\
    --output "summary_response.md"
        """
    )
    
    parser.add_argument(
        '--text-prompt', '-p',
        required=False,
        help='Initial text prompt to send to the LLM (not required if --input-file is used)'
    )
    
    parser.add_argument(
        '--refinement-prompt-file', '-rpf',
        required=False,
        help='Path to file containing refinement prompt'
    )
    
    parser.add_argument(
        '--input-file', '-i',
        help='Path to file containing the initial text prompt (alternative to text_prompt argument)'
    )
    
    parser.add_argument(
        '--api-endpoint',
        required=False,
        default=Config().api_endpoint,
        help=f"LLM server API endpoint. Default is {Config.DEFAULT_API_ENDPOINT}"
    )
    
    parser.add_argument(
        '--api-key',
        default=Config().api_key,
        help='API key for authentication (many local servers don\'t require this)'
    )
    
    parser.add_argument(
        '--models', '-m',
        default=Config().default_model,
        help=f"Comma separated list of models to use (default: {Config.DEFAULT_MODEL}). For multiple models e.g: qwen/qwen3-14b,phi4"
    )
    
    parser.add_argument(
        '--max-tokens', '-mt',
        type=int,
        default=4000,
        help='Maximum tokens in response (default: 4000)'
    )
    
    parser.add_argument(
        '--temperature', '-t',
        type=float,
        default=Config().default_model_temperature,
        help=f"Temperature for response generation (default: {Config.DEFAULT_MODEL_TEMPERATURE})"
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with debug information'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output filename to save the response (e.g., response.md)'
    )
    
    # context
    parser.add_argument(
        '--context-text', '-ct',
        default=None,
        help='Optional additional context text to prepend before the prompt'
    )
    parser.add_argument(
        '--context-files', '-cf',
        help='Optional comma separated additional context text file paths with content that should be prepended before the prompt'
    )
    parser.add_argument(
        '--context-directories', '-cd',
        default=None,
        help='Optional comma separated additional directory paths with files with content that should be prepended before the prompt'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    config = Config()
    
    # Validate that either text_prompt or input-file is provided
    if not args.text_prompt and not args.input_file:
        OutputPrinter.print_error("Either provide a text_prompt argument or use --input-file option")
        parser.print_help(file=sys.stderr)
        sys.exit(1)
    
    if args.text_prompt and args.input_file:
        OutputPrinter.print_error("Cannot use both text_prompt argument and --input-file option simultaneously")
        OutputPrinter.print_warning("Choose either command line prompt or input file, not both")
        sys.exit(1)
    
    # Validate text prompt (if provided via command line)
    if args.text_prompt and not args.text_prompt.strip():
        OutputPrinter.print_error("Text prompt cannot be empty")
        sys.exit(1)
    
    # Validate input file existence (if provided)
    if args.input_file and not Path(args.input_file).exists():
        OutputPrinter.print_error(f"Input prompt file not found: {args.input_file}")
        sys.exit(1)
    
    refinement_prompt_file = args.refinement_prompt_file
    if not args.refinement_prompt_file:
        refinement_prompt_file = Path(f"{Path(__file__).parent.parent.resolve()}/prompts/refine-prompt.md")
        OutputPrinter.print_info("No refinement prompt file provided. Using default:", refinement_prompt_file, Colors.BRIGHT_CYAN)
        
    if not Path(refinement_prompt_file).exists():
        OutputPrinter.print_error(f"Refinement prompt file not found: {refinement_prompt_file}")
        sys.exit(1)

    api_endpoint = args.api_endpoint
    if api_endpoint:
        if not validate_endpoint_url(api_endpoint):
            OutputPrinter.print_error(f"Invalid API endpoint URL: {args.api_endpoint}")
            OutputPrinter.print_warning("URL should start with http:// or https:// (e.g., http://localhost:1234/v1)")
            sys.exit(1)
    else:
        api_endpoint = config.api_endpoint
        
    api_key = args.api_key
    if not api_key:
        api_key = config.api_key
    
    models = None
    if args.models is not None:
        models = [s.strip() for s in args.models.split(",")]
    # load via env and .env file when not specified via parameter
    if not models:
        models = [config.default_model]
    
    if args.verbose:
        OutputPrinter.print_section("⚙️ CONFIGURATION", Colors.BRIGHT_BLUE, "═")
        OutputPrinter.print_info("API Endpoint", api_endpoint, Colors.BRIGHT_CYAN)
        OutputPrinter.print_info("API Key", '[SET]' if api_key else '[EMPTY]', Colors.BRIGHT_CYAN)
        OutputPrinter.print_info("Models", ', '.join(models), Colors.BRIGHT_CYAN)
        OutputPrinter.print_info("Max Tokens", f"{args.max_tokens:,}", Colors.BRIGHT_CYAN)
        OutputPrinter.print_info("Temperature", f"{args.temperature}", Colors.BRIGHT_CYAN)
        OutputPrinter.print_info("Refinement prompt file", f"{refinement_prompt_file}", Colors.BRIGHT_CYAN)
        OutputPrinter.print_info("Input Method", 'File' if args.input_file else 'Command Line', Colors.BRIGHT_CYAN)
        if args.input_file:
            OutputPrinter.print_info("Input File", args.input_file, Colors.BRIGHT_CYAN)
        if args.output:
            OutputPrinter.print_info("Output File", args.output, Colors.BRIGHT_CYAN)
        print()
        
    # context
    context_array = []
    if args.context_text:
        context_array.append(args.context_text)
        OutputPrinter.print_info("Appending context text to prompt:", args.context_text , Colors.BRIGHT_MAGENTA)
    if args.context_directories:
        directories = [s.strip() for s in args.context_directories.split(",")]
        context_array.extend(FileHelper.read_multiple_files_from_directories(directories, verbose=args.verbose))
        OutputPrinter.print_info("Appending context directories to prompt:", args.context_directories , Colors.BRIGHT_MAGENTA)
    if args.context_files:
        files = [s.strip() for s in args.context_files.split(",")]
        context_array.extend(FileHelper.read_multiple_files(files, verbose=args.verbose))
        OutputPrinter.print_info("Appending context files to prompt:", args.context_files , Colors.BRIGHT_MAGENTA)
    
    try:
        refiner = PromptRefiner(verbose=args.verbose)
        llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key, verbose=args.verbose)
        
        # Load initial prompt (either from command line or file)
        if args.input_file:
            if args.verbose:
                OutputPrinter.print_progress(f"Loading initial prompt from file {Colors.CYAN}{args.input_file}{Colors.RESET}")
            text_prompt = FileHelper.read_file(args.input_file, args.verbose)
        else:
            text_prompt = args.text_prompt
        # Load refinement prompt
        if args.verbose:
            OutputPrinter.print_progress(f"Loading refinement prompt from file {Colors.CYAN}{refinement_prompt_file}{Colors.RESET}")
        refinement_prompt = FileHelper.read_file(refinement_prompt_file, args.verbose)
        
        # Combine prompts
        if args.verbose:
            OutputPrinter.print_progress("Combining prompts...")
        combined_prompt = refiner.combine_refinement_prompt(text_prompt, refinement_prompt)
        
        if args.verbose:
            OutputPrinter.print_info("Combined prompt length", f"{len(combined_prompt):,} characters", Colors.BRIGHT_MAGENTA)
        
        # Send to LLM
        if args.verbose:
            OutputPrinter.print_progress(f"Sending request to LLM server at {Colors.CYAN}{api_endpoint}{Colors.RESET}")
        
        # send to llm
        created_files = []
        for i, model_name in enumerate(models, 1):
            OutputPrinter.print_header(f"🎯 MODEL {i}/{len(models)}: {model_name}", Colors.BRIGHT_GREEN, 60)

            response_content = llm_api.send(combined_prompt, model=model_name, 
                max_tokens=args.max_tokens, context_array=context_array)
            processed_content = refiner.clean_response(response_content)
        
            # Format as markdown
            markdown_output = refiner.format_as_markdown(processed_content)
        
            # Save to file if output filename is specified
            if args.output:
                f_name = args.output
                f_extension = 'md'
                
                try:
                    f_name, f_extension = args.output.rsplit('.', 1)
                except:
                    pass
                
                model_name_escaped = model_name.replace('/', '-')
                new_file_name = f"{f_name}-{model_name_escaped}.{f_extension}"
                
                OutputPrinter.print_progress(f"Saving response to file: {Colors.CYAN}{new_file_name}{Colors.RESET}")
                FileHelper.write_to_file(file_path=new_file_name, content=markdown_output, verbose=args.verbose)
                created_files.append(new_file_name)
                OutputPrinter.print_file_created(new_file_name)
            
            # Print the result to stdout (always print, regardless of file output)
            OutputPrinter.print_section(f"✨ GENERATED PROMPT FOR {model_name.upper()}", Colors.BRIGHT_MAGENTA, "═")
            print(f"{Colors.WHITE}{markdown_output}{Colors.RESET}")
            OutputPrinter.print_section("", Colors.BRIGHT_MAGENTA, "═")
            
            # Model unload wait
            if i < len(models):  # Don't wait after the last model
                OutputPrinter.print_progress(f"Waiting for model to unload... {Colors.DIM}(8 seconds){Colors.RESET}")
                time.sleep(8)
        
        # print files created list
        if created_files:
            OutputPrinter.print_header("📁 CREATED FILES", Colors.BRIGHT_GREEN, 60)
            for file_name in created_files:
                OutputPrinter.print_file_created(file_name)
            print()
        
        OutputPrinter.print_header("🎉 PROCESS COMPLETED SUCCESSFULLY! 🎉", Colors.BRIGHT_GREEN, 60)

    except FileNotFoundError as e:
        OutputPrinter.print_error(f"File Error: {e}")
        sys.exit(1)
    except IOError as e:
        OutputPrinter.print_error(f"IO Error: {e}")
        sys.exit(1)
    except Exception as e:
        OutputPrinter.print_error(f"Error: {e}")
        if args.verbose:
            import traceback
            OutputPrinter.print_section("🐛 FULL TRACEBACK", Colors.BRIGHT_RED, "═")
            traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
