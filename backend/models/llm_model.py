# backend/models/llm_model.py
import os
from ..utils.logger import get_logger

logger = get_logger("LocalLLM")

# Try llama-cpp-python first (fast local gguf) else use huggingface transformers pipeline
def try_import(name):
    try:
        module = __import__(name)
        return module
    except Exception:
        return None

class LocalLLM:
    def __init__(self):
        self.model = None
        # prefer llama-cpp-python if available & model path provided
        try:
            from llama_cpp import Llama
            model_path = os.environ.get("LLAMA_MODEL_PATH")  # set in your env or utils/config.py
            if model_path and os.path.exists(model_path):
                logger.info("Loading llama-cpp-python model...")
                self.model = Llama(model_path=model_path, n_threads=6)
                self.mode = "llama_cpp"
                return
        except Exception:
            pass

        # fallback to transformers text-generation pipeline (if installed)
        try:
            from transformers import pipeline
            model_name = os.environ.get("HF_TEXT_MODEL", "gpt2")
            logger.info(f"Loading transformers model pipeline ({model_name})...")
            self.pipe = pipeline("text-generation", model=model_name, device_map="auto" if try_import("torch") else None)
            self.mode = "transformers"
        except Exception as e:
            logger.error(f"No LLM available: {e}")
            self.mode = None

    def generate_text(self, prompt, max_tokens=200, temperature=0.7):
        if self.mode == "llama_cpp":
            out = self.model(prompt, max_tokens=max_tokens, temperature=temperature)
            return out["choices"][0]["text"]
        elif self.mode == "transformers":
            outs = self.pipe(prompt, max_new_tokens=max_tokens, do_sample=True, temperature=temperature)
            return outs[0]["generated_text"]
        else:
            raise RuntimeError("No local LLM available. Install llama-cpp-python or transformers.")
