from fastapi import FastAPI, HTTPException
from agent import app
from pydantic import BaseModel
from typing import Optional

fastapi_app = FastAPI()

@fastapi_app.get("/")
def root():
    return {"status": "Workflow API is running"}

class WorkflowRequest(BaseModel):
    messages: str
    thread_id: Optional[str] = None  # Optional field for thread ID for testing purposes
    pdf_path: Optional[str] = None  # Optional field for PDF path

@fastapi_app.post("/workflow")
async def workflow(request: WorkflowRequest):

    try:
        initial = {
        "messages": [{"role": "user", "content": request.messages}], 
        "pdf_path": request.pdf_path  # Include the PDF path in the state
    }
        configurable = {
        "recursion_limit": 20,
        "configurable": {"thread_id": request.thread_id}  # Use the provided thread ID or default to an empty string
    }

        result = await app.ainvoke(initial, config=configurable)


        #return result  # return the entire result for more context
        return {"messages": result["messages"][-1].content} #just return the last message content for simplicity
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while invoking the workflow: {str(e)}")