import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
import io, re, json, html
import urllib.request

# Page styling optimized for mobile view
st.set_page_config(page_title="Video-to-PDF", layout="centered")

def extract_video_id(url):
    """Extracts the 11-character YouTube video ID completely safe."""
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^"&?/\s]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript_official_google(video_id):
    """Direct connection to YouTube's official internal caption server."""
    try:
        # Step 1: Video watch page fetch karna
        url = f"https://youtube.com{video_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Content'})
        html_content = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        
        # Step 2: Internal player response block dhoodhna
        player_response_match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', html_content)
        if not player_response_match:
            # Alternate match pattern if structure varies
            player_response_match = re.search(r'var ytInitialPlayerResponse\s*=\s*({.+?});', html_content)
            
        if player_response_match:
            player_data = json.loads(player_response_match.group(1))
            captions = player_data.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
            
            if captions:
                # Target english or hindi tracks, fallback to the first one available
                track_url = captions[0]['baseUrl']
                
                # Fetch actual XML transcript string from secure server
                xml_req = urllib.request.Request(track_url, headers={'User-Agent': 'Mozilla/5.0'})
                xml_data = urllib.request.urlopen(xml_req, timeout=10).read().decode('utf-8')
                
                # Strip XML structural parameters smoothly
                text_segments = re.findall(r'text[^>]*>([^<]*)</text', xml_data)
                clean_sentences = [html.unescape(t) for t in text_segments if t]
                return " ".join(clean_sentences)
    except Exception:
        pass
    return None

def clean_transcript_text(raw_text):
    """Programmatic removal of standard advertising boilerplate lines."""
    fluff_pattern = r'(?i)\b(subscribe|like|share|channel|welcome back|bell icon|like aur share|comment below)\b'
    cleaned = re.sub(fluff_pattern, '', raw_text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def generate_pdf_buffer(text):
    """Compiles the texts layout structures to ReportLab PDF bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    custom_style = ParagraphStyle(
        name='MobileOptimized',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY
    )
    
    flowables = []
    words = text.split()
    paragraph_chunks = [" ".join(words[i:i + 75]) for i in range(0, len(words), 75)]
    
    for chunk in paragraph_chunks:
        flowables.append(Paragraph(chunk, custom_style))
        flowables.append(Spacer(1, 14))
        
    doc.build(flowables)
    buffer.seek(0)
    return buffer

# Application Graphical Elements Dashboard Rendering
st.markdown("<h2 style='text-align: center; font-family: sans-serif;'>🤖 Ultra Max Video-to-PDF Converter</h2>", unsafe_allow_html=True)
st.markdown("---")

url_input = st.text_input("Paste YouTube Video URL Link here:", placeholder="https://youtube.com...")

st.write("") 

if st.button("⚡ GENERATE BOTH PDFs", use_container_width=True):
    if not url_input.strip():
        st.error("Please enter a valid YouTube URL.")
    else:
        video_id = extract_video_id(url_input)
        if not video_id:
            st.error("🚨 Invalid link format. Paste a proper YouTube URL link.")
        else:
            try:
                with st.spinner("Extracting transcript securely from official servers..."):
                    raw_text = get_transcript_official_google(video_id)
                    
                    if not raw_text or len(raw_text.strip()) < 10:
                        st.error("🚨 Text extraction failed! Captions are turned off/disabled by the creator on this video.")
                    else:
                        clean_text = clean_transcript_text(raw_text)
                        
                        pdf1_buffer = generate_pdf_buffer(raw_text)
                        pdf2_buffer = generate_pdf_buffer(clean_text)
                        
                        st.success("✅ Document processing complete! Download below:")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(label="📥 Download PDF 1 (Full)", data=pdf1_buffer, file_name="Raw_Transcript.pdf", mime="application/pdf", use_container_width=True)
                        with col2:
                            st.download_button(label="📥 Download PDF 2 (Clean)", data=pdf2_buffer, file_name="Clean_Transcript.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Processing conflict encountered: {str(e)}")
