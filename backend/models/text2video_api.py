# backend/models/text2video_api.py
import requests
from ..utils.config import VIDEO_API_CONFIG, VIDEO_OUTPUT_DIR
from ..utils.logger import get_logger
import os, time

logger = get_logger("Text2VideoAPI")

class Text2VideoAPI:
    def __init__(self):
        # VIDEO_API_CONFIG from utils/config.py (api_key, provider_url, provider_name)
        self.config = VIDEO_API_CONFIG
        os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)

    def generate_video(self, prompt_text, product):
        """
        Generic wrapper that calls an external T2V API.
        You must configure provider and API key in backend/utils/config.py.
        This method returns a public URL or local file path (string).
        """
        provider = self.config.get("provider", "mock")
        if provider == "mock":
            # create dummy file for local testing
            fname = f"video_{int(time.time())}.txt"
            path = os.path.join(VIDEO_OUTPUT_DIR, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write("MOCK VIDEO\n")
                f.write("Product: " + product.get("title","") + "\n\n")
                f.write(prompt_text)
            logger.info(f"Mock video created: {path}")
            return f"/static/{os.path.basename(path)}"
        # Example for Pika / other provider (pseudo)
        elif provider == "pika":
            url = self.config["endpoint"]
            headers = {"Authorization": f"Bearer {self.config['api_key']}", "Content-Type":"application/json"}
            payload = {"prompt": prompt_text, "image": product.get("image"), "duration": 12}
            resp = requests.post(url, json=payload, headers=headers, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            # provider likely returns job id or url — adapt accordingly
            return data.get("video_url") or data.get("result_url")
        else:
            raise NotImplementedError("Provider not implemented. Configure in utils/config.py")
