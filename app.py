import streamlit as st
import urllib.request
import urllib.error
import re
import json
import io
import html
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

# ==========================================
# 1. ROBUST CLOUD PIPELINE SUBTITLE SCRAPER
# ==========================================

def extract_video_id(url):
    """Extract the YouTube video ID from various URL formats."""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def fetch_youtube_transcript(video_url):
    """Fetches transcript using Layer A (Direct) and Layer B (Fallback)."""
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")

    # Layer A: Direct request to YouTube page source
    try:
        req = urllib.request.Request(
            f"https://www.youtube.com/watch?v={video_id}",
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        html_content = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        
        # Search for caption tracks in JSON string inside the HTML
        match = re.search(r'"captionTracks":\s*(\[.*?\])', html_content)
        if match:
            tracks = json.loads(match.group(1))
            base_url = tracks[0]['baseUrl']
            
            # Fetch the raw XML data
            xml_req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
            xml_data = urllib.request.urlopen(xml_req, timeout=10).read().decode('utf-8')
            
            # Strip XML tags via regex to get the combined text string
            text_string = re.sub(r'<[^>]+>', ' ', xml_data)
            text_string = html.unescape(text_string)
            return re.sub(r'\s+', ' ', text_string).strip()
    except Exception as e:
        print(f"Layer A Failed: {e}")

    # Layer B: Fallback Router to the open mirror endpoint
    try:
        fallback_req = urllib.request.Request(
            f"https://v9.me/{video_id}", 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        fallback_resp = urllib.request.urlopen(fallback_req, timeout=10).read().decode('utf-8')
        json_data = json.loads(fallback_resp)
        
        # Extract text assuming JSON array of dictionaries or lines
        if isinstance(json_data, list):
            lines = [item.get('text', '') for item in json_data if isinstance(item, dict)]
            return " ".join(lines).strip()
        elif isinstance(json_data, dict) and 'text' in json_data:
            return json_data['text']
        else:
            return str(json_data)
    except Exception as e:
        raise RuntimeError(f"Both Layer A and Layer B failed to extract transcripts. Error: {e}")

# ==========================================
# 2. TWO-TIER TRANSCRIPTION CLEANING ENGINE
# ==========================================

def clean_transcript_text(raw_text):
    """Scrubs out promotional fluff words using regex."""
    # List of terms to filter out case-insensitively
    fluff_pattern = r'(?i)\b(subscribe|like|share|channel|welcome back|bell icon|like aur share)\b'
    
    # Apply regex filter and clean up any double spaces left behind
    cleaned = re.sub(fluff_pattern, '', raw_text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

# ==========================================
# 3. AUTOMATED PDF GENERATION (ReportLab)
# ==========================================

def generate_pdf_buffer(text):
    """Generates an in-memory PDF buffer strictly adhering to formatting rules."""
    buffer = io.BytesIO()
    
    # Apply margins = 40, pagesize = letter
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=40, 
        leftMargin=40, 
        topMargin=40, 
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom ParagraphStyle: 11pt size, 16pt leading, justified alignment
    custom_style = ParagraphStyle(
        name='MobileOptimized',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY
    )
    
    flowables = []
    
    # Format into neat paragraphs for crisp mobile legibility (approx 80 words per paragraph)
    words = text.split()
    paragraph_chunks = [" ".join(words[i:i + 80]) for i in range(0, len(words), 80)]
    
    for chunk in paragraph_chunks:
        flowables.append(Paragraph(chunk, custom_style))
        flowables.append(Spacer(1, 14)) # Space between paragraphs
        
    doc.build(flowables)
    buffer.seek(0)
    return buffer

# ==========================================
# 4. STREAMLIT MOBILE UI AND DOWNLOADS
# ==========================================

# Set UI layout to centered
st.set_page_config(page_title="Video-to-PDF", layout="centered")

# Clean header title
st.markdown("<h2 style='text-align: center;'>🤖 Ultra Max Video-to-PDF Converter</h2>", unsafe_allow_html=True)
st.markdown("---")

# Clean st.text_input() field box
url_input = st.text_input("Paste YouTube Video URL Link here:", placeholder="https://www.youtube.com/watch?v=...")

st.write("") # small spacing

# Prominent action success button
if st.button("⚡ GENERATE BOTH PDFs", use_container_width=True):
    if not url_input.strip():
        st.error("Please enter a valid YouTube URL.")
    else:
        try:
            with st.spinner("Extracting transcript via Cloud Pipeline..."):
                # Fetch Raw Text (Layer A/B)
                raw_text = fetch_youtube_transcript(url_input)
                
                if not raw_text:
                    st.error("Could not find captions/subtitles for this video.")
                else:
                    # Filter for Commercial Ready Version
                    clean_text = clean_transcript_text(raw_text)
                    
                    # Generate the PDF buffers
                    pdf1_buffer = generate_pdf_buffer(raw_text)
                    pdf2_buffer = generate_pdf_buffer(clean_text)
                    
                    # Success alert message
                    st.success("✅ Successfully generated and optimized documents!")
                    
                    # Show TWO side-by-side action buttons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="📥 Download PDF 1 (Full)",
                            data=pdf1_buffer,
                            file_name="Raw_Transcript.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                    with col2:
                        st.download_button(
                            label="📥 Download PDF 2 (Clean)",
                            data=pdf2_buffer,
                            file_name="Clean_Transcript.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
            
