import gradio as gr
from backend.main import app as fastapi_app

# Create a dummy Gradio interface just to satisfy Hugging Face's health checks
demo = gr.Interface(
    fn=lambda: "MietShield Backend is running!", 
    inputs=None, 
    outputs="text",
    title="MietShield API"
)

# Mount the dummy Gradio app onto our existing FastAPI application.
# This tricks Hugging Face into hosting our FastAPI app for free.
app = gr.mount_gradio_app(fastapi_app, demo, path="/")
