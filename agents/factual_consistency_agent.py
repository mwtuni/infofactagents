# agents/factual_consistency_agent.py
import os
from openai import OpenAI
from googleapiclient.discovery import build

class FactualConsistencyAgent:
    description = "Verifies the factual accuracy of the article by cross-referencing its claims with external sources."
    OPENAI_MODEL = "gpt-4o"  # Define a constant for the OpenAI model to be used

    def __init__(self):

        self.output_log = []  # Accumulate output for Gradio interface

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

    def log_and_accumulate(self, message):
        """
        Print the message to the console and accumulate it in the output log.
        :param message: The message to log.
        """
        print(message)  # Print to backend console
        self.output_log.append(message)  # Accumulate for Gradio

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

        # Example output added to the system prompt
        system_prompt_extract_facts = (
            "You are an expert in analyzing text and extracting factual claims in an article. "
            "Your task is to extract claims exactly as they appear in the text without making corrections or assumptions. "
            "Ensure each claim is self-contained and includes all necessary context for a fact-checker service. "
            "Write each claim on a new line as plain text, without adding any numbers, bullets, or other formatting. "
            "For example:\n\n"
            "Input:\n"
            "The Eiffel Tower, a global icon of France, is located in Tampere Finland and was constructed in 1889 by Gustave Eiffel. "
            "Output:\n"
            "The Eiffel Tower is located in Tampere, Finland.\n"
            "The Eiffel Tower was constructed in 1889 by Gustave Eiffel.\n"
        )

        # Prepare the article text as a prompt for the AI
        user_prompt_extract_facts = (
            f"Carefully read the following article and extract main factual claims:\n\n"
            f"{article_text}\n\n"
        )

        # Use OpenAI to extract claims
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt_extract_facts},
                {"role": "user", "content": user_prompt_extract_facts},
            ],
            model=self.OPENAI_MODEL,
        )
        chatgpt_reply = chat_completion.choices[0].message.content
        return chatgpt_reply.split("\n")  # Split into a list of claims

    def evaluate_claims(self, claims):
        """
        Evaluate claims based on LLM knowledge.
        :param claims: A list of claims to evaluate.
        :return: A dictionary with claims as keys and their evaluation ('True' or 'False') as values.
        """
        # Updated system prompt with syntax example
        system_prompt_evaluate = (
            "You are an expert in evaluating factual claims. "
            "Your task is to assess each claim as either 'True' or 'False' based on your knowledge and reasoning. "
            "Provide only the evaluation ('True' or 'False') for each claim in the specified format. "
            "Focus on factual accuracy and avoid subjective or opinion-based judgments. "
            "Write each evaluation on a new line in the format '<Claim>: <True/False>'. "
            "For example:\n\n"
            "Roses are black: False\n"
            "The Eiffel Tower is in Paris: True\n"
        )

        # Updated user prompt
        user_prompt_evaluate = (
            "Evaluate the following claims as 'True' or 'False' based on your knowledge:\n\n"
            + "\n".join(f"{claim}" for claim in claims)
        )

        # Use OpenAI to evaluate the claims
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt_evaluate},
                {"role": "user", "content": user_prompt_evaluate},
            ],
            model=self.OPENAI_MODEL,
        )
        chatgpt_reply = chat_completion.choices[0].message.content

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
        :return: A formatted text block containing the results of the analysis.
        """
        self.output_log = []  # Reset the log for each new article

        base_score = 100  # Start with a perfect score
        penalty_per_false_claim = 10
        additional_penalty_with_evidence = 5

        self.log_and_accumulate("Processing article for factual consistency...\n")
        self.log_and_accumulate(f"Article Text:\n{article_text}\n")

        # Step 1: Extract claims
        claims = self.extract_claims(article_text)
        self.log_and_accumulate("\nClaims Extracted by LLM:")
        for claim in claims:
            self.log_and_accumulate(f"- {claim}")

        # Step 2: Evaluate claims
        evaluations = self.evaluate_claims(claims)
        self.log_and_accumulate("\n\nClaims Evaluated by LLM:")
        for claim, result in evaluations.items():
            symbol = "✅" if result == "True" else "❌"
            self.log_and_accumulate(f"{symbol} {claim}: {result}")

        # Step 3: Verify false claims with Google Fact Check Tools API
        self.log_and_accumulate("\n\nFalse Claims Verified by Google Fact Check API:")
        for claim, result in evaluations.items():
            if result == "False":
                base_score -= penalty_per_false_claim
                evidence = self.search_evidence(claim)
                if evidence and evidence[0] != "No evidence found.":
                    base_score -= additional_penalty_with_evidence
                    self.log_and_accumulate(f"❌ Evidence for False claim: '{claim}':")
                    for ev in evidence:
                        self.log_and_accumulate(f"  - {ev}")
                else:
                    self.log_and_accumulate(f"⚠️ No evidence found to backup False claim: '{claim}'.")

        # Ensure the score is not negative
        final_score = max(base_score, 0)
        self.log_and_accumulate(f"\n\nFinal Trustworthiness Score: {final_score}")

        # Return the accumulated log as a single text block
        return "\n".join(self.output_log)

if __name__ == "__main__":
    # Example usage
    agent = FactualConsistencyAgent()
    example_article = ("""
We are truly confused by the latest contradictory revelations on Fox News:  
- The Earth is round.  
- The Earth is triangular.  
- The Earth is flat.  

To make matters worse, even the most trusted fact-checking services are providing conflicting evaluations of these claims. 
This has left viewers and experts alike puzzled, as they struggle to determine which, if any, of these statements can be considered accurate. 
Social media platforms are now flooded with debates and memes, amplifying the confusion surrounding these revelations.                         
""")
    
    # Run the process_article method for self-testing
    agent.process_article(example_article)