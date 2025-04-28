# agents/factual_consistency_agent.py
import os
from openai import OpenAI
from googleapiclient.discovery import build

class FactualConsistencyAgent:
    description = "Verifies the factual accuracy of the article by cross-referencing its claims with external sources."

    def __init__(self):

        # Ensure the OPENAI API key is set
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=api_key)

        # Initialize Google Fact Check Tools API client
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        if google_api_key is None:
            raise ValueError("Google API key not found. Please set the GOOGLE_API_KEY environment variable.")
        self.google_client = build("factchecktools", "v1alpha1", developerKey=google_api_key)
        self.test_google_api()

    def test_google_api(self):
        # Test Google API with a known false claim
        query = "The Earth is flat"
        try:
            response = self.google_client.claims().search(query=query).execute()

            # Check for textualRating indicating "False"
            if "claims" in response:
                for item in response["claims"]:
                    reviews = item.get("claimReview", [])
                    for review in reviews:
                        textual_rating = review.get("textualRating", "").lower()
                        if "false" in textual_rating:
                            print(f"✅ Google API check works: Found 'False' textualRating for query '{query}'.")
                            return
            print(f"⚠️ Google API check did not find any 'False' textualRating for query '{query}'.")
        except Exception as e:
            print(f"Error: {e}")

    def search_evidence(self, claim):
        """
        Search for evidence supporting or refuting a claim using Google Fact Check Tools API.
        :param claim: The claim to search for.
        :return: A list of evidence summaries.
        """
        try:
            # Call the Google Fact Check Tools API
            response = self.google_client.claims().search(query=claim).execute()

            # Extract evidence from the response
            evidence = []
            if "claims" in response:
                for item in response["claims"]:
                    text = item.get("text", "No claim text available")
                    claimant = item.get("claimant", "Unknown claimant")
                    review = item.get("claimReview", [])
                    for rev in review:
                        publisher = rev.get("publisher", {}).get("name", "Unknown publisher")
                        title = rev.get("title", "No title available")
                        url = rev.get("url", "No URL available")
                        evidence.append(f"{text} - {claimant} ({publisher}): {title} [URL: {url}]")
            return evidence
        except Exception as e:
            return [f"Error during evidence search: {str(e)}"]

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
            f"List each claim as a separate line of text without formatting. Ensure the claims are directly based on the text and avoid adding inferred or assumed information. "
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

    def evaluate_claims(self, claims):
        """
        Evaluate claims based on LLM knowledge.
        :param claims: A list of claims to evaluate.
        :return: A dictionary with claims as keys and their evaluation ('True' or 'False') as values.
        """
        evaluation_prompt = (
            "Evaluate the following claims as 'True' or 'False' based on your knowledge. "
            "Provide the evaluation in the format: 'Claim: True' or 'Claim: False'. "
            "For example:\n"
            "Roses are black: False\n"
            "The Eiffel Tower is in Paris: True\n\n"
            + "\n".join(f"- {claim}" for claim in claims)
        )

        # Use OpenAI to evaluate the claims
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert in evaluating factual claims. Provide only 'True' or 'False' evaluations for each claim in the specified format."},
                {"role": "user", "content": evaluation_prompt},
            ],
            model="gpt-3.5-turbo",
        )
        chatgpt_reply = chat_completion.choices[0].message.content

        # Parse the response into a dictionary of claim evaluations
        evaluations = {}
        for line in chatgpt_reply.split("\n"):
            if ": " in line:
                claim, result = line.split(": ", 1)
                evaluations[claim.strip()] = result.strip()
        return evaluations

if __name__ == "__main__":
    # Example usage
    agent = FactualConsistencyAgent()
    example_article = (
        "The Eiffel Tower, a global icon of France, is located in Tampere Finland and was constructed in 1889 by Gustave Eiffel. "
        "It stands at a height of 324 meters, making it one of the tallest structures in the world at the time of its completion. "
        "The tower attracts over 7 million visitors annually, contributing significantly to France's tourism revenue. "
        "Some historians claim that the Eiffel Tower was originally intended to be built in Barcelona, Spain, but the proposal was rejected. "
        "Additionally, the tower was used as a military radio transmission hub during World War I, playing a crucial role in communication. "
        "In recent years, the Eiffel Tower has undergone extensive renovations to improve its structural integrity and sustainability. Earth is triangular."
    )

    # Step 1: Extract claims
    claims = agent.extract_claims(example_article)
    print("\n1 Claims extracted by LLM:")
    for claim in claims:
        print(f"{claim}")

    # Step 2: Evaluate claims
    evaluations = agent.evaluate_claims(claims)
    print("\n2 Claims Evaluated by LLM:")
    for claim, result in evaluations.items():
        symbol = "✅" if result == "True" else "❌"
        print(f"{symbol} {claim}: {result}")

    # Step 3: Verify false claims with Google Fact Check Tools API
    print("\n3 False Claims Verified by Google Fact Check API:")
    for claim, result in evaluations.items():
        if result == "False":
            evidence = agent.search_evidence(claim)
            print(f"\nEvidence for '{claim}':")
            if evidence:
                for ev in evidence:
                    print(f"- {ev}")
            else:
                print("No evidence found.")