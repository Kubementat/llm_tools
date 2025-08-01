# sokrates

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Version: 0.4.2](https://img.shields.io/badge/Version-0.4.2-brightgreen.svg)](https://github.com/Kubementat/sokrates)

A comprehensive framework for Large Language Model (LLM) interactions, featuring advanced prompt refinement, system monitoring, extensive CLI tools, and a robust task queue system. Designed to facilitate working with LLMs through modular components, well-documented APIs, and production-ready utilities.

## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
  - [Available Commands](#available-commands)
  - [Task Queuing System](#task-queuing-system)
  - [sokrates-chat Commands](#sokrates-chat-commands)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Changelog](#changelog)

## Description

`sokrates` is a comprehensive framework for working with Large Language Models (LLMs). It provides a complete toolkit for developers and researchers to interact with LLMs efficiently and effectively.

### Core Capabilities:

- **Advanced Prompt Engineering**: Sophisticated prompt refinement tools that optimize LLM input/output for better performance
- **Real-time System Monitoring**: Track CPU, memory, and resource usage during LLM operations with detailed performance metrics
- **Voice-Enabled Chat**: Interactive command-line chat interface with optional voice input/output using OpenAI Whisper
- **Task Queue System**: Robust background task processing with persistence, error handling, and retry mechanisms
- **Multi-stage Workflows**: Complex task breakdown, idea generation, and sequential task execution
- **Extensive CLI Interface**: 15+ specialized commands for rapid experimentation and automation

### Key Features:

- **Modular Architecture**: Easily extensible components with clean separation of concerns
- **OpenAI-Compatible API**: Works with any OpenAI-compatible endpoint (LocalAI, Ollama, LM Studio, etc.)
- **Configuration Management**: Flexible configuration system with environment variable support
- **Output Processing**: Advanced text cleaning and formatting utilities for LLM-generated content
- **Performance Analytics**: Detailed timing metrics and token generation statistics
- **File Management**: Comprehensive file handling for context loading and result storage

## Installation

### Prerequisites

- Python 3.9 or higher
- Optional: FFmpeg (for voice features)
- Optional: Whisper-cpp (for enhanced voice processing)

### Install from PyPI

```bash
pip install sokrates

# or using uv (recommended)
## basic version: 
uv pip install sokrates

## voice enabled version
uv pip install sokrates[voice]

# Test the installation
sokrates-list-models --api-endpoint http://localhost:1234/v1
```

### Install for Development

```bash
git clone https://github.com/Kubementat/sokrates.git
cd sokrates
uv sync # for basic version
uv sync --all-extras # for voice support enabled version
```

### Optional Dependencies for Voice Features

```bash
# On macOS
brew install ffmpeg
brew install whisper-cpp

# On Ubuntu/Debian
sudo apt-get install ffmpeg
sudo apt-get install whisper-cpp
```

### Dependencies

The project includes the following key dependencies:
- **openai**: OpenAI API client for LLM interactions
- **psutil**: System monitoring and resource tracking
- **requests**: HTTP client for API calls
- **click**: Command-line interface framework
- **tabulate**: Table formatting for CLI output
- **colorama**: Terminal color support
- **markdownify**: HTML to Markdown conversion
- **openai-whisper**: Speech-to-text capabilities
- **pyaudio**: Audio input/output for voice features
- **dotenv**: Environment variable management
- **pytest**: Testing framework

## Configuration

You can configure the library via a configuration file in $HOME/.sokrates/.env

```
# Copy
cp .env.example $HOME/.sokrates/.env

# adjust to your needs
vim $HOME/.sokrates/.env
```

## Usage

### Basic Command Structure

Most commands follow this structure:
```bash
command --option1 value1 --option2 value2
```

You can always display the help via:
```
command --help

e.g.

uv run list-models --help
```

### Available Commands

#### Core LLM Operations
- `sokrates-list-models`: List available LLM models from your endpoint
- `sokrates-send-prompt`: Send a prompt to an LLM API
- `sokrates-chat`: Interactive chat interface with LLMs (supports voice mode)
- `sokrates-refine-prompt`: Refine prompts for better LLM performance
- `sokrates-refine-and-send-prompt`: Combine refinement and execution in one command

#### Task Management
- `sokrates-breakdown-task`: Break down complex tasks into manageable sub-tasks
- `sokrates-execute-tasks`: Execute tasks sequentially from JSON task lists
- `sokrates-task-add`: Add tasks to the background task queue
- `sokrates-task-list`: List queued tasks with status and priority
- `sokrates-task-status`: Check detailed status of specific tasks
- `sokrates-task-remove`: Remove tasks from the queue
- `sokrates-daemon`: Start/stop/restart the task queue daemon

#### Idea Generation & Content Creation
- `sokrates-idea-generator`: Generate ideas using multi-stage workflows with topic categorization
- `sokrates-generate-mantra`: Generate mantras or affirmations
- `sokrates-fetch-to-md`: Fetch web content and convert to markdown
- `sokrates-merge-ideas`: Merge multiple documents or ideas into a coherent output

#### Benchmarking & Analysis
- `sokrates-benchmark-model`: Benchmark LLM models with performance metrics
- `sokrates-benchmark-results-merger`: Merge multiple benchmark results
- `sokrates-benchmark-results-to-markdown`: Convert benchmark results to formatted markdown

### Task Queuing System

The task queue system allows you to queue LLM processing tasks in JSON format for reliable execution:

```bash
# Add a new task to the queue
sokrates-task-add tasks/new_task.json --priority high

# List all queued tasks
sokrates-task-list --status pending --priority high

# Get detailed status of specific task
sokrates-task-status task-123 --verbose

# Remove a task from the queue
sokrates-task-remove task-789 --force

# Start the daemon to process queued tasks
sokrates-daemon start

# Restart the daemon
sokrates-daemon restart

# Stop the daemon
sokrates-daemon stop
```

### Example Usage

#### Basic LLM Operations

```bash
# List available models
sokrates-list-models --api-endpoint http://localhost:1234/v1

# Send a simple prompt
sokrates-send-prompt --model qwen/qwen3-8b --prompt "Explain quantum computing in simple terms"

# Interactive chat with voice support
sokrates-chat --model qwen/qwen3-8b --voice  # Enable voice mode
sokrates-chat --model qwen/qwen3-8b --context-files ./docs/context.md

# Refine a prompt for better performance
sokrates-refine-prompt --prompt "Write a story about a robot" --model qwen/qwen3-8b
```

### sokrates-chat Commands

The sokrates-chat interface provides several special commands that enhance the chat experience:

#### `/voice`
Toggles between voice mode and text mode during the chat session.

- **Usage**: Type `/voice` in the chat interface
- **Description**: When enabled, voice mode allows you to speak your inputs instead of typing them. The system will use speech-to-text capabilities to transcribe your voice input. This requires the voice dependencies to be installed (FFmpeg and Whisper-cpp).
- **Example**:
  ```
  You: /voice
  [System message: Switched to voice mode.]
  ```

#### `/talk`
Enables text-to-speech functionality for the AI's responses.

- **Usage**: Type `/talk` in the chat interface
- **Description**: When activated, the AI will speak its responses aloud using text-to-speech capabilities. This is useful for hands-free interaction or when you prefer to listen rather than read the responses.
- **Example**:
  ```
  You: /talk
  [System message: Text-to-speech enabled for AI responses.]
  ```

#### `/add <Filepath>`
Adds additional context to the conversation from a file.

- **Usage**: Type `/add <path/to/file>` in the chat interface
- **Description**: Loads content from the specified file and adds it to the conversation history as a system message. This allows you to provide additional context or reference material during the conversation without restarting the chat.
- **Example**:
  ```
  You: /add ./docs/project-context.md
  [System message: Added context from ./docs/project-context.md]
  ```
- **Note**: The file path can be absolute or relative to the current working directory.

#### Task Management

```bash
# Break down a complex project into tasks
sokrates-breakdown-task --task "Build a web application for task management" --output project-tasks.json

# Execute the generated tasks sequentially
sokrates-execute-tasks --task-file project-tasks.json --output-dir ./results

# Add a task to the background queue
sokrates-task-add tasks/feature_request.json --priority high

# Start the task queue daemon
sokrates-daemon start

# Check task status
sokrates-task-status --task-id abc123 --verbose

# List all pending tasks
sokrates-task-list --status pending --priority high
```

#### Idea Generation & Content Creation

```bash
# Generate creative ideas with topic categorization
sokrates-idea-generator --topic "AI in healthcare" --output-dir ./healthcare-ideas --idea-count 5

# Generate mantras for motivation
sokrates-generate-mantra --count 3 --theme "productivity"

# Convert web content to markdown
sokrates-fetch-to-md --url "https://example.com/article" --output article.md
```

#### Idea Generation & Content Creation

```bash
# Generate creative ideas with topic categorization
sokrates-idea-generator --topic "AI in healthcare" --output-dir ./healthcare-ideas --idea-count 5

# Generate mantras for motivation
sokrates-generate-mantra -o my_mantra.md

# Convert web content to markdown
sokrates-fetch-to-md --url "https://example.com/article" --output article.md

# Merge multiple documents or ideas
sokrates-merge-ideas --source-documents 'docs/idea1.md,docs/idea2.md' --output-file merged-ideas.md
```

#### Benchmarking & Analysis

```bash
# Benchmark model performance
sokrates-benchmark-model --model qwen/qwen3-8b --iterations 10 --temperature 0.7

# Convert benchmark results to markdown
sokrates-benchmark-results-to-markdown --input benchmark_results.json --output benchmark_report.md
```

## Features

### 🚀 Core LLM Capabilities
- **Advanced Prompt Refinement**: Multi-stage prompt optimization with context awareness
- **Streaming Responses**: Real-time token streaming with performance metrics
- **Multi-model Support**: Compatible with any OpenAI-compatible LLM endpoint
- **Context Management**: Flexible context loading from files, directories, or text
- **Response Processing**: Intelligent cleaning and formatting of LLM outputs

### 🎯 Task Management & Workflows
- **Task Queue System**: Background task processing with SQLite persistence
- **Sequential Task Execution**: Complex multi-step task automation
- **Task Breakdown**: AI-powered task decomposition into manageable sub-tasks
- **Priority Queue**: Task prioritization and status tracking
- **Error Handling**: Comprehensive error recovery and logging

### 💬 Interactive Features
- **Voice-Enabled Chat**: Speech-to-text and text-to-speech capabilities using Whisper
- **Interactive CLI**: Rich command-line interface with colorized output
- **Conversation Logging**: Automatic chat history logging with timestamps
- **Context Switching**: Dynamic context addition during conversations

### 📊 System Monitoring & Analytics
- **Real-time Monitoring**: CPU, memory, and resource usage tracking
- **Performance Metrics**: Token generation speed, response times, and throughput
- **Benchmarking Tools**: Comprehensive model performance analysis
- **Logging Infrastructure**: Structured logging with configurable levels

### 🔧 Developer Tools
- **Modular Architecture**: Clean, extensible component design
- **Configuration Management**: Flexible environment-based configuration
- **File Management**: Comprehensive file handling utilities
- **Testing Framework**: Integrated pytest with comprehensive test coverage
- **Documentation**: Extensive inline documentation and examples

### 🎨 User Experience
- **Rich CLI Output**: Colorized, formatted output with progress indicators
- **Help System**: Comprehensive help and usage instructions for all commands
- **Error Handling**: User-friendly error messages and recovery suggestions
- **Cross-platform**: Works on macOS, Linux, and Windows

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository** and create a new branch for your feature
2. **Make your changes** with appropriate tests and documentation
3. **Run the test suite** to ensure everything works correctly
4. **Submit a pull request** with a clear description of your changes

### Development Setup

```bash
git clone https://github.com/Kubementat/sokrates.git
cd sokrates
uv sync
uv run pytest  # Run tests
```

### Guidelines

- Follow the existing code style and conventions
- Add tests for new functionality
- Update documentation for significant changes
- Ensure all existing tests pass

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contact

**Julian Weber** - Creator and Maintainer

- 📧 Email: [julianweberdev@gmail.com](mailto:julianweberdev@gmail.com)
- 🐙 GitHub: [@julweber](https://github.com/julweber)
- 💼 LinkedIn: [Julian Weber](https://www.linkedin.com/in/julianweberdev/)

**Project Links:**
- 🏠 Homepage: https://github.com/Kubementat/sokrates
- 📚 Documentation: See [docs/](docs/) directory for detailed documentation
- 🐛 Issues: [GitHub Issues](https://github.com/Kubementat/sokrates/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Kubementat/sokrates/discussions)

## Changelog

View our [CHANGELOG.md](CHANGELOG.md) for a detailed changelog.
