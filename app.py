import streamlit as st
import random
import re
from textblob import TextBlob

# Custom CSS
st.set_page_config(page_title="YouTube Title Pro", page_icon="📊", layout="wide")
st.markdown("""
<style>
.title {
    font-size: 28px !important;
    color: #FF0000 !important;
    font-weight: bold !important;
    text-align: center;
}
.card {
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
}
.good {
    border-left: 5px solid #4CAF50;
}
</style>
""", unsafe_allow_html=True)

# Constants
POWER_WORDS = [
    "Secret", "Ultimate", "Amazing", "Proven", "Shocking",
    "Essential", "Complete", "Perfect", "Advanced", "Insider"
]

TEMPLATES = [
    "{number} {power_word} {keyword} Tips Nobody Tells You",
    "The {power_word} Guide to {keyword} [You Need This]",
    "How I {keyword} Like a Pro ({power_word} Method)",
    "{number} {keyword} Hacks That Actually Work",
    "This {power_word} {keyword} Trick Will Change Everything"
]

# Core Functions
def generate_titles(competitor_title: str, keyword: str) -> list:
    """Generate optimized YouTube titles"""
    titles = []
    for _ in range(3):
        template = random.choice(TEMPLATES)
        title = template.replace("{number}", str(random.choice([3, 5, 7, 10]))) \
                       .replace("{power_word}", random.choice(POWER_WORDS)) \
                       .replace("{keyword}", keyword)
        titles.append(title)
    return titles

def analyze_sentiment(title: str) -> dict:
    """Simple sentiment analysis using TextBlob"""
    analysis = TextBlob(title)
    score = analysis.sentiment.polarity
    label = "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"
    return {"label": label, "score": score}

def optimize_length(title: str) -> str:
    """Optimize title length between 40-60 chars"""
    if len(title) < 40:
        return f"{title} [Pro Tip]"
    elif len(title) > 65:
        return ' '.join(title.split()[:8])
    return title

# UI Components
st.markdown('<p class="title">🎯 YouTube Title Generator</p>', unsafe_allow_html=True)

with st.form("title_form"):
    competitor_title = st.text_input("Competitor's viral title:", 
                                   placeholder="e.g., 10 Secrets Nobody Tells You About...")
    video_topic = st.text_input("Your video topic/keyword:", 
                               placeholder="e.g., YouTube growth")
    submitted = st.form_submit_button("Generate Titles")

if submitted and competitor_title:
    with st.spinner('Generating optimized titles...'):
        try:
            # Generate and display titles
            generated_titles = generate_titles(competitor_title, video_topic)
            
            st.markdown("### 🚀 Your Optimized Title Options")
            for i, title in enumerate(generated_titles, 1):
                optimized = optimize_length(title)
                sentiment = analyze_sentiment(optimized)
                
                st.markdown(f"""
                <div class="card good">
                    <h4>Option {i}: {optimized}</h4>
                    <p>📏 Length: {len(optimized)} chars | 😊 Sentiment: {sentiment['label']}</p>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error generating titles: {str(e)}")

# Sidebar Tips
with st.sidebar:
    st.markdown("## 💡 Pro Tips")
    st.markdown("""
    - Use numbers (3, 5, 7, 10)
    - Include power words
    - Keep length 40-60 chars
    - Positive titles perform better
    """)
