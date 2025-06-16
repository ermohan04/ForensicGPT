# src/chatbot/app.py

import gradio as gr
from chatbot import ask_forensicgpt

iface = gr.Interface(
    fn=ask_forensicgpt,
    inputs=gr.Textbox(
        lines=2, placeholder="Ask a forensic question about blood spatter..."
    ),
    outputs="text",
    title="🧬 ForensicGPT",
    description="Ask forensic questions related to blood spatter pattern analysis. Powered by GPT.",
)

if __name__ == "__main__":
    iface.launch()
