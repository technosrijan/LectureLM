from groq import Groq
import os
from dotenv import load_dotenv
from transcript import youtube_transcript_json
import json
import re
from urllib.parse import urlparse, parse_qs

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)
def generate_notes(url):
    normalized_url = normalize_url(url)
    video_id = parse_qs(urlparse(normalized_url).query)["v"][0]
    transcript = youtube_transcript_json(normalized_url)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
        {
        "role": "system",
        "content": """
         You are an expert academic note-taker. Your task is to convert a lecture transcript into complete, study-ready notes in Markdown. The transcript will be provided as a JSON array, where each element has:

- "start_time": the start time in seconds for that chunk
- "text": the transcript text for that chunk

Follow these rules:

1. Include **every explanation, example, definition, concept, and workflow** from the transcript. Do NOT generate summaries or high-level overviews.
2. Structure the notes using **headings, subheadings, bullet points, numbered lists**, and **bold/italic formatting** where appropriate.
3. For each chunk, create a **clickable hyperlink to the exact video timestamp** using this format:
   [description](https://www.youtube.com/watch?v=VIDEO_ID&t=START_TIMEs)
   - Replace VIDEO_ID with the actual video ID.
   - Replace START_TIME with the "start_time" in seconds from the JSON chunk.
4. Organize content logically so someone can understand the material without reading the original transcript.
5. Avoid lecture-style filler like “as discussed earlier,” “we will see,” or “important point here.”
6. If the lecture covers multiple topics, create separate sections for each topic, including all relevant content under that topic.
7. Make the notes **comprehensive but readable**, not just a bullet list of keywords.
8. Output **pure Markdown**; do not include raw JSON or extra commentary.

         """
      },

       {
        "role": "user",
        "content": "Video id: " + video_id + "\nLecture Transcript:\n" + json.dumps(transcript)
      }
    ],
    )
    return extract_markdown(response.choices[0].message.content)

def normalize_url(url: str) -> str:
    """
    Normalizes any YouTube URL to the canonical form:
    https://www.youtube.com/watch?v=VIDEO_ID
    """
    # Patterns for extracting video ID
    patterns = [
        r'(?:youtube\.com/(?:watch\?.*v=|embed/|v/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{11})',
        r'v=([A-Za-z0-9_-]{11})'
    ]
    video_id = None

    # Try regex patterns
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break

    # Fallback: parse query string
    if not video_id:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        if 'v' in qs and len(qs['v'][0]) == 11:
            video_id = qs['v'][0]

    if not video_id:
        raise ValueError("Could not extract YouTube video ID from URL.")

    return f"https://www.youtube.com/watch?v={video_id}"

import re

def extract_markdown(llm_output: str) -> str:
    """
    Extracts the Markdown portion from LLM output.
    Removes any leading/trailing non-Markdown text.
    """
    # Optional: strip JSON-looking wrappers
    if llm_output.startswith("{") or llm_output.startswith("["):
        # Try to extract the "markdown" field if JSON
        import json
        try:
            data = json.loads(llm_output)
            if "markdown" in data:
                return data["markdown"]
        except json.JSONDecodeError:
            pass

    # Remove any text before first Markdown heading
    first_heading = re.search(r"(?m)^#{1,6} ", llm_output)
    if first_heading:
        return llm_output[first_heading.start():].strip()
    
    # Otherwise, return as is
    return llm_output.strip()
