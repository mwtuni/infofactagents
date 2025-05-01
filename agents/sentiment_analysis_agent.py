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

    def add_icons_to_analysis(self, analysis_text):
        """
        Add icons to the analysis text based on sentiment and bias scores.
        :param analysis_text: The raw analysis text from OpenAI.
        :return: The analysis text with icons added.
        """
        lines = analysis_text.split("\n")
        updated_lines = []
        for line in lines:
            if "Overall Tone: Positive" in line:
                updated_lines.append(f"✅ {line}")
            elif "Overall Tone: Neutral" in line:
                updated_lines.append(f"🔍 {line}")
            elif "Overall Tone: Negative" in line:
                updated_lines.append(f"❌ {line}")
            elif "Sentiment Bias Score:" in line:
                score = int(line.split(":")[1].strip())
                if score < 30:
                    updated_lines.append(f"✅ {line}")
                elif 30 <= score < 70:
                    updated_lines.append(f"⚠️ {line}")
                else:
                    updated_lines.append(f"❌ {line}")
            elif "Impact:" in line:
                updated_lines.append(f"🔍 {line}")
            else:
                updated_lines.append(line)
        return "\n".join(updated_lines)

    def process_article(self, article_text):
        """
        Analyze the sentiment of the article and provide a structured output.
        :param article_text: The text of the article to analyze.
        :return: A formatted string summarizing the sentiment analysis.
        """
        # Updated system prompt
        system_prompt_sentiment = (
            "You are an expert in sentiment analysis. "
            "Your task is to evaluate the tone of the provided article and provide a structured summary. "
            "Focus on identifying the overall sentiment (positive, negative, or neutral), sentiment bias, and emotional tone. "
            "Provide the output in the following format:\n\n"
            "Overall Tone: <Positive/Negative/Neutral>\n"
            "Sentiment Bias Score: <0-100>\n"
            "Key Highlights:\n"
            "- <Highlight 1>\n"
            "- <Highlight 2>\n"
            "Impact: <Brief description of how the sentiment might influence readers>\n"
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

        # Add icons to the analysis
        analysis_with_icons = self.add_icons_to_analysis(chatgpt_reply)

        # Return the formatted response
        return f"### Sentiment Analysis\n\n{analysis_with_icons}"

if __name__ == "__main__":
    # Example usage
    agent = SentimentAnalysisAgent()
    example_article = (
        "The Democratic Party continues to push its reckless policies, ignoring the needs of hardworking Americans. "
        "Their so-called 'progressive' agenda is nothing more than a thinly veiled attempt to impose socialism on the country. "
        "Democrats have repeatedly failed to address rising inflation, leaving families struggling to make ends meet. "
        "Their obsession with raising taxes is driving businesses out of the country, killing jobs, and stifling innovation. "
        "Meanwhile, their open-border policies have created chaos, allowing criminals and drugs to pour into our communities. "
        "It's clear that the Democratic Party is more focused on pandering to radical activists than solving real problems. "
        "America deserves better than the failed leadership and dangerous ideas of the Democrats."
    )
    print(f"### Article\n\n{example_article}\n")
    result = agent.process_article(example_article)
    print(result)