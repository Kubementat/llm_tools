#!/usr/bin/env python3

import argparse
from .. import LLMApi, Config

def main():
    """
    Main function to list available models from the LLM API.
    
    This function initializes the LLMApi instance, retrieves the list of available models,
    and prints them to the console. It handles exceptions and prints error messages.
    
    Parameters:
        None
    
    Returns:
        None
    """
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Lists available models for an llm endpoint',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
 list_models.py --api-endpoint http://localhost:1234/v1 --api-key not-required
 list_models.py # for localhost:1234/v1
  
        """
    )

    parser.add_argument(
        '--api-endpoint',
        required=False,
        default=Config().api_endpoint,
        help=f"LLM server API endpoint. Default is {Config.DEFAULT_API_ENDPOINT}"
    )
    
    parser.add_argument(
        '--api-key',
        required=False,
        default=Config().api_key,
        help='API key for authentication (many local servers don\'t require this)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        config = Config()
        api_endpoint = config.api_endpoint
        api_key = config.api_key
        
        if args.api_endpoint:
            api_endpoint = args.api_endpoint
        if args.api_key:
            api_key = args.api_key
        
        llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key)
        models = llm_api.list_models()
        
        print("Available models:")
        for model in models:
            print(f"- {model}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
