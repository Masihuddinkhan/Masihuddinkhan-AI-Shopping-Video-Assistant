# backend/prompt_generator.py
from models.llm_model import LocalLLM
from utils.logger import get_logger

logger = get_logger("PromptGen")
llm = LocalLLM()

STYLES = {
    "Zenji": "Minimal, mindful, playful marketing tone for young professionals and lifestyle-focused customers.",
    "Age_30_45": "Balanced, mature, family & career-friendly marketing tone for ages 30 to 45.",
    "Corporate": "Polished, premium, productivity-focused marketing pitch for corporate professionals."
}

def build_prompt_base(product):
    base = f"Product: {product.get('title','')}\nDescription: {product.get('description','')}\nPrice: {product.get('price','')}\n"
    return base

def generate_prompts_for_product(product):
    base = build_prompt_base(product)
    outputs = {}
    for key, style in STYLES.items():
        prompt = (
            f"{base}\nWrite a short marketing script (2-3 lines) suitable for a promotional "
            f"short video targeted at the following audience: {style}\n"
            f"Keep it punchy, mention key benefits, include 1 CTA. Return only the script text."
        )
        try:
            text = llm.generate_text(prompt, max_tokens=250, temperature=0.7)
        except Exception as e:
            logger.error(f"LLM error for {key}: {e}")
            text = f"(LLM error) {product.get('title','')}"
        outputs[key] = text.strip()
    return outputs