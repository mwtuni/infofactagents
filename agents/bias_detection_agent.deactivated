# agents/bias_detection_agent.py
import os
from openai import OpenAI

class BiasDetectionAgent:
    description = "Analyzes the language of the article to detect potential bias."

    def __init__(self):
        # Ensure the API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=api_key)

    # Define function to detect bias
    def detect_bias(self, article_text):
        """
        Analyze the article for potential bias in language.
        :param article_text: The text of the article to analyze.
        :return: A string summarizing the bias analysis.
        """
        # Prepare the article text as a prompt for the AI
        bias_detection_prompt = (
            f"Analyze the following article for potential bias:\n"
            f"{article_text}\n"
            f"Identify any emotionally charged language, one-sided arguments, or lack of neutrality. "
            f"Provide a detailed explanation of the detected bias."
        )

        # Use OpenAI to detect bias
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert in detecting bias in written content."},
                {"role": "user", "content": bias_detection_prompt},
            ],
            model="gpt-3.5-turbo",
        )
        chatgpt_reply = chat_completion.choices[0].message.content
        return chatgpt_reply

if __name__ == "__main__":
    # Example usage
    agent = BiasDetectionAgent()
    example_article = (
        "The government has once again failed to deliver on its promises, leaving citizens frustrated and hopeless. "
        "Critics argue that this administration is the worst in decades, with no regard for the people's needs."
    )
    print(agent.detect_bias(example_article))