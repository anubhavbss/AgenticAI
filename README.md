# OpenAI GitHub Workflow Generator

This Python project uses the OpenAI API to generate an OpenTofu GitHub Actions workflow from a natural-language prompt.

## What It Does

The script:

1. Loads the OpenAI API key from a `.env` file.
2. Checks whether the API key exists.
3. Creates an OpenAI client.
4. Sends a request to the AI model.
5. Receives and prints the generated response.

The example prompt asks the AI to create a workflow that:

* Requires Pull Request (PR) approval before merging into the `main` branch.
* Deploys only after the approved PR has been merged into `main`.

## Requirements

* Python
* `uv`
* OpenAI API key

## Installation

Install the required packages:

```bash
uv add openai python-dotenv
```

## Environment Setup

Create a `.env` file in your project folder:

```text
OPENAI_API_KEY=your_api_key_here
```

Add `.env` to your `.gitignore` file:

```text
.env
```

**Never commit your API key to GitHub.**

## Running the Script

Run the application using:

```bash
uv run python main.py
```

## Important Note

The AI generates text as a response. Asking the AI to save a file on your computer does not automatically create that file.

To save the generated workflow, your Python code must explicitly write it to a file.

## Project Structure

```text
project/
├── lab1.py
├── .env
├── .gitignore
├── README.md
└── pyproject.toml
```

## Learning Outcomes

This project demonstrates how to:

* Use environment variables in Python.
* Protect API keys using `.env` and `.gitignore`.
* Use the OpenAI Python library.
* Send prompts to an AI model.
* Process and display AI-generated responses.
* Build simple AI-powered Python applications.
