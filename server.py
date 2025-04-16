from flask import Flask, request, jsonify
import logging
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
import uuid
import re

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Load GPT-2 model and tokenizer ONCE at startup
class FastGPT2:
    def __init__(self):
        self.model_dir = "capcutgpt"  # Change to your model path or "gpt2"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = GPT2TokenizerFast.from_pretrained(self.model_dir)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        # Use half precision if possible for speed
        torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.model = GPT2LMHeadModel.from_pretrained(
            self.model_dir,
            torch_dtype=torch_dtype
        ).to(self.device)
        self.model.eval()
        logger.info(f"Model loaded on {self.device}")

    def generate(self, prompt):
        # Shorten prompt and limit output for speed
        prompt = prompt.strip()[:200]
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=200,
            truncation=True
        ).to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=32,  # Shorter output for speed
                do_sample=False,    # Greedy decoding (fastest)
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove prompt from response if present
        if response.startswith(prompt):
            response = response[len(prompt):].strip()
        return response if response else "Sorry, I couldn't generate a response."

# Initialize model
try:
    gpt2 = FastGPT2()
except Exception as e:
    logger.error(f"Model failed to load: {e}")
    gpt2 = None

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request"}), 400
    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    if not gpt2:
        return jsonify({"error": "Model unavailable"}), 503
    # Clean input
    cleaned = re.sub(r"[^\w\s\?]", "", user_message.lower()).strip()
    # Fast prompt
    prompt = f"User: {cleaned}\nAssistant:"
    try:
        response = gpt2.generate(prompt)
        return jsonify({
            "response": response,
            "session_id": str(uuid.uuid4())
        })
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({"error": "Processing failed"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model_loaded": gpt2 is not None})

if __name__ == "__main__":
    # Use threaded=True for concurrent requests
    app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)
