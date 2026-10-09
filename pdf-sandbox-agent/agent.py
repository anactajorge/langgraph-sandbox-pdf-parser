from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv  
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
import subprocess
from langchain_core.rate_limiters import InMemoryRateLimiter
from pathlib import Path
import os

load_dotenv()

WORKSPACE_PATH = Path(__file__).parent / "workspace"
SCRIPT_PATH = WORKSPACE_PATH / "script.py"

# This configuration guarantees the application stays under a 15 RPM cap.
rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.07,      
    check_every_n_seconds=0.5,     
    max_bucket_size=1              
)

# Initialize the LLMs with rate limiting and retry logic
llm = ChatGoogleGenerativeAI( # more logical but not generous for RPM especially for free plan limited to 5RPM and 20RPD
    model="gemini-2.5-flash", 
    rate_limiter=rate_limiter,
    max_retries=3,
)
llm2 = ChatGroq( # more generous for RPM but might lack logic 
    model = "openai/gpt-oss-120b",
    rate_limiter=rate_limiter,
    max_retries=3,
)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    pdf_path: str # Added to track the path of the uploaded PDF file so it can handle names Dynamically

@tool
def execute_script(script: str) -> str:
    """
    Writes a Python script to workspace/script.py, executes it inside 
    the isolated Docker container, and returns the terminal output.
    """
    WORKSPACE_PATH.mkdir(parents=True, exist_ok=True)

    with open(SCRIPT_PATH, "w", encoding="utf-8") as f:
        f.write(script)

    cmd = [
        "docker", "run", "--rm",
        "--network", "none",
        "--memory=1g",
        "--cpus=1.0",
        "--pids-limit", "100",
        "--cap-drop=ALL",
        "-v", f"{WORKSPACE_PATH.resolve()}:/workspace",
        "pdf-sandbox",
        "python", "/workspace/script.py"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",  # Prevents decode crashes on malformed PDF characters
            timeout=30  
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            return f"Execution Error (Exit code {result.returncode}):\n{stderr if stderr else stdout}"

        if not stdout:
            return "Script executed successfully, but produced no terminal output."

        return f"Script Output:\n{stdout}"

    except subprocess.TimeoutExpired:
        return "Error: Script execution timed out after 30 seconds."
    except Exception as e:
        return f"Host error while attempting to run Docker: {str(e)}"

tools = [execute_script]
tool_node = ToolNode(tools)
llm_with_tools = llm2.bind_tools(tools)

# 3. Renamed function to avoid shadowing 'llm'
def agent_node(State: AgentState):
    pdf_file = State.get("pdf_path", "sample.pdf")
    filename = os.path.basename(pdf_file)

    system_prompt = SystemMessage(
        content=f"""You are an isolated PDF parser. The PDF is located at '/workspace/input/{filename}'. 
        Available libraries in the sandbox: pypdf, pdfplumber, pymupdf, pytesseract, PIL. 
        Use the execute_script tool to inspect the document and print your findings. 
        If you encounter a runtime error, inspect the traceback, fix the script, and run it again."""
    )
    
    messages = [system_prompt] + list(State["messages"])
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node) # Updated reference
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {"tools": "tools", END: END}
)

workflow.add_edge("tools", "agent")

app = workflow.compile()

# CLI entry point for testing the agent in a terminal environments
"""def running_agent():
    print("\nPDF Sandbox Agent is running. Type 'exit' or 'quit' to stop.")
    
    while True:
        user_input = input("\nWhat is your question: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        messages = [HumanMessage(content=user_input)] 

        result = app.invoke({"messages": messages})
        
        print("\n=== ANSWER ===")
        print(result['messages'][-1].content)

if __name__ == "__main__":
    running_agent()"""