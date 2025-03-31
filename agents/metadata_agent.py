# agents/metadata_agent.py
import os
from openai import OpenAI

class MetadataAgent:
    description = "Evaluates the credibility of the article's source by analyzing metadata."

    def __init__(self):
        # Ensure the API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=api_key)

    # Define function to analyze metadata
    def analyze_metadata(self, metadata):
        """
        Analyze the metadata of an article to evaluate its credibility.
        :param metadata: A dictionary containing metadata (e.g., domain, publication date, author).
        :return: A string summarizing the credibility analysis.
        """
        # Prepare the metadata as a prompt for the AI
        metadata_prompt = (
            f"Evaluate the credibility of the following article metadata:\n"
            f"Domain: {metadata.get('domain', 'Unknown')}\n"
            f"Publication Date: {metadata.get('publication_date', 'Unknown')}\n"
            f"Author: {metadata.get('author', 'Unknown')}\n"
            f"Provide a detailed analysis of the credibility of this source."
        )

        # Use OpenAI to analyze the metadata
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert in evaluating article credibility."},
                {"role": "user", "content": metadata_prompt},
            ],
            model="gpt-3.5-turbo",
        )
        chatgpt_reply = chat_completion.choices[0].message.content
        return chatgpt_reply

if __name__ == "__main__":
    # Example usage
    agent = MetadataAgent()
    example_metadata = {
        "domain": "example.com",
        "publication_date": "2025-03-27",
        "author": "John Doe"
    }
    print(agent.analyze_metadata(example_metadata))