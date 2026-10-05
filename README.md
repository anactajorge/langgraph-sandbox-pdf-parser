# PDF Sandbox Agent: Project Layout and Workflow

## Project layout

```text
pdf-sandbox-agent/
├── agent.py                 # LangGraph host logic
├── requirements.txt         # Host dependencies (LangGraph, Docker SDK)
├── .env                     # Private host API keys (kept out of container)
├── Dockerfile               # Sandbox definition with pre-installed PDF libraries
└── workspace/               # Mounted folder shared with container
    ├── input/               # User-uploaded PDFs
    ├── output/              # Extracted JSON, CSVs, or parsed text
    └── script.py            # Agent-generated parsing code
```

## Workflow

```mermaid
flowchart LR
    A([Start]) --> B["User PDF and query"]
    B --> C["LangGraph agent generates script"]
    C --> D["Docker / OrbStack sandbox runs script"]
    D --> E{"Need another run?"}
    E -- "Yes" --> C
    E -- "No" --> F([End: answer user])
```

**In simple terms:** LangGraph generates a script for the PDF, and OrbStack runs it. The result returns to LangGraph if another run is needed; otherwise, the agent answers the user and ends.

The `workspace/` folder lets the Mac host and the container access the same PDF and generated script. Keep the API key in the host's `.env`; the sandbox only needs the PDF, script via input folder, and any packages required to run the script.

--
## Current Status
- Created Graph and Sandbox Logic.
- TO use: input pdf to input folder.
- Accurately extracts contents (You can see the live code in script.py).

## Limitations 
- Should also create a tool for finding files and folders in the workspace folder. 
- Current approach: static system prompts for file/folder names.
- GPT-OSS-120b is smart but is stingy in outputs.
