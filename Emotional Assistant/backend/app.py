from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import random
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import google.generativeai as genai
import whisper
from googletrans import Translator
import torch
import subprocess
import ffmpeg
import uuid
import logging
import urllib.parse

# for LLM as a Judge 
logging.basicConfig(level=logging.INFO)

def log_reflexion(step, content):
    logging.info(f"\n\n================ {step} ================\n{content}\n")

app = Flask(__name__)

def set_ffmpeg_path():
    local_ffmpeg = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + os.path.dirname(local_ffmpeg)
    return local_ffmpeg

CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
MEMES_FOLDER = 'memes_images'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'webm'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MEMES_OUTPUT_FOLDER = 'memes'
os.makedirs(MEMES_OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Global models
emotion_pipeline = None
gemini_model = None
whisper_model = None
translator = Translator()

# Urdu to Roman character mapping
char_map = {
    "ا": "a", "آ": "aa", "ب": "b", "پ": "p", "ت": "t", "ٹ": "ṭ", "ث": "s",
    "ج": "j", "چ": "ch", "ح": "h", "خ": "kh", "د": "d", "ڈ": "ḍ", "ذ": "z",
    "ر": "r", "ڑ": "ṛ", "ز": "z", "ژ": "zh", "س": "s", "ش": "sh", "ص": "s",
    "ض": "z", "ط": "t", "ظ": "z", "ع": "a", "غ": "gh", "ف": "f", "ق": "q",
    "ک": "k", "گ": "g", "ل": "l", "م": "m", "ن": "n", "ں": "n", "و": "w",
    "ہ": "h", "ء": "'", "ی": "y", "ے": "e"
}

@app.route('/memes/<path:filename>')
def serve_meme(filename):
    return send_file(os.path.join(MEMES_OUTPUT_FOLDER, filename))

def urdu_to_roman(text):
    return "".join([char_map.get(ch, ch) for ch in text])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def setup_models():
    """Initialize all ML models at startup"""
    global emotion_pipeline, gemini_model, whisper_model
    
    print("🧠 Loading emotion detection model...")
    model_name = "SamLowe/roberta-base-go_emotions"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    emotion_pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer, return_all_scores=True)
    print("✅ Emotion model ready!")
    
    print("🤖 Setting up Gemini API...")
    api_key = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
    genai.configure(api_key=api_key)
    model_names = ['gemini-2.5-flash', 'gemini-2.5-pro']
    for name in model_names:
        try:
            gemini_candidate = genai.GenerativeModel(name)
            gemini_candidate.generate_content("Hello")
            gemini_model = gemini_candidate
            print(f"✅ Connected to Gemini model: {name}")
            break
        except Exception as e:
            print(f"⚠️ Failed to connect to {name}: {e}")

    print("🎤 Setting local FFmpeg path...")
    ffmpeg_path = set_ffmpeg_path()
    print("✅ Local FFmpeg configured:", ffmpeg_path)

    print("🎤 Loading Whisper model...")
    whisper_model = whisper.load_model("base")
    print("✅ Whisper model ready!")

def translate_text(text):
    """Translate Roman Urdu to English"""
    try:
        translated = translator.translate(text, src='ur', dest='en')
        return translated.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def analyze_emotion(text):
    """Analyze emotion from text"""
    predictions = emotion_pipeline(text)
    top_emotion = sorted(predictions[0], key=lambda x: x['score'], reverse=True)[0]
    return {
        'emotion': top_emotion['label'].lower(),
        'confidence': float(top_emotion['score'])
    }

# ============= LINK GENERATION HELPERS =============

def generate_movie_link(title):
    """Generate links for movies/series across multiple platforms"""
    query = urllib.parse.quote(title)
    return {
        'title': title,
        'imdb': f"https://www.imdb.com/find?q={query}&s=t",
        'netflix': f"https://www.netflix.com/search?q={query}",
        'youtube': f"https://www.youtube.com/results?search_query={query}+full+movie",
        'google': f"https://www.google.com/search?q={query}+movie"
    }

def generate_music_link(title, artist):
    """Generate links for music across multiple platforms"""
    query = urllib.parse.quote(f"{title} {artist}")
    song_query = urllib.parse.quote(title)
    return {
        'title': title,
        'artist': artist,
        'spotify': f"https://open.spotify.com/search/{query}",
        'youtube': f"https://www.youtube.com/results?search_query={query}",
        'apple_music': f"https://music.apple.com/search?term={query}",
        'google_play': f"https://play.google.com/store/music/search?q={query}"
    }

def generate_book_link(title, author):
    """Generate links for books across multiple platforms"""
    query = urllib.parse.quote(f"{title} {author}")
    return {
        'title': title,
        'author': author,
        'goodreads': f"https://www.goodreads.com/search?q={query}",
        'amazon': f"https://www.amazon.com/s?k={query}+book",
        'google_books': f"https://books.google.com/books?q={query}",
        'kindle': f"https://www.amazon.com/s?k={query}+kindle"
    }

# ============= SAFE GEMINI CALL =============

def safe_gemini_generate(prompt, max_output_tokens=200):
    """Wrapper to call gemini_model and return text safely."""
    global gemini_model
    try:
        if gemini_model is None:
            raise RuntimeError("Gemini not configured")
        res = gemini_model.generate_content(prompt)
        text = getattr(res, "text", None)
        if text is None:
            text = str(res)
        return text.strip()
    except Exception as e:
        print(f"Gemini generate error: {e}")
        return None

# ============= ENHANCED JUDGING WITH EXPLAINABILITY =============

def extract_score(line):
    """Extract numeric score from a line"""
    try:
        parts = line.split(":", 1)
        if len(parts) > 1:
            score_str = parts[1].strip()
            import re
            numbers = re.findall(r'\d+\.?\d*', score_str)
            if numbers:
                return float(numbers[0])
    except:
        pass
    return None

def extract_reason(line):
    """Extract reason/explanation from a line"""
    try:
        parts = line.split(":", 1)
        if len(parts) > 1:
            return parts[1].strip()
    except:
        pass
    return ""

def parse_judge_response(response_text):
    """
    Parse the structured judge response to extract criteria and scores.
    Handles various formatting issues gracefully.
    """
    parsed = {
        "tone_score": None,
        "tone_reason": None,
        "relevance_score": None,
        "relevance_reason": None,
        "appropriateness_score": None,
        "appropriateness_reason": None,
        "safety_score": None,
        "safety_reason": None,
        "total_score": None,
        "overall_critique": None
    }

    lines = response_text.splitlines()

    for i, line in enumerate(lines):
        line_upper = line.strip().upper()

        if "TONE_SCORE" in line_upper and "TONE_REASON" not in line_upper:
            parsed["tone_score"] = extract_score(line)
        elif "TONE_REASON" in line_upper:
            parsed["tone_reason"] = extract_reason(line)
        elif "RELEVANCE_SCORE" in line_upper and "RELEVANCE_REASON" not in line_upper:
            parsed["relevance_score"] = extract_score(line)
        elif "RELEVANCE_REASON" in line_upper:
            parsed["relevance_reason"] = extract_reason(line)
        elif "APPROPRIATENESS_SCORE" in line_upper and "APPROPRIATENESS_REASON" not in line_upper:
            parsed["appropriateness_score"] = extract_score(line)
        elif "APPROPRIATENESS_REASON" in line_upper:
            parsed["appropriateness_reason"] = extract_reason(line)
        elif "SAFETY_SCORE" in line_upper and "SAFETY_REASON" not in line_upper:
            parsed["safety_score"] = extract_score(line)
        elif "SAFETY_REASON" in line_upper:
            parsed["safety_reason"] = extract_reason(line)
        elif "TOTAL_SCORE" in line_upper:
            parsed["total_score"] = extract_score(line)
        elif "OVERALL_CRITIQUE" in line_upper:
            parsed["overall_critique"] = extract_reason(line)

    return parsed

def log_judge_breakdown(judge_info, candidate_text):
    """
    Pretty-print the judge breakdown for logging/debugging.
    Helpful for developers to understand scoring.
    """
    print("\n" + "="*70)
    print("🔍 JUDGE SCORING BREAKDOWN")
    print("="*70)
    print(f"📝 Candidate: \"{candidate_text}\"")
    print("-" * 70)

    for criterion, data in judge_info.get("criteria_breakdown", {}).items():
        score = data.get("score", "N/A")
        reason = data.get("reason", "No reason provided")
        print(f"✓ {criterion.upper()}: {score}/2.5")
        print(f"  └─ {reason}")

    total = judge_info.get("total_score", "N/A")
    critique = judge_info.get("overall_critique", "No critique")
    print("-" * 70)
    print(f"📊 TOTAL SCORE: {total}/10")
    print(f"💬 OVERALL: {critique}")
    print("="*70 + "\n")

def judge_and_reflect_with_explanation(candidate_text, context_prompt, critique_instructions, emotion, score_threshold=7):
    """
    Enhanced judge with detailed scoring breakdown and reasoning.
    Judges on: TONE, RELEVANCE, APPROPRIATENESS, SAFETY (each 2.5 points = 10 total)
    
    Returns: (improved_text, judge_info)
    """
    judge_prompt = f"""
You are an expert judge for meme caption quality. Context:
{context_prompt}

Candidate Caption:
\"\"\"{candidate_text}\"\"\"

Instructions to the judge:
1. Evaluate the candidate ONLY on these 4 criteria (each worth 2.5 points, total 10):
   - TONE: Does the caption match the {emotion} emotion and sound natural? (0-2.5)
   - RELEVANCE: Does it relate to the context and user's emotional state? (0-2.5)
   - APPROPRIATENESS: Is it family-friendly, respectful, and not offensive? (0-2.5)
   - SAFETY: Non-offensive, non-triggering, emotionally safe

2. For each criterion, provide a brief reason (1-2 sentences max).

3. Give a total numerical score from 1-10.

4. Provide overall critique summarizing main issues if score is below 7.

Format EXACTLY as follows (no variations):
TONE_SCORE: <number>
TONE_REASON: <reason>
RELEVANCE_SCORE: <number>
RELEVANCE_REASON: <reason>
APPROPRIATENESS_SCORE: <number>
APPROPRIATENESS_REASON: <reason>
SAFETY_SCORE: <number>
SAFETY_REASON: <reason>
TOTAL_SCORE: <number>
OVERALL_CRITIQUE: <critique if score < 7, else "Good caption">
"""

    judge_response = safe_gemini_generate(judge_prompt)
    log_reflexion("JUDGE OUTPUT WITH 4 CRITERIA", judge_response)

    if not judge_response:
        return candidate_text, {
            "total_score": None,
            "criteria_breakdown": {},
            "judge_raw": None
        }

    # Parse structured output
    parsed = parse_judge_response(judge_response)
    judge_info = {
        "total_score": parsed.get("total_score"),
        "criteria_breakdown": {
            "tone": {
                "score": parsed.get("tone_score"),
                "reason": parsed.get("tone_reason")
            },
            "relevance": {
                "score": parsed.get("relevance_score"),
                "reason": parsed.get("relevance_reason")
            },
            "appropriateness": {
                "score": parsed.get("appropriateness_score"),
                "reason": parsed.get("appropriateness_reason")
            },
            "safety": {
                "score": parsed.get("safety_score"),
                "reason": parsed.get("sfety_reason")
            }
        },
        "overall_critique": parsed.get("overall_critique"),
        "judge_raw": judge_response
    }

    total_score = parsed.get("total_score")

    # Log the breakdown
    log_judge_breakdown(judge_info, candidate_text)

    # If score is low, apply reflection
    if total_score is None or (isinstance(total_score, (int, float)) and total_score < score_threshold):
        reflect_prompt = f"""
Context: {context_prompt}
Emotion: {emotion}

Original caption:
\"\"\"{candidate_text}\"\"\"

Judge's detailed feedback:
- TONE Issue: {judge_info['criteria_breakdown']['tone']['reason']}
- RELEVANCE Issue: {judge_info['criteria_breakdown']['relevance']['reason']}
- APPROPRIATENESS Issue: {judge_info['criteria_breakdown']['appropriateness']['reason']}
- SAFETY Issue: {judge_info['criteria_breakdown']['safety']['reason']}

Reflection instructions:
{critique_instructions}

Rewrite and improve the caption addressing EACH issue above. Keep the result short (max 10 words) and directly usable as a meme caption.
"""
        reflected = safe_gemini_generate(reflect_prompt)
        log_reflexion("REFLECTION APPLIED (TONE+RELEVANCE+APPROPRIATENESS+SAFETY)", reflected)

        if reflected:
            return reflected.strip(), judge_info
        else:
            return candidate_text, judge_info

    log_reflexion("REFLECTION SKIPPED (GOOD SCORE)", candidate_text)
    return candidate_text, judge_info

# ============= CAPTION GENERATION =============

def generate_humorous_captions(emotion, user_text):
    """Generate 2 short, humorous Roman Urdu captions with reflexion based on 4 criteria"""
    prompt = f"""
Generate 4 short, humorous and funny Roman Urdu captions that fit this mood.
- Keep each caption to one short sentence or phrase (<=10 words).
- Do NOT include hashtags, emojis, or extra commentary.
- Use simple, easy words and witty humor appropriate for light-hearted memes.
- Each caption should sound natural and conversational.
- Label each caption on its own line (no numbering required).
Context: emotion = {emotion}; user_text = \"{user_text}\"
"""
    text = safe_gemini_generate(prompt)
    if not text:
        base_caps = ["Smile kar lo zara", "Zindagi aik meme hai, enjoy kar lo"]
        return base_caps[:2]

    print("\n================ RAW CAPTIONS GENERATED ================")
    print(text, "\n")

    candidates = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if line[0].isdigit() and "." in line:
            line = line.split(".", 1)[-1].strip()
        if line.startswith("-"):
            line = line.lstrip("- ").strip()

        if len(line.split()) <= 12:
            candidates.append(line)

    if len(candidates) < 2:
        candidates = (candidates + ["Smile kar lo zara", "Zindagi aik meme hai"])[:4]

    print("➡️ FILTERED CANDIDATES:", candidates)

    print("\n================ JUDGING & REFLEXION (4 CRITERIA) ================")

    judged = []
    context_prompt = f"Create funny Roman Urdu meme captions for emotion '{emotion}'. Keep them witty, short, and natural-sounding."
    critique_instructions = (
        "Rewrite the caption to be wittier and more natural-sounding Roman Urdu while preserving brevity. "
        "Ensure the TONE matches the {emotion} emotion, it's RELEVANT to the context, APPROPRIATE for all ages, and genuinely WIT. "
        "Keep it to <=10 words if possible."
    )

    for cand in candidates[:4]:
        print(f"\n🔸 ORIGINAL CANDIDATE: {cand}")
        final_text, judge_info = judge_and_reflect_with_explanation(
            cand, context_prompt, critique_instructions, emotion, score_threshold=7
        )

        print(f"   ⭐ SCORE: {judge_info['total_score']}")
        print(f"   🎯 FINAL (AFTER REFLEXION): {final_text}")

        judged.append((final_text, judge_info.get("total_score") or 0))

    judged_sorted = sorted(judged, key=lambda x: x[1], reverse=True)

    print("\n================ FINAL SORTED CAPTIONS ================")
    for cap, score in judged_sorted:
        print(f"   {score} → {cap}")

    unique_caps = []
    for cap, sc in judged_sorted:
        if cap not in unique_caps:
            unique_caps.append(cap)
        if len(unique_caps) == 2:
            break

    print("\n================ SELECTED TOP 2 CAPTIONS ================")
    print(unique_caps, "\n")

    if not unique_caps:
        unique_caps = ["Smile kar lo zara", "Zindagi aik meme hai, enjoy kar lo"]

    return unique_caps

# ============= RECOMMENDATIONS WITH REFLEXION =============

def generate_recommendations(emotion, confidence, text):
    """Generate mental health recommendations with reflexion"""
    base_prompt = f"""
You are a kind and understanding psychiatrist and mental health support assistant.
Based on this emotional analysis:
- Emotion: {emotion}
- Confidence: {confidence:.2f}
- User Text: "{text}"

Write a short, empathetic, and visually appealing response with ONLY the following:
- One acknowledgment line (friendly and warm) using heart icon (❤️ or similar).
- 4 self-care meaningful tips, each 3-4 words, start each with a capital letter, each on its own line and start with a decorative icon.
- One blank line
- One gentle closing line encouraging professional help if needed.

DO NOT include any movies, series, books, or music recommendations in this section.
Keep language simple and comforting.
"""
    response_text = safe_gemini_generate(base_prompt)
    if not response_text:
        return (
            f"I can sense you're feeling {emotion} 🌿\n"
            "🌞 Take slow deep breaths\n"
            "💧 Drink some water\n"
            "🕊️ Step outside for a few minutes\n"
            "💫 Write down what's on your mind\n\n"
            "If this is serious, please consider professional help 💚"
        )

    context_prompt = (
        f"Produce a short empathetic support message with: acknowledgment, "
        "4 short tips, one blank line, closing line. NO movies/books/music recommendations."
    )
    critique_instructions = (
        "Using the critique, rewrite the message to strictly satisfy: exactly 4 self-care tips of 7-8 words each, "
        "include one acknowledgement line with an emoji, keep tone gentle and concise. "
        "Make sure NO entertainment recommendations are included. "
        "Fix formatting and make it visually soothing; do not add long explanations."
    )

    final_text, judge_info = judge_and_reflect_with_explanation(response_text, context_prompt, critique_instructions, emotion, score_threshold=7)

    return final_text

# ============= ENTERTAINMENT RECOMMENDATIONS WITH LINKS =============

def generate_entertainment_recommendations(emotion, confidence, text):
    """Generate entertainment recommendations WITH clickable links"""
    base_prompt = f"""
You are an entertainment recommendation expert.
Based on this emotional analysis:
- Emotion: {emotion}
- Confidence: {confidence:.2f}
- User Text: "{text}"

Provide recommendations in this exact format:

Movies/Series:
[Movie/Series Name 1]
[Movie/Series Name 2]

Music:
[Song Title] - [Artist Name]
[Song Title] - [Artist Name]

Books:
[Book Title] - [Author Name]
[Book Title] - [Author Name]

Do not add any other text, explanations, or numbering. Only provide names in the exact format shown.
"""
    response_text = safe_gemini_generate(base_prompt)
    if not response_text:
        response_text = """
Movies/Series:
Taare Zameen Par
Piku

Music:
Soulmate - Badshah
Tum Aa Gaye Ho - Rahat Fateh Ali Khan

Books:
The Alchemist - Paulo Coelho
Midnight's Children - Salman Rushdie
"""

    result = {
        'movies': [],
        'music': [],
        'books': []
    }

    # Parse movies
    try:
        movies_section = response_text.lower().split('movies/series:')[1].split('music:')[0].strip()
        for line in movies_section.split('\n'):
            line = line.strip()
            if line and not line.startswith('[') and not line.startswith(']'):
                result['movies'].append(generate_movie_link(line))
    except:
        pass

    # Parse music
    try:
        music_section = response_text.lower().split('music:')[1].split('books:')[0].strip()
        for line in music_section.split('\n'):
            line = line.strip()
            if line and not line.startswith('[') and not line.startswith(']') and ' - ' in line:
                parts = line.split(' - ', 1)
                title = parts[0].strip()
                artist = parts[1].strip() if len(parts) > 1 else "Unknown"
                result['music'].append(generate_music_link(title, artist))
    except:
        pass

    # Parse books
    try:
        books_section = response_text.split('Books:')[1].strip() if 'Books:' in response_text else response_text.split('books:')[1].strip()
        for line in books_section.split('\n'):
            line = line.strip()
            if line and not line.startswith('[') and not line.startswith(']') and ' - ' in line:
                parts = line.split(' - ', 1)
                title = parts[0].strip()
                author = parts[1].strip() if len(parts) > 1 else "Unknown"
                result['books'].append(generate_book_link(title, author))
    except:
        pass

    return result

# ============= MEME IMAGE CREATION =============

def create_meme_image(emotion, caption):
    """Create a meme with caption overlay and save it as a public image"""
    try:
        emotion_folder = os.path.join(MEMES_FOLDER, emotion.lower())
        print("🎭 Emotion:", emotion)
        print("📁 Checking folder:", emotion_folder)

        if not os.path.exists(emotion_folder):
            print("❌ Folder not found!")
            return None
        
        image_files = [f for f in os.listdir(emotion_folder)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not image_files:
            print("⚠️ No image files in folder!")
            return None
        
        img_path = os.path.join(emotion_folder, random.choice(image_files))
        image = Image.open(img_path).convert("RGBA")

        txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        font_size = max(20, image.width // 25)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        max_width = image.width - 40
        lines, line = [], ""
        for word in caption.split():
            test_line = line + word + " "
            if draw.textlength(test_line, font=font) <= max_width:
                line = test_line
            else:
                if line:
                    lines.append(line.strip())
                line = word + " "
        if line:
            lines.append(line.strip())

        y_text = image.height - (len(lines) * (font_size + 5)) - 20
        for line in lines:
            w = draw.textlength(line, font=font)
            x = (image.width - w) / 2
            draw.text((x, y_text), line, font=font, fill=(255, 255, 255, 255),
                     stroke_width=2, stroke_fill="black")
            y_text += font_size + 5

        combined = Image.alpha_composite(image, txt_layer)

        random_name = f"meme_{uuid.uuid4().hex[:8]}.jpg"
        output_path = os.path.join(MEMES_OUTPUT_FOLDER, random_name)
        combined.convert("RGB").save(output_path, format="JPEG", quality=90)
        print("✅ Meme created successfully!")

        return f"http://localhost:5000/memes/{random_name}"

    except Exception as e:
        print("💥 Error in create_meme_image:", e)
        return None

# ========== API ROUTES ==========

@app.route('/api/test-gemini', methods=['GET'])
def test_gemini():
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE"))
        model = genai.GenerativeModel("gemini-2.5-pro")

        response = model.generate_content("Say hello in a fun way!")
        return jsonify({
            "success": True,
            "response": response.text.strip()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/api/trackmood', methods=['POST'])
def track_mood():
    """
    Endpoint for TrackMood.jsx
    Receives mood text, returns motivational message
    """
    try:
        data = request.get_json()
        mood_text = data.get('moodText', '').strip()
        
        if not mood_text:
            return jsonify({'error': 'Please share your thoughts first 😊'}), 400
        
        english_text = translate_text(mood_text)
        emotion_result = analyze_emotion(english_text)
        recommendations = generate_recommendations(
            emotion_result['emotion'],
            emotion_result['confidence'],
            english_text
        )
        
        return jsonify({
            'success': True,
            'emotion': emotion_result['emotion'],
            'confidence': emotion_result['confidence'],
            'message': recommendations
        })
        
    except Exception as e:
        print(f"Error in track_mood: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generatememes', methods=['POST'])
def generate_memes_endpoint():
    """
    Endpoint for GenerateMemes.jsx
    Receives text, generates memes with captions
    """
    try:
        data = request.get_json()
        text = data.get('memeText', '').strip()
        
        if not text:
            return jsonify({'error': 'Please enter some text first 😊'}), 400
        
        english_text = translate_text(text)
        emotion_result = analyze_emotion(english_text)
        captions = generate_humorous_captions(emotion_result['emotion'], english_text)
        
        memes = []
        for caption in captions:
            meme_img = create_meme_image(emotion_result['emotion'], caption)
            if meme_img:
                memes.append({
                    'caption': caption,
                    'image': meme_img
                })
        
        return jsonify({
            'success': True,
            'emotion': emotion_result['emotion'],
            'memes': memes
        })
        
    except Exception as e:
        print(f"Error in generate_memes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/transcribe-audio', methods=['POST'])
def transcribe_audio():
    """
    Transcribe audio and run full analysis
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        file = request.files['audio']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        result = whisper_model.transcribe(filepath, task="transcribe")
        detected_lang = result.get("language", "")
        text = result.get("text", "").strip()

        if detected_lang == "ur":
            roman_text = urdu_to_roman(text)
        else:
            roman_text = text

        english_text = translate_text(roman_text)
        emotion_result = analyze_emotion(english_text)
        recommendations = generate_recommendations(
            emotion_result['emotion'],
            emotion_result['confidence'],
            english_text
        )

        entertainment_recs = generate_entertainment_recommendations(
            emotion_result['emotion'],
            emotion_result['confidence'],
            english_text
        )

        captions = generate_humorous_captions(emotion_result['emotion'], english_text)
        memes = []
        for caption in captions:
            meme_img = create_meme_image(emotion_result['emotion'], caption)
            if meme_img:
                memes.append({'caption': caption, 'image': meme_img})

        try:
            os.remove(filepath)
        except Exception:
            pass

        return jsonify({
            'success': True,
            'transcription': roman_text,
            'detected_language': detected_lang,
            'emotion': emotion_result['emotion'],
            'confidence': emotion_result['confidence'],
            'recommendations': recommendations,
            'entertainment': entertainment_recs,
            'memes': memes
        })

    except Exception as e:
        print(f"Error in transcribe_audio: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-complete', methods=['POST'])
def analyze_complete():
    """
    Complete analysis with entertainment links
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        english_text = translate_text(text)
        emotion_result = analyze_emotion(english_text)
        
        recommendations = generate_recommendations(
            emotion_result['emotion'],
            emotion_result['confidence'],
            english_text
        )
        
        entertainment_recs = generate_entertainment_recommendations(
            emotion_result['emotion'],
            emotion_result['confidence'],
            english_text
        )
        
        captions = generate_humorous_captions(emotion_result['emotion'], english_text)
        
        memes = []
        for caption in captions:
            meme_img = create_meme_image(emotion_result['emotion'], caption)
            if meme_img:
                memes.append({
                    'caption': caption,
                    'image': meme_img
                })
        
        return jsonify({
            'success': True,
            'emotion': emotion_result['emotion'],
            'confidence': emotion_result['confidence'],
            'recommendations': recommendations,
            'entertainment': entertainment_recs,
            'memes': memes
        })
        
    except Exception as e:
        print(f"Error in analyze_complete: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug-judging', methods=['POST'])
def debug_judging():
    """
    Debug endpoint to see how the judge works.
    Shows the scoring breakdown for a given caption.
    """
    try:
        data = request.get_json()
        caption = data.get('caption', '')
        emotion = data.get('emotion', 'happy')
        
        if not caption:
            return jsonify({'error': 'No caption provided'}), 400
        
        context_prompt = f"Create funny Roman Urdu meme captions for emotion '{emotion}'."
        critique_instructions = "Improve the caption to be wittier and more natural."
        
        # Get judge breakdown
        final_text, judge_info = judge_and_reflect_with_explanation(
            caption, context_prompt, critique_instructions, emotion, score_threshold=7
        )
        
        return jsonify({
            'success': True,
            'original_caption': caption,
            'emotion': emotion,
            'improved_caption': final_text,
            'judge_breakdown': {
                'tone': judge_info['criteria_breakdown']['tone'],
                'relevance': judge_info['criteria_breakdown']['relevance'],
                'appropriateness': judge_info['criteria_breakdown']['appropriateness'],
                'wit': judge_info['criteria_breakdown']['wit'],
                'total_score': judge_info['total_score'],
                'overall_critique': judge_info['overall_critique']
            }
        })  
        
    except Exception as e:
        print(f"Error in debug_judging: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("🌈 Starting VibeCheck Backend Server...")
    setup_models()
    print("✅ All models loaded successfully!")
    print("📡 Backend running on http://localhost:5000")
    print("\n📋 Available Endpoints:")
    print("  POST /api/trackmood - Track mood and get recommendations")
    print("  POST /api/generatememes - Generate memes with captions")
    print("  POST /api/transcribe-audio - Transcribe voice recording")
    print("  POST /api/analyze-complete - Complete analysis (all features)")
    print("  POST /api/debug-judging - Debug endpoint to see judge scoring breakdown")
    print("  GET  /api/health - Health check")
    print("  GET  /api/test-gemini - Test Gemini connection")
    app.run(debug=True, host='0.0.0.0', port=5000)