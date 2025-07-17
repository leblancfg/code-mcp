# Code MCP Server

An MCP (Model Context Protocol) server that provides code interpretation capabilities via Google Cloud Functions.

## Features

- Execute Python, JavaScript, and Bash code in a sandboxed environment
- Automatic deployment to Google Cloud Functions
- STDIO-based MCP server implementation

## Prerequisites

- Python 3.11+
- Google Cloud SDK (`gcloud`) installed and configured
- A Google Cloud Project with Cloud Functions API enabled

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

### As an MCP Server

```bash
python main.py
```

### Running Tests

```bash
pytest
```

### Testing with the MCP Inspector
You can use the CLI feature with

```console
$ GCF_URL=$MY_COOL_GCF_URL \
npx @modelcontextprotocol/inspector@0.11.0 \
--cli uv run python main.py \
--method tools/call \
--tool-name run_code \
--tool-arg "code=print(1+1)" \
--tool-arg language=python \
| jq
```

## Configuration

Set the `GCF_URL` environment variable to use an existing Cloud Function, otherwise the server will attempt to deploy one automatically.

```bash
export GCF_URL="https://region-project.cloudfunctions.net/code-interpreter"
```

## Architecture

- **MCP Server**: Handles tool requests from AI agents
- **Google Cloud Function**: Executes code in an isolated environment
- **Supported Languages**: Python, JavaScript (Node.js), Bash
