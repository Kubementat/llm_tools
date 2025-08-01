#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from ..output_printer import OutputPrinter
from .. import Colors, Config, MergeIdeasWorkflow, FileHelper

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Idea merger workflow: Merges ideas from multiple documents into one final result document",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
TODO
        """
    )
    
    parser.add_argument(
        '--model', '-m',
        default=Config().default_model,
        help=f"The identifier of the model to use (default: {Config.DEFAULT_MODEL})."
    )
    
    parser.add_argument(
        '--api-endpoint', '-ae',
        default=Config.DEFAULT_API_ENDPOINT,
        help='OpenAI-compatible API endpoint URL'
    )
    
    parser.add_argument(
        '--api-key', '-ak',
        default="lmstudio",
        help='API key for authentication'
    )
    
    parser.add_argument(
        '--max-tokens', '-mt',
        type=int,
        default=50000,
        help='Maximum tokens in response for all LLM calls (Default: 50000)'
    )
    
    parser.add_argument(
        '--temperature', '-t',
        type=float,
        default=Config().default_model_temperature,
        help=f"Temperature for response generation for all LLM calls (Default: {Config.DEFAULT_MODEL_TEMPERATURE})"
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--output-file', '-o',
        required=True,
        help='File path to save the final document to'
    )
    
    parser.add_argument(
        '--source-documents', '-sd',
        required=True,
        help=f"Comma separated list of document paths to use for the merge."
    )

    return parser.parse_args()

def main():
    """Main execution function"""
    OutputPrinter.print_header("🚀 Idea Merger 🚀", Colors.BRIGHT_CYAN, 60)

    args = parse_arguments()

    config = Config()
    api_endpoint = config.api_endpoint
    api_key = config.api_key
    
    if args.api_key:
        api_key = args.api_key
    if args.api_endpoint:
        api_endpoint = args.api_endpoint
    if args.model:
        model = args.model
    
    OutputPrinter.print_info("api-endpoint",api_endpoint)
    OutputPrinter.print_info("model", model)
    OutputPrinter.print_info("source-documents", args.source_documents)
    OutputPrinter.print_info("temperature", args.temperature)
    OutputPrinter.print_info("max-tokens", args.max_tokens)
    OutputPrinter.print_info("verbose", args.verbose)
    OutputPrinter.print_info("output-file", args.output_file)

    workflow = MergeIdeasWorkflow(
        model=model,
        api_endpoint=api_endpoint,
        api_key=api_key,
        verbose=args.verbose,
        max_tokens=args.max_tokens,
        temperature=args.temperature
    )
    
    # load documents and initialize dict to pass into the merge ideas function
    document_paths = args.source_documents.split(",")
    source_documents = []
    for doc_path in document_paths:
        doc_content = FileHelper.read_file(doc_path, args.verbose)
        source_documents.append({
            "identifier": doc_path,
            "content": doc_content
        })
    
    doc_output = workflow.merge_ideas(source_documents=source_documents)
    FileHelper.write_to_file(args.output_file, doc_output, args.verbose)
    OutputPrinter.print_success("Finished merging ideas.")
    OutputPrinter.print_file_created(args.output_file)
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Process interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        OutputPrinter.print_error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)