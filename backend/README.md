# LectureLM Backend

This project provides a backend service for generating lecture notes, transcripts, and converting markdown to PDF using AI models. It is built with Python and FastAPI, and leverages the GROQ API for language model capabilities.

## Features
- Generate lecture notes from transcripts
- Convert markdown files to PDF
- Transcribe audio files
- REST API endpoints for integration

## Requirements
- Python 3.12+
- A free GROQ API Key (see below)

## Setup Instructions

1. **Get a GROQ API Key**
   - Sign up at [GROQ](https://groq.com/) to obtain a free API key.
   - Export your API key as an environment variable:
     ```sh
     export GROQ_API_KEY="your_api_key_here"
     ```

2. **Clone the repository**
   ```sh
   git clone <repo-url>
   cd backend
   ```

3. **Create and activate a virtual environment**
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

5. **Start the FastAPI server**
   ```sh
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```
   The API will be available at [http://localhost:8000](http://localhost:8000).

## Usage
- Access API documentation at [http://localhost:8000/docs](http://localhost:8000/docs)
- Use endpoints for note generation, transcript processing, and markdown to PDF conversion

## Environment Variables
- `GROQ_API_KEY`: Your GROQ API key (required)

## License
MIT

## Contact
For questions or support, open an issue or contact the maintainer.
