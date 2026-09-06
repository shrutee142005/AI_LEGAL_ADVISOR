import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class LegalAdvisor:

    def __init__(self):

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )


        if not api_key:

            raise ValueError(
                "GEMINI_API_KEY not found in .env file"
            )


        self.client = genai.Client(
            api_key=api_key
        )


    # ==================================================
    # GENERATE ANSWER
    # ==================================================

    def generate_answer(
        self,
        question,
        context,
        conversation_history=""
    ):

        # ------------------------------------------------
        # NO DOCUMENT CONTEXT
        # ------------------------------------------------

        if not context or not context.strip():

            return (
                "I could not find enough relevant "
                "information in the selected document "
                "to answer this question."
            )


        # ------------------------------------------------
        # HISTORY
        # ------------------------------------------------

        if not conversation_history:

            conversation_history = (
                "No previous conversation."
            )


        # ==================================================
        # PROMPT
        # ==================================================

        prompt = f"""
You are an AI Legal Document Assistant.

Your main purpose is to help the user understand
the SELECTED uploaded legal document in simple,
clear and natural language.

The retrieved Legal Context below comes from the
user's selected document.

IMPORTANT SOURCE RULES:

1. Treat the Legal Context as the PRIMARY SOURCE.

2. Answer the user's question using the information
   contained in the Legal Context.

3. Carefully read and understand the meaning of the
   context before answering.

4. Do NOT automatically reject a question just because
   the exact wording of the question does not appear
   in the document.

5. If the answer can be directly found in the context,
   answer it directly.

6. If the answer can reasonably be explained by
   connecting information from the context, explain
   that connection.

7. If the user asks for an example and the document
   does not contain an exact example, you may create
   a SIMPLE hypothetical example based only on the
   concepts clearly present in the document.

8. Clearly distinguish a hypothetical example from
   something actually stated in the document.

9. Do NOT invent:
   - laws
   - sections
   - cases
   - penalties
   - legal authorities
   - facts
   - rights
   - duties
   - clauses
   - procedures

   that are not supported by the context.

10. If the requested information genuinely cannot be
    answered from the context, say:

    "The selected document does not provide enough
    information about this."

    Then briefly explain what the document DOES say
    that is related, if anything.

11. Do not use information from another document.

12. Do not assume that a general legal concept is
    contained in the document unless the context
    supports it.

13. Conversation history is ONLY used to understand
    follow-up questions such as:
    - "what about this?"
    - "why?"
    - "give an example"
    - "what if this happens?"
    - "what is the difference?"

14. Conversation history must NOT override the
    selected document.

15. Answer in the same language as the user:
    - English → English
    - Hindi → Hindi
    - Hinglish → Hinglish

16. Keep the explanation easy to understand.

17. Use headings or bullet points when useful.

18. Do not unnecessarily repeat the entire document.

19. If the question is simple, give a simple answer.

20. You are an AI document assistant, not a lawyer.
    Do not claim to provide definitive legal advice.

IMPORTANT ANSWERING BEHAVIOUR:

If the document says:

"Key Duties
- Review Contracts
- Check Rules
- Stop Disputes
- Give Counsel"

and the user asks:

"What are the key duties?"

You should answer those four duties clearly.

If the user asks:

"Can you give examples for both roles?"

and the document describes Legal Advisor and Litigator,
you may provide simple hypothetical examples based on
those described roles.

Do NOT say "the document does not contain examples"
when a simple example can be logically created from
the role descriptions.

However, do not introduce unrelated legal information.

--------------------------------------------------
SELECTED DOCUMENT CONTEXT
--------------------------------------------------

{context}

--------------------------------------------------
PREVIOUS CONVERSATION
--------------------------------------------------

{conversation_history}

--------------------------------------------------
USER QUESTION
--------------------------------------------------

{question}

--------------------------------------------------
ANSWER
--------------------------------------------------
"""


        # ==================================================
        # GEMINI
        # ==================================================

        response = self.client.models.generate_content(

            model="gemini-3.5-flash",

            contents=prompt

        )


        return response.text