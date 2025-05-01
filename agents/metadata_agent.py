import os
import re
from openai import OpenAI

class MetadataAgent:
    description = "Analyzes the credibility of URLs and persons mentioned within the article."

    def __init__(self):
        # Ensure the API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=api_key)

    def extract_urls_and_persons(self, article_text):
        """
        Extract all URLs and names of persons from the article text.
        :param article_text: The text of the article.
        :return: A tuple containing a list of URLs and a list of persons.
        """
        # Extract URLs using a regex pattern
        url_pattern = r"https?://[^\s]+"
        urls = re.findall(url_pattern, article_text)

        # Extract potential names of persons using a simple heuristic (capitalized words)
        person_pattern = r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"
        persons = re.findall(person_pattern, article_text)

        return urls, persons

    def process_article(self, article_text):
        """
        Analyze the credibility of URLs and persons mentioned within the article.
        :param article_text: The text of the article to analyze.
        :return: A dictionary summarizing the credibility analysis.
        """
        # Extract URLs and persons from the article
        urls, persons = self.extract_urls_and_persons(article_text)
        print("Extracted URLs:", urls)  # Debugging
        print("Extracted Persons:", persons)  # Debugging

        # Prepare the system prompt with an example output format
        system_prompt = (
            "You are an expert in evaluating the credibility of online sources and individuals. "
            "Your task is to analyze the credibility of the provided URLs and persons mentioned in the article. "
            "For each entity, provide a brief analysis of its reliability, potential bias, and trustworthiness. "
            "Follow the format below:\n\n"
            "URLs:\n"
            "https://example.com/news: Reliability: High. Bias: Neutral. Trustworthiness: Reliable source for news.\n"
            "https://another-example.org/research: Reliability: Medium. Bias: Slightly academic. Trustworthiness: Credible for research purposes.\n\n"
            "Persons:\n"
            "John Doe: Reliability: High. Bias: Neutral. Trustworthiness: Well-regarded expert in the field.\n"
            "Jane Smith: Reliability: Medium. Bias: Slightly political. Trustworthiness: Known for defending controversial policies.\n"
        )

        # Prepare the user prompt with the extracted URLs and persons
        metadata_prompt = (
            "Evaluate the credibility of the following entities mentioned in the article:\n\n"
            "URLs:\n" + ("\n".join(urls) if urls else "None") + "\n\n"
            "Persons:\n" + ("\n".join(persons) if persons else "None") + "\n\n"
            "Provide your evaluation in the specified format."
        )

        # Use OpenAI to analyze the metadata
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": metadata_prompt},
            ],
            model="gpt-3.5-turbo",
        )
        chatgpt_reply = chat_completion.choices[0].message.content
        print("Raw OpenAI Response:", chatgpt_reply)  # Debugging

        # Parse the response into a structured format
        response_lines = chatgpt_reply.split("\n")
        print("Response Lines:", response_lines)  # Debugging
        analysis = {"URLs": {}, "Persons": {}}
        current_section = None

        for line in response_lines:
            if line.startswith("URLs:"):
                current_section = "URLs"
            elif line.startswith("Persons:"):
                current_section = "Persons"
            elif ": " in line and current_section:
                entity, evaluation = line.split(": ", 1)
                analysis[current_section][entity.strip()] = evaluation.strip()

        return analysis

if __name__ == "__main__":
    # Example usage
    agent = MetadataAgent()
    example_article = (
        "According to a recent report by The New York Times (https://www.nytimes.com), "
        "the global economy is facing unprecedented challenges due to climate change. "
        "The article highlights statements from John Kerry, the U.S. Special Presidential Envoy for Climate, "
        "who emphasized the need for immediate action. Additionally, the report references data from the World Bank "
        "(https://www.worldbank.org) and the International Monetary Fund (https://www.imf.org), "
        "both of which have warned about the economic risks of inaction. "
        "Critics, including Michael Johnson, a prominent economist, argue that the proposed solutions may not be sufficient "
        "to address the scale of the problem. Meanwhile, advocacy groups like Greenpeace (https://www.greenpeace.org) "
        "continue to push for more aggressive policies to combat climate change."
    )
    result = agent.analyze_metadata(example_article)
    print("Metadata Analysis Summary:")
    for section, entities in result.items():
        print(f"{section}:")
        for entity, evaluation in entities.items():
            print(f"  {entity}: {evaluation}")