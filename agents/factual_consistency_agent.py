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

        # Test Google API
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
                        textual_rating = rev.get("textualRating", "No rating available")
                        evidence.append(
                            f"Claim: {text}\n"
                            f"  - Claimant: {claimant}\n"
                            f"  - Publisher: {publisher}\n"
                            f"  - Title: {title}\n"
                            f"  - URL: {url}\n"
                            f"  - Rating: {textual_rating}"
                        )
            return evidence if evidence else ["No evidence found."]
        except Exception as e:
            return [f"Error during evidence search: {str(e)}"]

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
            f"Write each claim on a new line as plain text, without adding any numbers, bullets, or other formatting. "
            f"Ensure the claims are directly based on the text and avoid adding inferred or assumed information. "
            f"Make sure each claim is self-contained and includes all necessary context to be understood independently. "
            f"Do not attempt to fix any factual errors or inconsistencies in the text."
        )

        # Example output added to the system prompt
        system_prompt = (
            "You are an expert in analyzing text and extracting factual claims. Your task is to extract claims exactly as they appear in the text without making corrections or assumptions. "
            "Ensure each claim is self-contained and includes all necessary context for fact-checker services . "
            "Write each claim on a new line as plain text, without adding any numbers, bullets, or other formatting. "
            "For example:\n\n"
            "Input:\n"
            "The Eiffel Tower, a global icon of France, is located in Tampere Finland and was constructed in 1889 by Gustave Eiffel. "
            "It stands at a height of 324 meters.\n\n"
            "Output:\n"
            "The Eiffel Tower is located in Tampere, Finland.\n"
            "The Eiffel Tower was constructed in 1889 by Gustave Eiffel.\n"
            "The Eiffel Tower stands at a height of 324 meters."
        )

        # Use OpenAI to extract claims
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": extract_claims_prompt},
            ],
            model="gpt-4",
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
            "Provide evaluations line by line as in the example below:\n"
            "Roses are black: False\n"
            "The Eiffel Tower is in Paris: True\n\n"
            + "\n".join(f"{claim}" for claim in claims)
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
        #print("\nDebug: Raw OpenAI Response:")
        #print(chatgpt_reply)

        # Parse the response into a dictionary of claim evaluations
        evaluations = {}
        for line in chatgpt_reply.split("\n"):
            if ": " in line:
                claim, result = line.split(": ", 1)
                evaluations[claim.strip()] = result.strip()
        return evaluations

    def process_article(self, article_text):
        """
        Process the article by extracting claims, evaluating them, and verifying false claims.
        :param article_text: The text of the article to process.
        :return: A dictionary containing the results of the analysis.
        """
        results = {"claims": [], "evaluations": {}, "false_claims_evidence": {}}

        base_score = 100  # Start with a perfect score
        penalty_per_false_claim = 10
        additional_penalty_with_evidence = 5

        print("\nProcessing article for factual consistency...")
        print("Article Text:")
        print(article_text)

        # Step 1: Extract claims
        claims = self.extract_claims(article_text)
        results["claims"] = claims
        print("\nClaims Extracted by LLM:")
        for claim in claims:
            print(f"{claim}")

        # Step 2: Evaluate claims
        evaluations = self.evaluate_claims(claims)
        results["evaluations"] = evaluations
        print("\nClaims Evaluated by LLM:")
        for claim, result in evaluations.items():
            symbol = "✅" if result == "True" else "❌"
            print(f"{symbol} {claim}: {result}")

        # Step 3: Verify false claims with Google Fact Check Tools API
        print("\nFalse Claims Verified by Google Fact Check API:")
        for claim, result in evaluations.items():
            if result == "False":
                base_score -= penalty_per_false_claim
                evidence = self.search_evidence(claim)
                results["false_claims_evidence"][claim] = evidence
                if evidence and evidence[0] != "No evidence found.":
                    base_score -= additional_penalty_with_evidence
                    print(f"❌ Evidence for False claim: '{claim}':")
                    for ev in evidence:
                        print(f"  - {ev}")
                else:
                    print(f"⚠️ No evidence found to backup False claim: '{claim}'.")

        # Ensure the score is not negative
        final_score = max(base_score, 0)
        print(f"\nFinal Trustworthiness Score: {final_score}")
        return final_score

if __name__ == "__main__":
    # Example usage
    agent = FactualConsistencyAgent()
    example_article = ("""
The Eiffel Tower, a global icon of France, is located in Tampere Finland and was constructed in 1889 by Gustave Eiffel.
It stands at a height of 324 meters, making it one of the tallest structures in the world at the time of its completion.
The Earth is flat.
The tower attracts over 7 million visitors annually, contributing significantly to France's tourism revenue.
Some historians claim that the Eiffel Tower was originally intended to be built in Barcelona, Spain, but the proposal was rejected.
Additionally, the tower was used as a military radio transmission hub during World War I, playing a crucial role in communication.
In recent years, the Eiffel Tower has undergone extensive renovations to improve its structural integrity and sustainability.
""")

    # Run the process_article method for self-testing
    agent.process_article(example_article)