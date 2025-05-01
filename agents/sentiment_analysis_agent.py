# agents/sentiment_analysis_agent.py
import os
from openai import OpenAI

class SentimentAnalysisAgent:
    description = "Analyzes the sentiment of the article, providing a quick overview of sentiment bias and emotional tone."

    def __init__(self):
        # Ensure the API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=api_key)

    def analyze_sentiment(self, article_text):
        """
        Analyze the sentiment of the article and provide brief, actionable metrics.
        :param article_text: The text of the article to analyze.
        :return: A dictionary summarizing the sentiment analysis.
        """
        # Updated system prompt
        system_prompt_sentiment = (
            "You are an expert in sentiment analysis. "
            "Your task is to evaluate the tone of the provided article and provide a brief summary. "
            "Focus on identifying the overall sentiment (positive, negative, or neutral), sentiment bias, and emotional tone. "
            "Provide the output in the following format:\n\n"
            "Overall Tone: <Positive/Negative/Neutral>\n"
            "Sentiment Bias Score: <0-100>\n"
            "Key Highlights: <List of emotionally charged phrases or sections>\n"
            "Impact: <Brief description of how the sentiment might influence readers>"
        )

        # Updated user prompt
        user_prompt_sentiment = (
            f"Analyze the sentiment of the following article:\n\n"
            f"{article_text}\n\n"
            f"Provide your evaluation in the specified format."
        )

        # Use OpenAI to analyze sentiment
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt_sentiment},
                {"role": "user", "content": user_prompt_sentiment},
            ],
            model="gpt-3.5-turbo",
        )
        chatgpt_reply = chat_completion.choices[0].message.content

        # Parse the response into a structured format with error handling
        response_lines = chatgpt_reply.split("\n")
        result = {
            "Overall Tone": self._extract_value(response_lines, 0, "Overall Tone"),
            "Sentiment Bias Score": self._extract_value(response_lines, 1, "Sentiment Bias Score"),
            "Key Highlights": self._extract_value(response_lines, 2, "Key Highlights"),
            "Impact": self._extract_value(response_lines, 3, "Impact"),
        }
        return result

    def _extract_value(self, response_lines, index, key):
        """
        Safely extract a value from the response lines.
        :param response_lines: List of response lines.
        :param index: Index of the line to extract.
        :param key: Expected key for the line.
        :return: Extracted value or a default message if the line is missing or malformed.
        """
        if index < len(response_lines):
            parts = response_lines[index].split(": ", 1)
            if len(parts) == 2 and parts[0].strip() == key:
                return parts[1].strip()
        return "Unknown"

if __name__ == "__main__":
    # Example usage
    agent = SentimentAnalysisAgent()
    example_article = (
        "The Democratic Party continues to push its reckless policies, ignoring the needs of hardworking Americans. "
        "Their so-called 'progressive' agenda is nothing more than a thinly veiled attempt to impose socialism on the country. "
        "Democrats have repeatedly failed to address rising inflation, leaving families struggling to make ends meet. "
        "Their obsession with raising taxes is driving businesses out of the country, killing jobs, and stifling innovation. "
        "Meanwhile, their open-border policies have created chaos, allowing criminals and drugs to pour into our communities. "
        "It’s clear that the Democratic Party is more focused on pandering to radical activists than solving real problems. "
        "America deserves better than the failed leadership and dangerous ideas of the Democrats."
    )
    result = agent.analyze_sentiment(example_article)
    print("Sentiment Analysis Summary:")
    for key, value in result.items():
        print(f"{key}: {value}")