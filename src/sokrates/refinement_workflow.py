# This script defines the `RefinementWorkflow` class, which orchestrates
# prompt refinement and execution processes. It integrates with `LLMApi`
# for interacting with Large Language Models and `PromptRefiner` for
# cleaning and formatting LLM responses. This class provides methods
# for refining input prompts, sending them to LLMs for execution, and
# generating specific content like "mantras" based on provided context.

from typing import List
from pathlib import Path
from .llm_api import LLMApi
from .prompt_refiner import PromptRefiner
from .colors import Colors
from .config import Config
from .file_helper import FileHelper

class RefinementWorkflow:
    """
    Orchestrates prompt refinement and execution workflows.

    This class integrates with LLM API for model interaction and
    PromptRefiner for prompt processing and response cleaning.
    """
    def __init__(self, api_endpoint: str = Config.DEFAULT_API_ENDPOINT, 
        api_key: str = Config.DEFAULT_API_KEY, 
        model: str = Config.DEFAULT_MODEL, 
        max_tokens: int = 20000,
        temperature: float = 0.7,
        verbose: bool = False) -> None:
      """
      Initializes the RefinementWorkflow.

      Args:
          api_endpoint (str): The API endpoint for the LLM. Defaults to Config.DEFAULT_API_ENDPOINT.
          api_key (str): The API key for the LLM. Defaults to Config.DEFAULT_API_KEY.
          model (str): The default LLM model to use. Defaults to Config.DEFAULT_MODEL.
          max_tokens (int): The maximum number of tokens for LLM responses. Defaults to 20000.
          temperature (float): The sampling temperature for LLM responses. Defaults to 0.7.
          verbose (bool): If True, enables verbose output. Defaults to False.
      """
      self.llm_api = LLMApi(api_endpoint=api_endpoint, api_key=api_key, verbose=verbose)
      self.refiner = PromptRefiner(verbose=verbose)
      self.model = model
      self.max_tokens = max_tokens
      self.temperature = temperature
      self.verbose = verbose

    def refine_prompt(self, input_prompt: str, refinement_prompt: str, context_array: List[str]=None) -> str:
      """
      Refines an input prompt using a specified refinement prompt and an LLM.

      Args:
          input_prompt (str): The initial prompt to be refined.
          refinement_prompt (str): The prompt containing instructions for refinement.

      Returns:
          str: The refined and formatted prompt as a Markdown string.
      """
      if self.verbose:
        print(f"{Colors.MAGENTA}Refining prompt:\n{Colors.RESET}")
        print(f"{Colors.MAGENTA}{input_prompt}\n{Colors.RESET}")
      combined_prompt = self.refiner.combine_refinement_prompt(input_prompt, refinement_prompt)
      response_content = self.llm_api.send(combined_prompt, model=self.model, max_tokens=self.max_tokens, context_array=context_array)
      processed_content = self.refiner.clean_response(response_content)

      # Format as markdown
      markdown_output = self.refiner.format_as_markdown(processed_content)
      if self.verbose:
        print(f"{Colors.MAGENTA}Processed response:\n{Colors.RESET}")
        print(f"{Colors.MAGENTA}{markdown_output}\n{Colors.RESET}")
      return markdown_output
    
    def refine_and_send_prompt(self, input_prompt: str, refinement_prompt: str, refinement_model: str = None, execution_model: str = None, refinement_temperature: float = None) -> str:
      """
      Refines an input prompt and then sends the refined prompt to an LLM for execution.

      Args:
          input_prompt (str): The initial prompt to be refined.
          refinement_prompt (str): The prompt containing instructions for refinement.
          refinement_model (str, optional): The model to use for refinement. Defaults to self.model.
          execution_model (str, optional): The model to use for execution. Defaults to self.model.
          refinement_temperature (float, optional): The temperature for refinement. Defaults to self.temperature.

      Returns:
          str: The executed response as a Markdown string.
      """
      if not refinement_model:
        refinement_model = self.model
      if not execution_model:
        execution_model = self.model
      if not refinement_temperature:
        refinement_temperature = self.temperature
      
      if self.verbose:
        print(f"{Colors.MAGENTA}Refining and sending prompt...\n{Colors.RESET}")
      refined_prompt = self.refine_prompt(input_prompt=input_prompt, refinement_prompt=refinement_prompt)
      
      if self.verbose:
        print(f"{Colors.MAGENTA}Sending refined prompt to model: {execution_model}\n{Colors.RESET}") # Corrected model_name to execution_model
      
      
      response_content = self.llm_api.send(refined_prompt, model=execution_model, 
        max_tokens=self.max_tokens, temperature=refinement_temperature)
      processed_content = self.refiner.clean_response(response_content)

      # Format as markdown
      markdown_output = self.refiner.format_as_markdown(processed_content)
      if self.verbose:
        print(f"{Colors.MAGENTA}Execution response:\n{Colors.RESET}")
        print(f"{Colors.MAGENTA}{markdown_output}\n{Colors.RESET}")
      return markdown_output
    
    def breakdown_task(self, task: str, model: str, context_array: List[str] = None):
      breakdown_instructions_filepath = Path(f"{Path(__file__).parent.resolve()}/prompts/breakdown-v1.md").resolve()
      breakdown_instructions = FileHelper.read_file(breakdown_instructions_filepath)
      
      result = self.refine_prompt(input_prompt=task, refinement_prompt=breakdown_instructions, context_array=context_array)
      return result
    
    def generate_mantra(self, context_files: List[str] = None, task_file_path: str = None) -> str:
      """
      Generates a "mantra" based on provided context and a task file.

      Args:
          context_files (List[str], optional): A list of file paths containing context for mantra generation.
                                               Defaults to a specific self-improvement principles file.
          task_file_path (str, optional): The file path containing the task prompt for mantra generation.
                                          Defaults to a specific generate-mantra file.

      Returns:
          str: The generated mantra as a Markdown string.
      """
      if not context_files:
        context_files = [
          Path(f"{Path(__file__).parent.resolve()}/prompts/context/self-improvement-principles-v1.md").resolve()
        ]
      if not task_file_path:
        task_file_path = Path(f"{Path(__file__).parent.resolve()}/prompts/generate-mantra-v1.md").resolve()
      
      task = FileHelper.read_file(file_path=task_file_path)
      context = FileHelper.combine_files(file_paths=context_files)
      if self.verbose:
        print(f"{Colors.MAGENTA}Context:\n{Colors.RESET}")
        print(f"{Colors.MAGENTA}{context}\n{Colors.RESET}")
        
      print(f"{Colors.MAGENTA}Generating mantra for today...\n{Colors.RESET}")
      
      combined_prompt = self.refiner.combine_refinement_prompt(task, context)
      response_content = self.llm_api.send(combined_prompt, model=self.model, max_tokens=self.max_tokens)
      processed_content = self.refiner.clean_response(response_content)

      # Format as markdown
      markdown_output = self.refiner.format_as_markdown(processed_content)
      if self.verbose:
        print(f"{Colors.MAGENTA}Processed response:\n{Colors.RESET}")
        print(f"{Colors.MAGENTA}{markdown_output}\n{Colors.RESET}")
      return markdown_output
