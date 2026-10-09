import os
import shutil
import gradio as gr
from agent import app

WORKSPACE_INPUT = os.path.join(os.path.dirname(__file__), "workspace", "input")
os.makedirs(WORKSPACE_INPUT, exist_ok=True)


def handle_pdf_upload(file):
    if not file:
        return None, "<p>No PDF loaded</p>"
    
    dest_path = os.path.join(WORKSPACE_INPUT, os.path.basename(file.name))
    shutil.copy(file.name, dest_path)
    
    # Use Gradio's internal file route to embed in an iframe
    pdf_html = f'<iframe src="/gradio_api/file={dest_path}" width="100%" height="700px" style="border:none;"></iframe>'
    return dest_path, pdf_html


def chat_with_agent(user_message, chat_history, active_pdf_path):
    if not user_message.strip():
        return "", chat_history

    if not active_pdf_path:
        bot_response = "Please upload a PDF on the left panel first."
    else:
        initial_state = {
            "messages": [("user", user_message)],
            "pdf_path": active_pdf_path,
        }
        result = app.invoke(initial_state)
        bot_response = result["messages"][-1].content

    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": bot_response})
    return "", chat_history


with gr.Blocks(title="PDF Sandbox Agent") as demo:
    active_pdf = gr.State(value=None)

    with gr.Row():
        # Left Panel: Native Uploader + Iframe Viewer
        with gr.Column(scale=1):
            gr.Markdown("### Document Preview")
            pdf_input = gr.File(
                label="Upload PDF",
                file_types=[".pdf"],
                type="filepath",
            )
            pdf_preview = gr.HTML(
                value="<p style='color: gray; text-align: center; padding-top: 100px;'>Upload a document to preview</p>"
            )

        # Right Panel: Chat Interface
        with gr.Column(scale=1):
            gr.Markdown("### Agent Chat")
            chatbot = gr.Chatbot(label="Conversation", height=650)
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Ask a question or request extraction...",
                    show_label=False,
                    scale=4,
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)

    # Handlers
    pdf_input.upload(
        fn=handle_pdf_upload,
        inputs=[pdf_input],
        outputs=[active_pdf, pdf_preview],
    )

    msg_input.submit(
        fn=chat_with_agent,
        inputs=[msg_input, chatbot, active_pdf],
        outputs=[msg_input, chatbot],
    )
    send_btn.click(
        fn=chat_with_agent,
        inputs=[msg_input, chatbot, active_pdf],
        outputs=[msg_input, chatbot],
    )

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860, allowed_paths=[WORKSPACE_INPUT])