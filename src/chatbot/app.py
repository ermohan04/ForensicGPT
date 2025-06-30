import gradio as gr
import base64
from chatbot import ask_forensicgpt  # your existing chatbot function


def file_to_data_url(file_obj):
    """
    Converts an uploaded file to a base64-encoded data URL string with mime type,
    so Gradio can display it inline as an image.
    """
    if file_obj is None:
        return None

    with open(file_obj.name, "rb") as f:
        encoded_bytes = base64.b64encode(f.read())
    encoded_str = encoded_bytes.decode("utf-8")

    ext = file_obj.name.split(".")[-1].lower()
    if ext == "png":
        mime = "image/png"
    elif ext == "jpg" or ext == "jpeg":
        mime = "image/jpeg"
    else:
        # unsupported files like pdf, just ignore for display
        return None

    # Build data URL string
    data_url = f"data:{mime};base64,{encoded_str}"
    return data_url


def respond(chat_history, user_text, uploaded_files, mic_audio):
    if chat_history is None:
        chat_history = []

    text = (user_text or "").strip()
    has_voice = mic_audio is not None
    has_images = uploaded_files is not None and len(uploaded_files) > 0

    # Make a copy of chat history to avoid mutating input directly
    history = chat_history.copy()

    # Case 1: User only uploads images (no text or voice)
    if not text and has_images and not has_voice:
        for f in uploaded_files:
            data_url = file_to_data_url(f)
            if data_url:
                # Add an image message from user to chat history
                history.append(
                    {
                        "role": "user",
                        "content": {"type": "image", "image": data_url},
                    }
                )
        # Assistant replies asking what to do with the images
        history.append(
            {
                "role": "assistant",
                "content": "Thanks for the image(s). How can I help you with this?",
            }
        )

    # Case 2: User types text (may also upload images or voice)
    elif text:
        # Add user's text message
        history.append({"role": "user", "content": text})

        # Add any uploaded images as user messages
        if has_images:
            for f in uploaded_files:
                data_url = file_to_data_url(f)
                if data_url:
                    history.append(
                        {
                            "role": "user",
                            "content": {"type": "image", "image": data_url},
                        }
                    )

        # Indicate if user sent voice message
        if has_voice:
            history.append({"role": "user", "content": "[User sent a voice message]"})

        # Get assistant's reply from your chatbot function
        bot_reply = ask_forensicgpt(text)
        history.append({"role": "assistant", "content": bot_reply})

    # Case 3: No input, greet the user
    else:
        history.append(
            {
                "role": "assistant",
                "content": "Hello! How can I assist you with blood spatter analysis today?",
            }
        )

    # Return updated chat history and reset input fields
    return history, "", None, None


with gr.Blocks(title="ForensicGPT") as demo:
    gr.Markdown("# ForensicGPT Chat")

    chatbot = gr.Chatbot(
        label="ForensicGPT Chatbot",
        type="messages",  # Important: this expects messages as dicts with 'role' and 'content'
    )

    with gr.Row():
        txt = gr.Textbox(
            placeholder="Type your question or upload images/voice...",
            show_label=False,
            lines=1,
            max_lines=5,
        )
        file_upload = gr.File(
            file_types=[".png", ".jpg", ".jpeg"],
            label="Upload images",
            file_count="multiple",
        )
        mic = gr.Audio(label="Record voice", type="numpy")
        send_btn = gr.Button("Send")

    # Connect input components to respond function
    txt.submit(
        respond,
        inputs=[chatbot, txt, file_upload, mic],
        outputs=[chatbot, txt, file_upload, mic],
    )
    send_btn.click(
        respond,
        inputs=[chatbot, txt, file_upload, mic],
        outputs=[chatbot, txt, file_upload, mic],
    )


if __name__ == "__main__":
    demo.launch(debug=True)
