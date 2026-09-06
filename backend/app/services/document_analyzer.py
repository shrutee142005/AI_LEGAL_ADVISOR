import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class DocumentAnalyzer:

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
    # ANALYZE DOCUMENT
    # ==================================================

    def analyze(self, text):

        if not text or not text.strip():

            return {
                "summary": "",
                "important_points": [],
                "key_topics": []
            }


        # ------------------------------------------
        # LIMIT EXTREMELY LARGE DOCUMENTS
        # ------------------------------------------

        # For now, keep enough text for analysis
        # while avoiding unnecessarily huge prompts.

        max_characters = 50000

        document_text = text[:max_characters]


        # ==================================================
        # PROMPT
        # ==================================================

        prompt = f"""
You are an AI Legal Document Analyzer.

Analyze the uploaded legal document carefully.

The user wants an easy-to-understand analysis of the
document, not formal legal advice.

IMPORTANT RULES:

1. Use ONLY the information present in the document.
2. Do NOT add outside legal knowledge.
3. Do NOT invent facts.
4. Keep the explanation simple and systematic.
5. Important points must actually come from the document.
6. Explain difficult legal concepts in easy words.
7. If the document contains legal terms, preserve the
   legal term and explain it simply.
8. The analysis should be useful before the user starts
   asking questions in chat.
9. The user may later ask hypothetical questions based
   on this document, so identify the important principles
   clearly.
10. Do NOT give a definitive legal conclusion.
11. Do NOT say information is missing unless it genuinely
    cannot be identified from the document.

Return the result in EXACTLY this structure:

SUMMARY:
Write a short, clear summary of what the document is about.

IMPORTANT_POINTS:
- Point 1
- Point 2
- Point 3
- Point 4
- Point 5

KEY_TOPICS:
- Topic 1
- Topic 2
- Topic 3

DOCUMENT:
----------------
{document_text}
----------------
"""


        # ==================================================
        # GEMINI
        # ==================================================

        response = self.client.models.generate_content(

            model="gemini-3.5-flash",

            contents=prompt

        )


        result = response.text.strip()


        # ==================================================
        # PARSE RESPONSE
        # ==================================================

        summary = ""

        important_points = []

        key_topics = []


        current_section = None


        for line in result.splitlines():

            line = line.strip()


            if not line:
                continue


            upper_line = line.upper()


            # ------------------------------------------
            # SUMMARY
            # ------------------------------------------

            if upper_line.startswith(
                "SUMMARY:"
            ):

                current_section = "summary"

                value = line[
                    len("SUMMARY:"):
                ].strip()

                if value:
                    summary = value

                continue


            # ------------------------------------------
            # IMPORTANT POINTS
            # ------------------------------------------

            if upper_line.startswith(
                "IMPORTANT_POINTS:"
            ):

                current_section = "important_points"

                continue


            # ------------------------------------------
            # KEY TOPICS
            # ------------------------------------------

            if upper_line.startswith(
                "KEY_TOPICS:"
            ):

                current_section = "key_topics"

                continue


            # ------------------------------------------
            # BULLET
            # ------------------------------------------

            if line.startswith(
                "-"
            ):

                value = line[1:].strip()

            elif line.startswith(
                "*"
            ):

                value = line[1:].strip()

            else:

                value = line


            # ------------------------------------------
            # SAVE SECTION DATA
            # ------------------------------------------

            if current_section == "summary":

                if summary:

                    summary += " " + value

                else:

                    summary = value


            elif current_section == "important_points":

                important_points.append(
                    value
                )


            elif current_section == "key_topics":

                key_topics.append(
                    value
                )


        # ==================================================
        # FALLBACK
        # ==================================================

        if not summary:

            summary = (
                "The document was analyzed successfully."
            )


        # Remove accidental empty values

        important_points = [
            point
            for point in important_points
            if point.strip()
        ]


        key_topics = [
            topic
            for topic in key_topics
            if topic.strip()
        ]


        # ==================================================
        # RETURN STRUCTURED RESULT
        # ==================================================

        return {

            "summary":
                summary,

            "important_points":
                important_points,

            "key_topics":
                key_topics

        }