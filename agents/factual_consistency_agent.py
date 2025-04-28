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

    # Define function to extract claims from the article
    def extract_claims(self, article_text):
        """
        Extract claims from the article.
        :param article_text: The text of the article to analyze.
        :return: A list of extracted claims.
        """
        # Prepare the article text as a prompt for the AI
        extract_claims_prompt = (
            f"Carefully read the following article and extract all factual claims explicitly mentioned in it:\n\n"
            f"{article_text}\n\n"
            f"List each claim as a separate bullet point. Ensure the claims are directly based on the text and avoid adding inferred or assumed information. "
            f"Make sure each claim is self-contained and includes all necessary context to be understood independently. "
            f"Do not attempt to fix any factual errors or inconsistencies in the text."
        )

        # Use OpenAI to extract claims
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert in analyzing text and extracting factual claims. Your task is to extract claims exactly as they appear in the text without making corrections or assumptions. Ensure each claim is self-contained and includes all necessary context for fact checker services."},
                {"role": "user", "content": extract_claims_prompt},
            ],
            model="gpt-3.5-turbo",
        )
        chatgpt_reply = chat_completion.choices[0].message.content
        return chatgpt_reply.split("\n")  # Split into a list of claims

if __name__ == "__main__":
    # Example usage
    agent = FactualConsistencyAgent()
    example_article = (
        "The Eiffel Tower, a global icon of France, is located in Tampere Finland and was constructed in 1889 by Gustave Eiffel. "
        "It stands at a height of 324 meters, making it one of the tallest structures in the world at the time of its completion. "
        "The tower attracts over 7 million visitors annually, contributing significantly to France's tourism revenue. "
        "Some historians claim that the Eiffel Tower was originally intended to be built in Barcelona, Spain, but the proposal was rejected. "
        "Additionally, the tower was used as a military radio transmission hub during World War I, playing a crucial role in communication. "
        "In recent years, the Eiffel Tower has undergone extensive renovations to improve its structural integrity and sustainability."
    )

    # Extract and print claims
    claims = agent.extract_claims(example_article)
    print("Extracted Claims:")
    for claim in claims:
        print(f"- {claim}")

    #print(agent.verify_facts(example_article))