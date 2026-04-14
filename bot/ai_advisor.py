import os
import openai
from dotenv import load_dotenv
from .logging_config import get_logger

logger = get_logger(__name__)
load_dotenv()

class AIAdvisor:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
            self.is_available = True
            logger.info("AIAdvisor initialized successfully.")
        else:
            self.is_available = False
            logger.warning("OPENAI_API_KEY not found. AIAdvisor is unavailable.")

    def analyze_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None) -> str:
        if not self.is_available:
            return "AI advisor unavailable (no API key set)"

        prompt = (f"I am about to place a {side} {order_type} order for {quantity} {symbol} ")
        if price:
            prompt += f"at price {price} "
        prompt += "on Binance Futures Testnet. Give me a 2-sentence risk summary and one key thing to watch out for."

        logger.info(f"AI Request (analyze_order): {prompt}")

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional cryptocurrency trading advisor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            ai_text = response.choices[0].message.content.strip()
            logger.info(f"AI Response (analyze_order): {ai_text}")
            return ai_text
        except Exception as e:
            logger.error(f"OpenAI API Error (analyze_order): {str(e)}")
            return f"AI advisor encountered an error: {str(e)}"

    def explain_order_result(self, order_response: dict) -> str:
        if not self.is_available:
            return "AI advisor unavailable (no API key set)"

        prompt = (f"I just placed an order on Binance. Here is the response data: {order_response}. "
                  "Explain what happened with this order in plain English in 2-3 sentences.")

        logger.info(f"AI Request (explain_order_result): {prompt}")

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful trading assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            ai_text = response.choices[0].message.content.strip()
            logger.info(f"AI Response (explain_order_result): {ai_text}")
            return ai_text
        except Exception as e:
            logger.error(f"OpenAI API Error (explain_order_result): {str(e)}")
            return f"AI advisor encountered an error: {str(e)}"
