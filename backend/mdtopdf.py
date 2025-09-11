import markdown
from weasyprint import HTML, CSS
import sys
from pathlib import Path
import logging
import re  # Added for preprocessing MD to fix list recognition

# Set up logging for better debugging in the project
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Polished CSS for professional lecture-style PDFs (using web fonts for simplicity)
DEFAULT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,400;0,700;1,400&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400&display=swap');

/* Page setup */
@page {
    size: A4;
    margin: 2.5cm;
    @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #777;
    }
}

/* Body text */
body {
    font-family: 'Open Sans', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

/* Headings */
h1 {
    font-size: 22pt;
    font-weight: 700;
    border-bottom: 2px solid #ddd;
    padding-bottom: 0.3em;
    margin-top: 1.5em;
    margin-bottom: 0.6em;
}
h2 {
    font-size: 18pt;
    font-weight: 700;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.2em;
    margin-top: 1.2em;
    margin-bottom: 0.6em;
}
h3 {
    font-size: 14pt;
    font-weight: 600;
    color: #444;
    margin-top: 1em;
    margin-bottom: 0.4em;
}
h4, h5, h6 {
    font-size: 12pt;
    font-weight: 600;
    color: #555;
    margin-top: 0.8em;
    margin-bottom: 0.4em;
}

/* Paragraphs */
p {
    margin: 0.6em 0;
}

/* Lists */
ul, ol {
    margin: 0.6em 0 0.6em 1.6em;
    padding-left: 1.2em;
}
ul {
    list-style-type: disc;
}
ul ul {
    list-style-type: circle;   /* nested level 2 */
}
ul ul ul {
    list-style-type: square;   /* nested level 3 */
}
ol {
    list-style-type: decimal;
}
li {
    margin: 0.3em 0;
}

/* Links */
a {
    color: #1a73e8;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}

/* Inline code */
code {
    font-family: 'Fira Code', monospace;
    background: #f4f4f4;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 10pt;
}

/* Code blocks */
pre {
    font-family: 'Fira Code', monospace;
    background: #f4f4f4;
    padding: 12px;
    border-radius: 6px;
    overflow: auto;  /* Changed from overflow-x for WeasyPrint compatibility */
    margin: 1em 0;
    font-size: 10pt;
}

/* Blockquotes */
blockquote {
    border-left: 4px solid #ccc;
    margin: 1em 0;
    padding-left: 1em;
    color: #555;
    font-style: italic;
    background: #fafafa;
}

/* Tables */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    font-size: 10.5pt;
}
th, td {
    border: 1px solid #ccc;
    padding: 6px 10px;
    text-align: left;
}
th {
    background: #f8f8f8;
    font-weight: 600;
}
"""

def markdown_to_pdf(markdown_text: str, output_pdf_path: str, css: str = DEFAULT_CSS, base_url: str = None):
    """
    Converts Markdown text to a styled PDF with professional fonts.
    - markdown_text: The MD content as a string.
    - output_pdf_path: Path to save the PDF (can be a file path or BytesIO for in-memory).
    - css: Custom CSS string (optional).
    - base_url: Base URL for resolving relative links/images (optional).
    """
    try:
        # Preprocess MD to ensure lists are recognized (add blank line before * if after text)
        markdown_text = re.sub(r'([^\n])\n\*', r'\1\n\n*', markdown_text)
        
        # Convert MD to HTML with enhanced extensions for lists
        html_text = markdown.markdown(
            markdown_text,
            extensions=['extra', 'toc', 'nl2br', 'attr_list', 'def_list', 'sane_lists']
        )
        
        # Generate PDF
        html_doc = HTML(string=html_text, base_url=base_url)
        html_doc.write_pdf(target=output_pdf_path, stylesheets=[CSS(string=css)])
        
        logging.info(f"✅ PDF generated successfully at: {output_pdf_path}")
        return True
    except Exception as e:
        logging.error(f"❌ Error generating PDF: {str(e)}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python mdtopdf.py input.md output.pdf")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    if not input_path.exists():
        logging.error(f"❌ Error: File {input_path} does not exist.")
        sys.exit(1)
    
    markdown_text = input_path.read_text(encoding='utf-8')
    success = markdown_to_pdf(markdown_text, str(output_path))
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()