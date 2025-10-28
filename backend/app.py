# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ❌ Purane imports hatao
# from .scraper import extract_product_info
# from .prompt_generator import generate_prompts_for_product

# ✅ Naye imports (without dot)
import scraper
import prompt_generator
from models.text2video_api import Text2VideoAPI
from utils.logger import get_logger

# Initialize logger
logger = get_logger("Main")

# Initialize FastAPI app
app = FastAPI(title="AI Shopping Video Assistant")

# Allow frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize video generator
video_api = Text2VideoAPI()

# --- Input Models ---
class LinkIn(BaseModel):
    product_link: str

class PromptIn(BaseModel):
    product_link: str
    selected_style: str

# --- Routes ---
@app.get("/")
async def root():
    return {"message": "✅ AI Shopping Video Assistant Backend is running!"}

@app.post("/generate_prompts")
async def gen_prompts(payload: LinkIn):
    product = scraper.extract_product_info(payload.product_link)
    prompts = prompt_generator.generate_prompts_for_product(product)
    return {"product": product, "prompts": prompts}

@app.post("/generate_video")
async def gen_video(payload: PromptIn):
    product = scraper.extract_product_info(payload.product_link)
    prompts = prompt_generator.generate_prompts_for_product(product)
    
    style_key = payload.selected_style
    if style_key not in prompts:
        return {"error": "Invalid style selected", "available": list(prompts.keys())}
    
    prompt_text = prompts[style_key]
    logger.info(f"🎬 Generating video for style = {style_key}")
    video_url = video_api.generate_video(prompt_text, product)
    return {"video_url": video_url}