# agents/sentiment_analysis_agent.py
import os
from openai import OpenAI

class SentimentAnalysisAgent:
    description = "Analyzes the sentiment of the article, identifying whether the tone is positive, negative, or neutral."

    def __init__(self):
        # Ensure the API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=api_key)

    # Define function to analyze sentiment
    def analyze_sentiment(self, article_text):
        """
        Analyze the sentiment of the article.
        :param article_text: The text of the article to analyze.
        :return: A string summarizing the sentiment analysis.
        """
        # Prepare the article text as a prompt for the AI
        sentiment_analysis_prompt = (
            f"Analyze the sentiment of the following article:\n"
            f"{article_text}\n"
            f"Determine whether the tone is positive, negative, or neutral, and provide a detailed explanation."
        )

        # Use OpenAI to analyze sentiment
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert in sentiment analysis."},
                {"role": "user", "content": sentiment_analysis_prompt},
            ],
            model="gpt-3.5-turbo",
        )
        chatgpt_reply = chat_completion.choices[0].message.content
        return chatgpt_reply

if __name__ == "__main__":
    # Example usage
    agent = SentimentAnalysisAgent()
    example_article = (
        "The new policy has been met with widespread praise from citizens, who describe it as a step in the right direction. "
        "However, some critics argue that it does not go far enough to address the underlying issues."
    )
    print(agent.analyze_sentiment(example_article))