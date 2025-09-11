import os
import subprocess
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

WORDS_PER_CHUNK = 200
MAX_SIZE_MB = 19.5

def youtube_transcript_json(youtube_url: str, words_per_chunk=WORDS_PER_CHUNK, max_size_mb=MAX_SIZE_MB):
    """
    Downloads a YouTube video's audio, compresses if necessary, transcribes it,
    and returns a JSON-ready list of chunks. Optimized for local execution.
    """
    temp_file = "temp_audio.webm"
    audio_to_use = temp_file
    compressed_file = "temp_audio_compressed.webm"

    try:
        # 1. Get video info to find the best audio format
        info_json_str = subprocess.run(
            ["yt-dlp", "-j", youtube_url],
            capture_output=True, text=True, check=True
        ).stdout
        video_info = json.loads(info_json_str)

        # 2. Filter for audio-only formats
        audio_only = [f for f in video_info["formats"] if f.get("acodec") != "none" and f.get("vcodec") == "none"]
        if not audio_only:
            raise ValueError("No audio-only tracks found!")

        # 3. Prioritize English, then fallback to smallest overall
        english_audios = [f for f in audio_only if f.get("language") == "en"]
        best_audio = min(english_audios or audio_only, key=lambda f: f.get("filesize") or float('inf'))

        # 4. Download the selected audio track
        subprocess.run([
            "yt-dlp", "-f", best_audio["format_id"], "-o", temp_file, youtube_url
        ], check=True)

        # 5. Compress if the audio file is too large
        if os.path.getsize(temp_file) / (1024 * 1024) > max_size_mb:
            subprocess.run([
                "ffmpeg", "-i", temp_file, "-c:a", "libopus", "-b:a", "32k",
                "-ac", "1", "-y", compressed_file
            ], check=True)
            audio_to_use = compressed_file
            if os.path.getsize(audio_to_use) / (1024 * 1024) > max_size_mb:
                raise ValueError("Audio is too large even after compression.")

        # 6. Transcribe the audio file
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        with open(audio_to_use, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=(audio_to_use, f.read()),
                model="whisper-large-v3-turbo",
                response_format="verbose_json"
            )

        # 7. Process transcription into chunks
        chunks = []
        current_words = []
        start_time = None
        for seg in transcription.segments:
            words = seg["text"].strip().split()
            if start_time is None and words:
                start_time = seg["start"]
            for word in words:
                current_words.append(word)
                if len(current_words) >= words_per_chunk:
                    chunks.append({"start_time": start_time, "text": " ".join(current_words)})
                    current_words = []
                    start_time = seg["end"]
        if current_words:
            chunks.append({"start_time": start_time, "text": " ".join(current_words)})
        
        return chunks

    finally:
        # 8. Clean up temporary files
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if audio_to_use != temp_file and os.path.exists(audio_to_use):
            os.remove(audio_to_use)



