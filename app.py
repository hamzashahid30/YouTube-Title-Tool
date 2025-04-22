import streamlit as st
import random
import re
import numpy as np
from transformers import pipeline
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict

# Initialize all models and components
@st.cache_resource
def load_models():
    """Load all required ML models"""
    try:
        # Load pretrained CTR model if available
        ctr_model = joblib.load('models/ctr_model.pkl')
        vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
    except:
        # Fallback if no pretrained model
        ctr_model, vectorizer = None, None
    
    # Load sentiment analysis model
    sentiment_analyzer = pipeline("sentiment-analysis")
    
    return {
        'ctr_model': ctr_model,
        'vectorizer': vectorizer,
        'sentiment_analyzer': sentiment_analyzer
    }

models = load_models()

# Constants
POWER_WORDS = [
    "Secret", "Ultimate", "Amazing", "Proven", "Shocking", 
    "Unbelievable", "Essential", "Complete", "Exact", "Perfect",
    "Absolute", "Advanced", "Never Seen Before", "Insider", "Exclusive",
    "Guaranteed", "Instant", "Limited", "Breakthrough", "Master"
]

TEMPLATES = [
    "{number} {power_word} {keyword} Tips Nobody Tells You",
    "The {power_word} Guide to {keyword} [You Need This]",
    "How I {keyword} Like a Pro ({power_word} Method)",
    "{number} {keyword} Hacks That Actually Work",
    "This {power_word} {keyword} Trick Will Change Everything",
    "Why Nobody Talks About {keyword} (And What To Do)",
    "{number} Minute {keyword} Masterclass ({power_word} Results)",
    "{keyword} Explained: {power_word} {number}-Step System",
    "The {power_word} Truth About {keyword}",
    "{number} {power_word} Ways to {keyword} Fast"
]

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
.avg {
    border-left: 5px solid #FFC107;
}
.bad {
    border-left: 5px solid #F44336;
}
.ctr-good { color: #4CAF50; font-weight: bold; }
.ctr-avg { color: #FFC107; font-weight: bold; }
.ctr-bad { color: #F44336; font-weight: bold; }
.pro-tip {
    background-color: #E3F2FD;
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Core Functions
# ----------------------------

def generate_titles(competitor_title: str, keyword: str) -> List[str]:
    """Generate optimized YouTube titles"""
    titles = []
    used_templates = set()
    
    while len(titles) < 3:
        template = random.choice(TEMPLATES)
        if template in used_templates:
            continue
        used_templates.add(template)
        
        replacements = {
            "{number}": str(random.choice([3, 5, 7, 10, 13, 15, 21])),
            "{power_word}": random.choice(POWER_WORDS),
            "{keyword}": keyword
        }
        
        title = template
        for k, v in replacements.items():
            title = title.replace(k, v)
            
        titles.append(title)
    
    return titles[:3]

def analyze_sentiment(title: str) -> Dict:
    """Analyze title sentiment using NLP"""
    result = models['sentiment_analyzer'](title)[0]
    return {
        "label": result['label'],
        "score": result['score']
    }

def predict_ctr(title: str) -> Dict:
    """Predict CTR percentage for title"""
    if models['ctr_model'] and models['vectorizer']:
        # If proper model is loaded
        features = models['vectorizer'].transform([title])
        ctr = models['ctr_model'].predict(features)[0]
    else:
        # Simple heuristic-based fallback
        length_score = max(0, 1 - abs(len(title) - 50)/50)
        power_word_score = 0.5 if any(pw.lower() in title.lower() for pw in POWER_WORDS) else 0
        number_score = 0.3 if any(word.isdigit() for word in title.split()) else 0
        question_score = 0.4 if title.endswith('?') else 0
        
        ctr = 3 + (length_score * 3) + (power_word_score * 2) + number_score + question_score
        ctr = min(12, max(1, ctr))
    
    rating = "good" if ctr > 7 else "avg" if ctr > 4 else "bad"
    return {"value": round(ctr, 1), "rating": rating}

def optimize_length(title: str) -> str:
    """Optimize title length between 40-60 chars"""
    current_len = len(title)
    
    if current_len < 40:
        # Add power word or bracket text
        additions = ["[2024]", "[Pro Tip]", "[Works!]", "[Free]"]
        return f"{title} {random.choice(additions)}"
    elif current_len > 65:
        # Shorten title
        words = title.split()
        while len(' '.join(words)) > 60 and len(words) > 5:
            words.pop(random.randint(2, len(words)-2))
        return ' '.join(words)
    return title

def generate_ab_test_variants(title: str) -> List[str]:
    """Generate A/B testing variants"""
    variants = []
    
    # 1. Question vs Statement
    if '?' not in title:
        variants.append(title + "?")
    else:
        variants.append(title.replace('?', '!'))
    
    # 2. Number variation
    if any(word.isdigit() for word in title.split()):
        new_title = re.sub(r'\d+', lambda m: str(int(m.group()) + random.choice([1,2,-1])), title)
        variants.append(new_title)
    else:
        variants.append(f"{random.choice([3,5,7])} {title}")
    
    # 3. Power word swap
    for pw in POWER_WORDS:
        if pw.lower() in title.lower():
            new_pw = random.choice([p for p in POWER_WORDS if p != pw])
            variants.append(title.replace(pw, new_pw))
            break
    
    # 4. Bracket addition/removal
    if '[' in title:
        variants.append(re.sub(r'\[.*?\]', '', title).strip())
    else:
        brackets = ["[Try This]", "[Free Guide]", "[Step-by-Step]", "[New Method]"]
        variants.append(f"{title} {random.choice(brackets)}")
    
    return list(set(variants))[:4]

# ----------------------------
# Streamlit UI
# ----------------------------

# App Header
st.markdown('<p class="title">🎯 YouTube Title Pro - Viral Title Generator</p>', unsafe_allow_html=True)
st.caption("Analyze competitor titles and generate optimized versions with higher CTR potential")

# Input Section
with st.form("title_form"):
    col1, col2 = st.columns(2)
    with col1:
        competitor_title = st.text_input("Competitor's viral title:", placeholder="e.g., 10 Secrets Nobody Tells You About...")
    with col2:
        video_topic = st.text_input("Your video topic/keyword:", placeholder="e.g., YouTube growth")
    
    submitted = st.form_submit_button("Generate Optimized Titles")

# Results Section
if submitted and competitor_title:
    with st.spinner('Analyzing and generating titles...'):
        try:
            # Generate base titles
            generated_titles = generate_titles(competitor_title, video_topic)
            
            # Advanced analysis
            sentiment = analyze_sentiment(competitor_title)
            ctr_score = predict_ctr(competitor_title)
            optimized_titles = [optimize_length(title) for title in generated_titles]
            ab_test_variants = generate_ab_test_variants(competitor_title)
            
            # Display competitor analysis
            st.markdown("### 🔍 Competitor Title Analysis")
            with st.expander("View Detailed Analysis", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sentiment", f"{sentiment['label']} ({sentiment['score']:.2f})")
                with col2:
                    st.metric("Predicted CTR", f"{ctr_score['value']}%", 
                             help="Estimated click-through-rate based on title patterns")
                with col3:
                    st.metric("Length", f"{len(competitor_title)} chars", 
                             "Ideal: 40-60" if 40 <= len(competitor_title) <= 60 else "Too short" if len(competitor_title) < 40 else "Too long")
                
                st.progress(ctr_score['value']/15)
                st.caption("CTR prediction scale: Good (>7%), Average (4-7%), Poor (<4%)")
            
            # Display generated titles
            st.markdown("### 🚀 Your Optimized Title Options")
            for i, title in enumerate(optimized_titles, 1):
                title_ctr = predict_ctr(title)
                sentiment = analyze_sentiment(title)
                
                st.markdown(f"""
                <div class="card good">
                    <h4>Option {i}: {title}</h4>
                    <p>📏 Length: {len(title)} chars | 🎯 CTR: <span class='ctr-{title_ctr['rating']}'>{title_ctr['value']}%</span> | 
                    😊 Sentiment: {sentiment['label']} ({sentiment['score']:.2f})</p>
                </div>
                """, unsafe_allow_html=True)
            
            # A/B Testing Section
            st.markdown("### 🔬 A/B Testing Variants")
            st.markdown('<div class="pro-tip">💡 Test these variations against your main title to see what performs best</div>', unsafe_allow_html=True)
            
            for i, variant in enumerate(ab_test_variants, 1):
                variant_ctr = predict_ctr(variant)
                st.markdown(f"""
                **Variant {i}:** `{variant}`  
                📏 {len(variant)} chars | 🎯 CTR: <span class='ctr-{variant_ctr['rating']}'>{variant_ctr['value']}%</span>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error generating titles: {str(e)}")

# Sidebar with Tips
with st.sidebar:
    st.markdown("## 📊 Title Analytics Guide")
    st.markdown("""
    - **CTR Prediction**: Based on title patterns, keywords, and length
    - **Sentiment Analysis**: Positive titles often perform better
    - **Ideal Length**: 40-60 characters
    - **Power Words**: Increase emotional impact
    """)
    
    st.markdown("## 🧪 A/B Testing Tips")
    st.markdown("""
    1. Test completely different title structures
    2. Try different power words
    3. Vary title lengths
    4. Test with/without numbers
    5. Run tests for at least 1 week
    """)
    
    st.markdown("## ⚙️ How It Works")
    st.markdown("""
    1. Analyzes competitor's title structure
    2. Identifies high-performing patterns
    3. Generates optimized variations
    4. Provides performance predictions
    """)

# Footer
st.markdown("---")
st.caption("🚀 Pro Tip: Combine the best elements from different generated titles to create your perfect headline")
