import requests
import json
import gradio as gr

url = "http://localhost:11434/api/generate"

headers = {
    'Content-Type': 'application/json',
}

# Start history as list of messages with roles
history = [
    {"role": "assistant", "content": "Hi there! I'm Gemma, a large language model created by Gayatri Sutar. I’m an open-weights model, widely available for public use!\n\nIt’s nice to meet you! 😊"}
]

def generate_response(message, chat_history):
    # chat_history is a list of dicts with role and content
    if chat_history is None:
        chat_history = []

    # Append user message
    chat_history.append({"role": "user", "content": message})

    # Create prompt from chat history
    prompt = ""
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "Bot"
        prompt += f"{role}: {msg['content']}\n"

    data = {
        "model": "gemma3",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        bot_reply = f"⚠️ Request failed: {e}"
        chat_history.append({"role": "assistant", "content": bot_reply})
        return "", chat_history

    try:
        data = response.json()
        bot_reply = data.get('response', '⚠️ No response from model')
    except json.JSONDecodeError:
        bot_reply = f"⚠️ Invalid JSON: {response.text}"

    # Append bot reply
    chat_history.append({"role": "assistant", "content": bot_reply})

    return "", chat_history


with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue")) as demo:
    gr.Markdown("<h1 style='text-align: center;'>💬 My AI Chatbot</h1>")
    gr.Markdown("Type your question below and get instant responses from **Gemma3** running on Ollama!")

    chatbot = gr.Chatbot(value=history, height=400, avatar_images=("👤", "🤖"), type="messages")
    msg = gr.Textbox(placeholder="Hey, tell me what you want to know...", label="Your Message")
    clear = gr.Button("🗑️ Clear Chat")

    msg.submit(generate_response, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: (None, history), None, [msg, chatbot])

demo.launch()
