# agents/factual_consistency_agent.py
import os
from openai import OpenAI

class FactualConsistencyAgent:
    description = "Verifies the factual accuracy of the article by cross-referencing its claims with external sources."

    def __init__(self):
        # Ensure the API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=api_key)

    # Define function to verify factual consistency
    def verify_facts(self, article_text):
        """
        Verify the factual accuracy of the article.
        :param article_text: The text of the article to analyze.
        :return: A string summarizing the factual consistency analysis.
        """
        # Prepare the article text as a prompt for the AI
        fact_check_prompt = (
            f"Analyze the following article for factual accuracy:\n"
            f"{article_text}\n"
            f"Identify any claims that are factually incorrect or unsupported, and provide explanations."
        )

        # Use OpenAI to verify the facts
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert in fact-checking and verifying claims."},
                {"role": "user", "content": fact_check_prompt},
            ],
            model="gpt-3.5-turbo",
        )
        chatgpt_reply = chat_completion.choices[0].message.content
        return chatgpt_reply

if __name__ == "__main__":
    # Example usage
    agent = FactualConsistencyAgent()
    example_article = (
        "The Eiffel Tower is located in Berlin, Germany. "
        "It was constructed in 1889 and is one of the most visited monuments in the world."
    )
    print(agent.verify_facts(example_article))