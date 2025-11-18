import streamlit as st
import requests
import feedparser
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Valid News",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    .subtitle {
        font-size: 1.3rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* News card styling */
    .news-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .news-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    .news-card:hover::before {
        opacity: 1;
    }
    .news-card h3 {
        color: #1e293b;
        margin-top: 0;
        margin-bottom: 0.75rem;
        font-size: 1.25rem;
        font-weight: 700;
        line-height: 1.4;
        position: relative;
        z-index: 1;
    }
    .news-meta {
        color: #64748b;
        font-size: 0.875rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        position: relative;
        z-index: 1;
    }
    .news-snippet {
        color: #475569;
        margin: 1rem 0;
        line-height: 1.7;
        font-size: 0.95rem;
        position: relative;
        z-index: 1;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.625rem 1.75rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    .stButton>button:hover::before {
        left: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px -2px rgba(102, 126, 234, 0.4);
    }
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Result box styling */
    .result-box {
        padding: 1.5rem;
        border-radius: 12px;
        margin-top: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.3s ease-out;
        position: relative;
        overflow: hidden;
    }
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .result-real {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 5px solid #10b981;
        color: #065f46;
    }
    .result-fake {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 5px solid #ef4444;
        color: #991b1b;
    }
    .result-unverified {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 5px solid #f59e0b;
        color: #92400e;
    }
    .result-box h3 {
        margin-top: 0;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        font-weight: 700;
    }
    .result-box p {
        margin: 0.5rem 0;
        line-height: 1.6;
    }
    .result-box strong {
        font-weight: 700;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
    }
    [data-testid="stSidebar"] .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Input styling */
    .stTextInput input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Link styling */
    a {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s ease;
    }
    a:hover {
        color: #764ba2;
        text-decoration: underline;
    }
    
    /* Badge styling for labels */
    .label-badge {
        display: inline-block;
        padding: 0.375rem 0.875rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.875rem;
        margin-right: 0.5rem;
    }
    .label-real {
        background-color: #10b981;
        color: white;
    }
    .label-fake {
        background-color: #ef4444;
        color: white;
    }
    .label-unverified {
        background-color: #f59e0b;
        color: white;
    }
    
    /* Confidence bar */
    .confidence-bar {
        height: 8px;
        border-radius: 4px;
        background-color: #e2e8f0;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    .confidence-fill {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.5s ease;
    }
    
    /* Subheader styling */
    h2 {
        color: #1e293b;
        font-weight: 700;
        font-size: 1.75rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        border-radius: 10px;
        border-left: 4px solid #10b981;
    }
    .stError {
        border-radius: 10px;
        border-left: 4px solid #ef4444;
    }
    .stWarning {
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
    }
    .stInfo {
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# Demo data fallback
DEMO_INDIAN_NEWS = [
    {
        "title": "Government announces new scholarship for engineering students",
        "source": "pib.gov.in",
        "published": "2024-01-15T10:00:00Z",
        "summary": "Official press release from the Ministry of Education describing eligibility and dates.",
        "link": "https://pib.gov.in"
    },
    {
        "title": "India's GDP grows by 7.2% in Q3",
        "source": "The Economic Times",
        "published": "2024-01-14T08:00:00Z",
        "summary": "India's economy shows strong growth momentum with GDP expanding at 7.2% in the third quarter.",
        "link": "https://economictimes.indiatimes.com"
    },
    {
        "title": "New metro line inaugurated in Mumbai",
        "source": "Hindustan Times",
        "published": "2024-01-13T12:00:00Z",
        "summary": "Prime Minister inaugurates new metro line connecting key areas of Mumbai.",
        "link": "https://www.hindustantimes.com"
    }
]

DEMO_INTERNATIONAL_NEWS = [
    {
        "title": "Global climate summit reaches historic agreement",
        "source": "BBC News",
        "published": "2024-01-15T14:00:00Z",
        "summary": "World leaders agree on ambitious targets to reduce carbon emissions by 2030.",
        "link": "https://www.bbc.com/news"
    },
    {
        "title": "Tech giant announces breakthrough in AI research",
        "source": "Reuters",
        "published": "2024-01-14T16:00:00Z",
        "summary": "Major technology company reveals new AI model capable of advanced reasoning.",
        "link": "https://www.reuters.com"
    },
    {
        "title": "Space mission successfully lands on Mars",
        "source": "NASA",
        "published": "2024-01-13T18:00:00Z",
        "summary": "Latest Mars rover mission completes successful landing and begins exploration.",
        "link": "https://www.nasa.gov"
    }
]

def parse_rss(url):
    """Parse RSS feed and return list of news items."""
    try:
        feed = feedparser.parse(url)
        news_items = []
        for entry in feed.entries[:10]:  # Get top 10
            news_items.append({
                "title": entry.get("title", "No title"),
                "source": entry.get("source", {}).get("title", "Unknown source") if hasattr(entry, "source") else entry.get("link", "Unknown"),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", entry.get("description", "No summary available")),
                "link": entry.get("link", "#")
            })
        return news_items
    except Exception as e:
        st.sidebar.error(f"RSS parsing error: {str(e)}")
        return []

def fetch_indian_news(use_demo=False):
    """Fetch Indian news from RSS feed or return demo data."""
    if use_demo:
        return DEMO_INDIAN_NEWS
    
    url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
    news = parse_rss(url)
    if not news:
        return DEMO_INDIAN_NEWS
    return news

def fetch_international_news(use_demo=False):
    """Fetch International news from RSS feed or return demo data."""
    if use_demo:
        return DEMO_INTERNATIONAL_NEWS
    
    url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    news = parse_rss(url)
    if not news:
        return DEMO_INTERNATIONAL_NEWS
    return news

def call_aiml(title, content, source):
    """
    Call AIML API to classify news article.
    Returns JSON with label, confidence, explanation, and highlights.
    """
    api_key = os.getenv("AIML_API_KEY")
    
    if not api_key:
        return {
            "label": "Unverified",
            "confidence": 0.0,
            "explanation": "API key not found. Please set AIML_API_KEY environment variable.",
            "highlights": []
        }
    
    # Construct the prompt
    prompt = f"""You are an expert fact-checking assistant. I will give you a news article title, content snippet, and source.

Task:
1) Briefly reason (1 sentence) about the veracity of the article.
2) Then output EXACTLY valid JSON with keys:
   {{
     "label": "Real" | "Fake" | "Unverified",
     "confidence": float between 0 and 1,
     "explanation": "one or two sentence reason",
     "highlights": ["keyword1","keyword2", ...]
   }}

Rules:
- First think very shortly, then output **only the JSON**.
- No extra text outside JSON.
- Use the style and values from the examples.

EXAMPLES:
Input:
title: "Government announces new scholarship for engineering students"
content: "Official press release from the Ministry of Education describing eligibility and dates."
source: "pib.gov.in"

JSON:
{{"label":"Real","confidence":0.95,"explanation":"Official government release with verifiable source.","highlights":["press release","pib.gov.in"]}}


Input:
title: "Miracle herbal pill cures diabetes overnight"
content: "A celebrity claims a pill can cure diabetes with no scientific backing."
source: "randomblog.xyz"

JSON:
{{"label":"Fake","confidence":0.85,"explanation":"Extraordinary claim without any scientific evidence.","highlights":["miracle cure","no evidence"]}}


NOW INPUT:
title: "{title}"
content: "{content}"
source: "{source}"
"""
    
    # Try different AIML models (using Mistral and other open models)
    models_to_try = ["mistralai/Mistral-7B-Instruct-v0.2", "mistralai/Mixtral-8x7B-Instruct-v0.1", "meta-llama/Llama-2-7b-chat-hf"]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    url = "https://api.aimlapi.com/v1/chat/completions"
    
    response = None
    last_error = None
    for model_name in models_to_try:
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            break  # Success, exit the loop
        except requests.exceptions.HTTPError as e:
            last_error = e
            if response:
                status_code = response.status_code
                
                # Handle rate limiting (429)
                if status_code == 429:
                    retry_after = response.headers.get('Retry-After', 'unknown')
                    return {
                        "label": "Unverified",
                        "confidence": 0.0,
                        "explanation": f"Rate limit exceeded. Too many requests to AIML API. Please wait a moment and try again. (Retry after: {retry_after} seconds)",
                        "highlights": []
                    }
                
                # Handle authentication errors (401)
                if status_code == 401:
                    return {
                        "label": "Unverified",
                        "confidence": 0.0,
                        "explanation": "Invalid API key. Please check your AIML_API_KEY in the .env file.",
                        "highlights": []
                    }
                
                # Handle insufficient quota (402)
                if status_code == 402:
                    return {
                        "label": "Unverified",
                        "confidence": 0.0,
                        "explanation": "Insufficient quota. Your AIML API account has exceeded its usage limit. Please check your billing or upgrade your plan.",
                        "highlights": []
                    }
                
                # Handle model not found (404)
                if status_code == 404:
                    # Model not found, try next model
                    continue
                
                # Other HTTP errors
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                except:
                    error_msg = response.text[:200] if response.text else "Unknown error"
                
                return {
                    "label": "Unverified",
                    "confidence": 0.0,
                    "explanation": f"API error (Status {status_code}): {error_msg}",
                    "highlights": []
                }
            else:
                return {
                    "label": "Unverified",
                    "confidence": 0.0,
                    "explanation": f"API error: {str(e)}",
                    "highlights": []
                }
        except requests.exceptions.Timeout:
            return {
                "label": "Unverified",
                "confidence": 0.0,
                "explanation": "Request timed out. The API took too long to respond. Please try again.",
                "highlights": []
            }
        except Exception as e:
            last_error = e
            return {
                "label": "Unverified",
                "confidence": 0.0,
                "explanation": f"Request error: {str(e)}",
                "highlights": []
            }
    
    # If we get here without a successful response, all models failed
    if not response:
        return {
            "label": "Unverified",
            "confidence": 0.0,
            "explanation": f"API model not found. Please check your API key and available models. Tried: {', '.join(models_to_try)}",
            "highlights": []
        }
    
    try:
        result = response.json()
        
        # Extract text from AIML API response
        if "choices" in result and len(result["choices"]) > 0:
            text_content = result["choices"][0]["message"]["content"]
            
            # Try to extract JSON from response
            # Remove markdown code blocks if present
            text_content = text_content.strip()
            if text_content.startswith("```json"):
                text_content = text_content[7:]
            if text_content.startswith("```"):
                text_content = text_content[3:]
            if text_content.endswith("```"):
                text_content = text_content[:-3]
            text_content = text_content.strip()
            
            # Try to find JSON object
            try:
                # Find JSON object boundaries
                start_idx = text_content.find("{")
                end_idx = text_content.rfind("}") + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = text_content[start_idx:end_idx]
                    classification = json.loads(json_str)
                    return classification
            except json.JSONDecodeError:
                pass
            
            # If JSON parsing fails, return unverified
            return {
                "label": "Unverified",
                "confidence": 0.0,
                "explanation": "Could not parse model response. Please try again.",
                "highlights": []
            }
        else:
            return {
                "label": "Unverified",
                "confidence": 0.0,
                "explanation": "Invalid response from model.",
                "highlights": []
            }
            
    except requests.exceptions.Timeout:
        return {
            "label": "Unverified",
            "confidence": 0.0,
            "explanation": "Request timed out. Please try again.",
            "highlights": []
        }
    except requests.exceptions.RequestException as e:
        return {
            "label": "Unverified",
            "confidence": 0.0,
            "explanation": f"Network error: {str(e)}",
            "highlights": []
        }
    except Exception as e:
        return {
            "label": "Unverified",
            "confidence": 0.0,
            "explanation": f"Error: {str(e)}",
            "highlights": []
        }

def classify_text_block(text, source="User Input"):
    """Classify a text block entered by the user."""
    if not text.strip():
        st.warning("Please enter some text to classify.")
        return None
    
    # Extract title and content (simple heuristic: first line as title, rest as content)
    lines = text.strip().split("\n")
    title = lines[0] if lines else "User Input"
    content = "\n".join(lines[1:]) if len(lines) > 1 else text
    
    return call_aiml(title, content, source)

# Initialize session state
if "indian_news" not in st.session_state:
    st.session_state.indian_news = []
if "international_news" not in st.session_state:
    st.session_state.international_news = []
if "use_demo" not in st.session_state:
    st.session_state.use_demo = False

# Sidebar
with st.sidebar:
    st.title("📰 Valid News")
    st.markdown("---")
    
    if st.button("🔄 Refresh News", use_container_width=True):
        with st.spinner("Fetching latest news..."):
            st.session_state.indian_news = fetch_indian_news(st.session_state.use_demo)
            st.session_state.international_news = fetch_international_news(st.session_state.use_demo)
        st.success("News refreshed!")
    
    st.session_state.use_demo = st.checkbox("Use Demo Data", value=st.session_state.use_demo)
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    **Valid News** uses AI to help detect fake news.
    
    - Fetches real-time headlines
    - Classifies using AIML API
    - Provides confidence scores
    """)
    
    # Check API key status
    api_key = os.getenv("AIML_API_KEY")
    if api_key:
        st.success("✅ API Key Loaded")
    else:
        st.error("❌ API Key Not Found")
        st.info("Set AIML_API_KEY environment variable")

# Main header
st.markdown('<h1 class="main-header">Valid News</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Indian & International Fake News Detection</p>', unsafe_allow_html=True)

# Tabs for Indian and International news
tab1, tab2, tab3 = st.tabs(["🇮🇳 Indian News", "🌍 International News", "✍️ Custom Text"])

# Indian News Tab
with tab1:
    if not st.session_state.indian_news:
        with st.spinner("Loading Indian news..."):
            st.session_state.indian_news = fetch_indian_news(st.session_state.use_demo)
    
    st.subheader("Latest Indian Headlines")
    
    for idx, article in enumerate(st.session_state.indian_news):
        with st.container():
            st.markdown(f"""
                <div class="news-card">
                    <h3>{article['title']}</h3>
                    <div class="news-meta">
                        <strong>Source:</strong> {article['source']} | 
                        <strong>Published:</strong> {article.get('published', 'N/A')}
                    </div>
                    <div class="news-snippet">{article['summary']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🔍 Classify", key=f"classify_indian_{idx}"):
                    with st.spinner("Analyzing..."):
                        result = call_aiml(
                            article['title'],
                            article['summary'],
                            article['source']
                        )
                        st.session_state[f"result_indian_{idx}"] = result
            
            with col2:
                if article['link'] != "#":
                    st.markdown(f"[🔗 Open Source Link]({article['link']})", unsafe_allow_html=True)
            
            # Display result if available
            if f"result_indian_{idx}" in st.session_state:
                result = st.session_state[f"result_indian_{idx}"]
                label = result.get("label", "Unverified")
                confidence = result.get("confidence", 0.0)
                explanation = result.get("explanation", "")
                highlights = result.get("highlights", [])
                
                result_class = "result-unverified"
                if label == "Real":
                    result_class = "result-real"
                elif label == "Fake":
                    result_class = "result-fake"
                
                highlights_text = ", ".join(highlights) if highlights else "None"
                label_class = f"label-{label.lower()}"
                confidence_width = int(confidence * 100)
                
                st.markdown(f"""
                    <div class="result-box {result_class}">
                        <h3>Classification Result</h3>
                        <p>
                            <span class="label-badge {label_class}">{label}</span>
                            <strong>Confidence:</strong> {confidence:.1%}
                        </p>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: {confidence_width}%"></div>
                        </div>
                        <p><strong>Explanation:</strong> {explanation}</p>
                        <p><strong>Highlights:</strong> {highlights_text}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")

# International News Tab
with tab2:
    if not st.session_state.international_news:
        with st.spinner("Loading International news..."):
            st.session_state.international_news = fetch_international_news(st.session_state.use_demo)
    
    st.subheader("Latest International Headlines")
    
    for idx, article in enumerate(st.session_state.international_news):
        with st.container():
            st.markdown(f"""
                <div class="news-card">
                    <h3>{article['title']}</h3>
                    <div class="news-meta">
                        <strong>Source:</strong> {article['source']} | 
                        <strong>Published:</strong> {article.get('published', 'N/A')}
                    </div>
                    <div class="news-snippet">{article['summary']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🔍 Classify", key=f"classify_intl_{idx}"):
                    with st.spinner("Analyzing..."):
                        result = call_aiml(
                            article['title'],
                            article['summary'],
                            article['source']
                        )
                        st.session_state[f"result_intl_{idx}"] = result
            
            with col2:
                if article['link'] != "#":
                    st.markdown(f"[🔗 Open Source Link]({article['link']})", unsafe_allow_html=True)
            
            # Display result if available
            if f"result_intl_{idx}" in st.session_state:
                result = st.session_state[f"result_intl_{idx}"]
                label = result.get("label", "Unverified")
                confidence = result.get("confidence", 0.0)
                explanation = result.get("explanation", "")
                highlights = result.get("highlights", [])
                
                result_class = "result-unverified"
                if label == "Real":
                    result_class = "result-real"
                elif label == "Fake":
                    result_class = "result-fake"
                
                highlights_text = ", ".join(highlights) if highlights else "None"
                label_class = f"label-{label.lower()}"
                confidence_width = int(confidence * 100)
                
                st.markdown(f"""
                    <div class="result-box {result_class}">
                        <h3>Classification Result</h3>
                        <p>
                            <span class="label-badge {label_class}">{label}</span>
                            <strong>Confidence:</strong> {confidence:.1%}
                        </p>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: {confidence_width}%"></div>
                        </div>
                        <p><strong>Explanation:</strong> {explanation}</p>
                        <p><strong>Highlights:</strong> {highlights_text}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")

# Custom Text Tab
with tab3:
    st.subheader("Classify Your Own Text")
    st.markdown("Paste any headline or article text below to classify it.")
    
    user_text = st.text_area(
        "Enter news headline/article:",
        height=150,
        placeholder="Paste your news headline or article text here..."
    )
    
    user_source = st.text_input("Source (optional):", placeholder="e.g., BBC News, Twitter, etc.")
    
    if st.button("🔍 Classify Text", use_container_width=True):
        if user_text.strip():
            with st.spinner("Analyzing your text..."):
                result = classify_text_block(user_text, user_source if user_source else "User Input")
                
                if result:
                    label = result.get("label", "Unverified")
                    confidence = result.get("confidence", 0.0)
                    explanation = result.get("explanation", "")
                    highlights = result.get("highlights", [])
                    
                    result_class = "result-unverified"
                    if label == "Real":
                        result_class = "result-real"
                    elif label == "Fake":
                        result_class = "result-fake"
                    
                    highlights_text = ", ".join(highlights) if highlights else "None"
                    label_class = f"label-{label.lower()}"
                    confidence_width = int(confidence * 100)
                    
                    st.markdown(f"""
                        <div class="result-box {result_class}">
                            <h3>Classification Result</h3>
                            <p>
                                <span class="label-badge {label_class}">{label}</span>
                                <strong>Confidence:</strong> {confidence:.1%}
                            </p>
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: {confidence_width}%"></div>
                            </div>
                            <p><strong>Explanation:</strong> {explanation}</p>
                            <p><strong>Highlights:</strong> {highlights_text}</p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Please enter some text to classify.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #64748b; padding: 2.5rem 1rem; background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%); border-radius: 12px; margin-top: 3rem;'>
        <p style='margin: 0; font-size: 0.95rem; font-weight: 500;'>
            📰 <strong>Valid News</strong> - AI-Powered Fact Checking
        </p>
        <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #94a3b8;'>
            Built with Streamlit & AIML API
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

