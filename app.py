import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
import io
import re

# Set page configuration optimized for mobile
st.set_page_config(
    page_title="Ultra Max Video-to-PDF",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def extract_video_id(url):
    """Extracts the 11-character YouTube video ID from various URL formats."""
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^"&?/\s]{11})'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def clean_commercial_text(text):
    """Scrubs promotional fluff while preserving educational knowledge."""
    # FIXED: Added proper quotes and string formatting to prevent code crash
    fluff_patterns = [
        r'(?i)\b(please\s+)?(subscribe|like|share|comment)\b([\s\w]*\b(channel|video|bell\s+icon|button)\b)?',
        r'(?i)\bwelcome\s+back\s+to\s+my\s+channel\b',
        r'(?i)\bhit\s+the\s+bell\s+icon\b',
        r'(?i)\bthumbs\s+up\b',
        r'(?i)\blink\s+in\s+the\s+description\b'
    ]
    
    cleaned = text
    for pattern in fluff_patterns:
        cleaned = re.sub(pattern, '', cleaned)
    
    # Clean up redundant spaces and empty lines left over by removal
    cleaned = re.sub(r' +', ' ', cleaned)
    cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned)
    return cleaned.strip()

def build_pdf(text_content, title_text):
    """Generates a styled PDF in memory using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom typography style configurations
    title_style = ParagraphStyle(
        'PDFTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        spaceAfter=20,
        alignment=TA_LEFT
    )
    
    body_style = ParagraphStyle(
        'PDFBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    story = []
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 10))
    
    # Process text chunks into paragraphs to maintain legibility
    paragraphs = text_content.split('\n\n')
    for para in paragraphs:
        if para.strip():
            # Replace basic newlines inside a paragraph with spaces
            clean_para = para.replace('\n', ' ').strip()
            story.append(Paragraph(clean_para, body_style))
            
    doc.build(story)
    buffer.seek(0)
    return buffer

# Application UI Rendering
st.title("🤖 Ultra Max Video-to-PDF Converter")
st.markdown("Convert any educational or instructional YouTube video directly into readable, downloadable PDF documents instantly.")

video_url = st.text_input("🔗 Paste YouTube Video URL here:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("⚡ GENERATE BOTH PDFs", use_container_width=True):
    if not video_url.strip():
        st.error("🚨 Please enter a valid YouTube URL first.")
    else:
        video_id = extract_video_id(video_url)
        
        if not video_id:
            st.error("🚨 Invalid YouTube URL format. Please check the link and try again.")
        else:
            full_raw_text = None
            with st.spinner("📥 Fetching video transcript layers..."):
                try:
                    # Attempt to fetch Hindi/Hinglish or English tracks safely
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi', 'en'])
                    
                    # Combine timestamp segments into coherent paragraph text blocks
                    raw_text_chunks = []
                    current_chunk = []
                    
                    for index, entry in enumerate(transcript_list):
                        current_chunk.append(entry['text'])
                        # Form a new paragraph block every 6 lines for readable spacing
                        if (index + 1) % 6 == 0:
                            raw_text_chunks.append(" ".join(current_chunk))
                            current_chunk = []
                    if current_chunk:
                        raw_text_chunks.append(" ".join(current_chunk))
                        
                    full_raw_text = "\n\n".join(raw_text_chunks)
                    
                except Exception as e:
                    st.error("🚨 Unable to retrieve transcripts for this video. Captions may be disabled, or the language is unsupported.")

            if full_raw_text:
                with st.spinner("⚙️ Processing engines and compiling layout documentation..."):
                    # Process Tier 2 Commercial Filtering
                    commercial_ready_text = clean_commercial_text(full_raw_text)
                    
                    # Generate In-Memory PDFs
                    pdf_raw_buffer = build_pdf(full_raw_text, f"Full Verbatim Transcript (Video ID: {video_id})")
                    pdf_commercial_buffer = build_pdf(commercial_ready_text, f"Commercial Cleaned Transcript (Video ID: {video_id})")
                    
                st.success("✅ Document processing complete! Download your files below:")
                
                # Render Mobile-Optimized Instant Action Download Layout
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📥 Download PDF 1 (Full Transcript)",
                        data=pdf_raw_buffer,
                        file_name="1_Full_Transcript.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                with col2:
                    st.download_button(
                        label="📥 Download PDF 2 (Commercial Ready)",
                        data=pdf_commercial_buffer,
                        file_name="2_Ready_To_Sell.pdf",
                        mime="application/pdf",
                        use_container_width=True
            )
    
