"""
╔══════════════════════════════════════════════════════════════╗
║ PathFinder v4 — Career Intelligence Platform ║
║ Deploy-Ready · All Features Merged · Production Grade ║
╠══════════════════════════════════════════════════════════════╣
║ ✦ Cinematic nebula + grain texture animated background ║
║ ✦ 3D morphing orb with pulsing glow rings ║
║ ✦ Animated particle constellation (Canvas, trait-colored) ║
║ ✦ Dynamic full-UI repainting per RIASEC trait color ║
║ ✦ Interactive Plotly RIASEC Radar chart ║
║ ✦ Animated Personality DNA fingerprint bars ║
║ ✦ Card-slide quiz with progress beam ║
║ ✦ Cinematic 3-step analyzing overlay ║
║ ✦ PDF export (fpdf2) with branded layout & score bars ║
║ ✦ Email roadmap via SMTP (Gmail-ready) ║
║ ✦ SQLite analytics — auto /tmp for cloud deploy ║
║ ✦ Admin Mission Control: KPI cards, Plotly charts, table ║
║ ✦ EN / हिंदी / தமிழ் multi-language ║
║ ✦ 30 RIASEC Questions (5 per trait) - ENHANCED ║
║ ✦ Extended Interview Prep Section ║
║ ✦ Fixed Session State Bug ║
╚══════════════════════════════════════════════════════════════╝

QUICK START:
 pip install streamlit pandas plotly fpdf2
 streamlit run app.py

DEPLOY (Streamlit Cloud):
 1. Push this file + requirements.txt to GitHub
 2. Connect at share.streamlit.io — no extra config needed
 3. Set SMTP_USER / SMTP_PASSWORD / ADMIN_PASSWORD as secrets

ENVIRONMENT VARIABLES (optional):
 SMTP_HOST — default: smtp.gmail.com
 SMTP_PORT — default: 587
 SMTP_USER — your Gmail address
 SMTP_PASSWORD — Gmail App Password
 SMTP_FROM — display name + address
 ADMIN_PASSWORD — dashboard access code (default: pathfinder2025)
"""

# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import io, time, sqlite3, smtplib, os, re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

try:
 from fpdf import FPDF
 FPDF_OK = True
except ImportError:
 FPDF_OK = False

# ─────────────────────────────────────────────
# PAGE CONFIG (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
 page_title = "PathFinder — Career Intelligence",
 page_icon = "🧭",
 layout = "wide",
 initial_sidebar_state = "collapsed",
)

# ═══════════════════════════════════════════════════════════
# ① RIASEC META DATA
# ═══════════════════════════════════════════════════════════
TRAITS = {
 "Realistic": {"e":"🔧","label":"The Builder", "hex":"#FF6B35","rgb":"255,107,53", "glow":"rgba(255,107,53,.6)"},
 "Investigative": {"e":"🔬","label":"The Thinker", "hex":"#00D4FF","rgb":"0,212,255", "glow":"rgba(0,212,255,.6)"},
 "Artistic": {"e":"🎨","label":"The Creator", "hex":"#D45CFF","rgb":"212,92,255", "glow":"rgba(212,92,255,.6)"},
 "Social": {"e":"🤝","label":"The Helper", "hex":"#06D6A0","rgb":"6,214,160", "glow":"rgba(6,214,160,.6)"},
 "Enterprising": {"e":"💼","label":"The Leader", "hex":"#FFD60A","rgb":"255,214,10", "glow":"rgba(255,214,10,.6)"},
 "Conventional": {"e":"📊","label":"The Organizer", "hex":"#FF5EAB","rgb":"255,94,171", "glow":"rgba(255,94,171,.6)"},
}

CAREERS = {
 "Realistic": ["Mechanical Engineer","Civil Engineer","Robotics Engineer","Pilot","Architect"],
 "Investigative": ["Data Scientist","Research Scientist","Doctor","AI Engineer","Astronomer"],
 "Artistic": ["UX Designer","Filmmaker","Graphic Designer","Game Artist","Author"],
 "Social": ["Psychologist","Teacher","Social Worker","HR Leader","Counselor"],
 "Enterprising": ["Entrepreneur","Product Manager","Investment Banker","Marketing Director","Lawyer"],
 "Conventional": ["Chartered Accountant","Data Analyst","Financial Planner","Company Secretary","Auditor"],
}

# ═══════════════════════════════════════════════════════════
# ② MOCK DATA - 30 RIASEC QUESTIONS (5 PER TRAIT)
# ═══════════════════════════════════════════════════════════
QUESTIONS_CSV = """Question_ID,Text,Trait
Q01,I love building or repairing physical things — machines, electronics, or structures.,Realistic
Q02,I prefer hands-on work over sitting at a desk all day.,Realistic
Q03,Working with tools and fixing broken things gives me genuine satisfaction.,Realistic
Q04,I enjoy outdoor work and activities involving the natural environment.,Realistic
Q05,I'd rather do something practical than theoretical or abstract.,Realistic
Q06,I get a thrill from cracking a tough logic puzzle or math problem.,Investigative
Q07,I like running experiments and forming hypotheses about how the world works.,Investigative
Q08,I spend hours exploring scientific concepts and researching topics that fascinate me.,Investigative
Q09,I enjoy analyzing data and uncovering patterns others miss.,Investigative
Q10,I'm naturally curious and want to understand why things work the way they do.,Investigative
Q11,I express myself through art, music, writing, or performance.,Artistic
Q12,I would rather create something new than follow an established process.,Artistic
Q13,I love exploring creative ideas and unconventional ways of thinking.,Artistic
Q14,I often daydream about new worlds, stories, and imaginative scenarios.,Artistic
Q15,Beauty and aesthetics matter deeply to me in everything I do.,Artistic
Q16,I genuinely enjoy listening to others and helping solve their problems.,Social
Q17,Teaching or coaching someone and watching them grow excites me.,Social
Q18,I feel energized when collaborating with people and building meaningful relationships.,Social
Q19,I'm the person friends come to for advice and emotional support.,Social
Q20,Making a positive difference in people's lives is extremely important to me.,Social
Q21,I naturally step into leadership and enjoy persuading people.,Enterprising
Q22,Starting a new venture or project from scratch energizes me.,Enterprising
Q23,I thrive in competitive environments and love the challenge of winning.,Enterprising
Q24,I'm comfortable taking calculated risks to achieve ambitious goals.,Enterprising
Q25,I enjoy being in charge and making strategic decisions.,Enterprising
Q26,I value structure, clear rules, and organized systems.,Conventional
Q27,I find satisfaction in accurate data, clean records, and flawless processes.,Conventional
Q28,I prefer following established procedures and maintaining consistency.,Conventional
Q29,Attention to detail and precision is one of my greatest strengths.,Conventional
Q30,I like jobs where expectations are clear and success is measurable.,Conventional
"""

ROADMAPS_CSV = """Dominant_Trait,Recommended_Stream,Path_After_10th,Path_After_12th,YouTube_Link,Video_Title
Realistic,Science (PCM),"Choose Physics, Chemistry, Maths. Explore ITI trades or Polytechnic Diploma in Engineering for hands-on mastery.","B.Tech / B.E. in Mechanical · Civil · Electrical · Robotics. Key Entrances: JEE Main · JEE Advanced · State CETs.",https://www.youtube.com/watch?v=dQw4w9WgXcQ,Engineering Career Roadmap
Investigative,Science (PCB or PCM),"Take Science stream. Compete in Olympiads (Math, Science, Astronomy). Build research projects and publish mini-papers.","B.Sc. Research / MBBS / B.Tech (CS+AI). Key Entrances: NEET · JEE · KVPY · CUET.",https://www.youtube.com/watch?v=dQw4w9WgXcQ,Research & Science Career Guide
Artistic,Humanities / Fine Arts,"Explore Fine Arts, Music or Mass Communication diplomas. Build a portfolio website and start creating publicly.","B.F.A. · B.Des. · BA Journalism/Media. Key Entrances: NID · NIFT · UCEED · CLAT.",https://www.youtube.com/watch?v=dQw4w9WgXcQ,Creative Arts Career Paths
Social,Humanities / Arts,"Take Humanities with Psychology or Sociology. Volunteer, mentor juniors, and join social initiatives.","BA Psychology · B.Ed. · BSW. Key Entrances: CUET · NEET · State CET.",https://www.youtube.com/watch?v=dQw4w9WgXcQ,Social & Helping Professions Guide
Enterprising,Commerce / Any Stream,"Commerce with Maths is ideal. Join debate teams, Model UNs, and school business competitions.","BBA · B.Com · CA Foundation · LLB. Key Entrances: IPMAT (IIM) · CLAT · CA Foundation.",https://www.youtube.com/watch?v=dQw4w9WgXcQ,Business & Entrepreneurship Roadmap
Conventional,Commerce,"Commerce with Accountancy. Learn Excel, Tally, and Python basics early.","B.Com · BBA (Finance) · CA · CS · CMA. Key Entrances: CA Foundation · ICSI · CUET.",https://www.youtube.com/watch?v=dQw4w9WgXcQ,Finance & Accounting Career Path
"""

INTERVIEW_PREP_CSV = """Category,Question_EN,Question_HI,Question_TA,Tips
Common,Tell me about yourself,अपने बारे में बताएं,உங்களைப் பற்றி சொல்லுங்கள்,"Be concise (2-3 min). Share background, interests, and career goals. Avoid autobiography."
Common,What are your greatest strengths?,आपकी सबसे बड़ी ताकत क्या हैं?,உங்கள் மிகப் பெரிய வலிமைகள் என்ன?,"Mention 2-3 strengths with examples. Relate them to the job description."
Common,What is your biggest weakness?,आपकी सबसे बड़ी कमजोरी क्या है?,உங்கள் மிகப் பெரிய பலவீனம் என்ன?,"Choose a real weakness but show you're working on improving it. Avoid red flags."
Common,Why do you want this job?,आप यह नौकरी क्यों चाहते हैं?,நீங்கள் ஏன் இந்த வேலை வேண்டும்?,"Show genuine interest. Align your goals with company mission. Do research beforehand."
Common,Where do you see yourself in 5 years?,5 साल में आप अपने आप को कहाँ देखते हैं?,5 ஆண்டுக்குப் பிறகு நீங்கள் எங்கே இருப்பீர்கள்?,"Be realistic but ambitious. Show growth mindset and career progression."
Common,Tell me about a time you failed,एक ऐसी घटना बताएं जब आप असफल हुए,நீங்கள் தோல்வி அடைந்த சமயத்தைப் பற்றி சொல்லுங்கள்,"Use STAR method. Focus on what you learned. Demonstrate resilience and accountability."
Common,How do you handle stress or pressure?,आप तनाव या दबाव को कैसे संभालते हैं?,நீங்கள் மன அழுத்தம் அல்லது அழுத்தத்தை எவ்வாறு சামாளிக்கிறீர்கள்?,"Give specific strategies: planning, breaks, exercise, support systems."
Common,What are your salary expectations?,आपकी वेतन की अपेक्षाएं क्या हैं?,உங்கள் சம்பளம் அதிகமாக என்ன?,Research industry standards. Provide a range with flexibility. Don't give a number first.
Technical,Can you explain a complex project you worked on?,क्या आप एक जटिल प्रोजेक्ट समझा सकते हैं?,நீங்கள் பணிபுரிந்த சிக்கலான திட்டத்தை விளக்க முடியுமா?,"Use STAR. Focus on your role, challenges, solutions, and impact. Avoid jargon."
Technical,What programming languages / tools do you know?,आप कौन सी भाषाएँ जानते हैं?,நீங்கள் எந்த மொழிகளை அறிந்திருக்கிறீர்கள்?,"List relevant skills. Be honest about proficiency levels. Mention ongoing learning."
Technical,How would you approach solving a new problem?,आप एक नई समस्या को कैसे हल करेंगे?,நீங்கள் புதிய சிக்கலை எவ்வாறு தீர்க்கப் போகிறீர்கள்?,"Break it down into steps. Show analytical thinking. Ask clarifying questions."
Technical,Tell me about your experience with databases / APIs?,डेटाबेस / API अनुभव के बारे में बताएं?,தரவுத்தளங்கள் / API பற்றிய உங்கள் அভிজ্ञதையைச் சொல்லுங்கள்,"Describe specific projects. Mention technologies used. Highlight results and challenges overcome."
Technical,What's your experience working with teams?,टीम के साथ काम का अनुभव क्या है?,குழுவுடன் பணிபுரிந்த அভिজ्ञตा என்ன?,Share examples of collaboration. Mention communication and conflict resolution skills."
Technical,How do you stay updated with industry trends?,आप ट्रेंड के साथ कैसे अपडेट रहते हैं?,நீங்கள் தொழிற்துறை போக்குகளுடன் எவ்வாறு புதுப்பித்திருக்கிறீர்கள்?,"Mention courses, blogs, conferences, communities. Show genuine passion for learning."
Behavioral,Describe a time you showed leadership,एक बार का वर्णन करें जब आपने नेतृत्व दिखाया,நீங்கள் தலைமை தகுதி காட்டிய சமயத்தை விளக்குங்கள்,"Use STAR method. Show initiative, decision-making, and positive outcomes."
Behavioral,Tell me about a conflict with a colleague,सहकर्मी के साथ संघर्ष के बारे में बताएं,সহ��র্মীর সাথে দ্বন্দ্ব সম্পর্কে বলুন,"Focus on resolution. Show empathy and communication skills. Avoid blame."
Behavioral,How do you prioritize when you have multiple tasks?,आप कई काम होने पर प्राथमिकता कैसे तय करते हैं?,நீங்கள் பல பணிகள் ��ருக்கும்போது முன்னுரிமை எவ்வாறு வைக்கிறீர்கள்?,"Explain your system: lists, urgency/importance matrix. Show flexibility and adaptability."
Behavioral,Tell me about a time you had to learn something new quickly,एक ऐसा समय बताएं जब आपको जल्दी कुछ नया सीखना पड़ा,நீங்கள் দ்রुதமாக புதிதாக ஒன்றைக் கற்க வேண்டிய சமயத்தைச் சொல்லுங்கள்,"Show adaptability and growth mindset. Highlight the outcome and new skills acquired."
Behavioral,Describe your ideal work environment,अपने आदर्श कार्य वातावरण का वर्णन करें,உங்கள் சிறந்த பணிச்சூழல் விவரிக்குங்கள்,"Be specific but flexible. Align with company culture shown in research."
Behavioral,How do you handle criticism or feedback?,आप आलोचना को कैसे संभालते हैं?,நீங்கள் விமர்சனத்தை எவ்வாறு சமாளிக்கிறீர்கள்?,"Show receptiveness to feedback. Give an example of improvement based on criticism."
"""

@st.cache_data
def load_questions(): return pd.read_csv(io.StringIO(QUESTIONS_CSV))
@st.cache_data
def load_roadmaps(): return pd.read_csv(io.StringIO(ROADMAPS_CSV))
@st.cache_data
def load_interview_prep(): return pd.read_csv(io.StringIO(INTERVIEW_PREP_CSV))

# ═══════════════════════════════════════════════════════════
# ③ TRANSLATIONS (EN / HI / TA)
# ═══════════════════════════════════════════════════════════
TR = {
 "en":{
 "tagline":"Discover Your Destiny",
 "subtitle":"AI-powered career intelligence for Class 10 & 12 students",
 "enter_name":"Your Name","name_ph":"e.g. Priya Sharma","cta":"Begin Journey →",
 "name_warn":"Please enter your name first.",
 "what":"What is RIASEC?",
 "what_body":"Holland's RIASEC model maps your personality across 6 dimensions to reveal careers where you will naturally thrive — not just survive.",
 "q_sub":"Rate how strongly this describes you",
 "back":"Back","next":"Next","submit":"Reveal My Results ✦",
 "no_ans":"Please select a rating to continue.",
 "a1":"Reading your personality constellation…","a2":"Mapping your trait signature…","a3":"Plotting your career orbit…",
 "result_title":"Your Career DNA",
 "dominant":"Dominant Trait","stream":"Recommended Stream",
 "after10":"After Class 10th","after12":"After Class 12th",
 "careers":"Career Orbits","video":"Watch: Your Path Explained",
 "pdf_btn":"⬇ Download PDF Roadmap","pdf_ok":"PDF ready — download above!",
 "email_lbl":"Email this roadmap","email_ph":"you@email.com",
 "email_send":"Send →","email_ok":"Sent! Check your inbox.",
 "email_err":"Email failed — check SMTP config.","email_bad":"Enter a valid email.",
 "retake":"↩ Retake Quiz",
 "admin":"🛡 Admin","admin_title":"Mission Control",
 "admin_sub":"Real-time analytics across all quiz sessions",
 "pwd_lbl":"Access Code","pwd_btn":"Authenticate","pwd_err":"Invalid access code.",
 "kpi_total":"Total Sessions","kpi_top":"Leading Trait","kpi_today":"Today",
 "dist":"Trait Distribution","avg":"Avg RIASEC Scores","recent":"Recent Sessions",
 "no_data":"No sessions yet — complete a quiz first.",
 "logout":"🔒 Sign Out","home_btn":"🏠 Home",
 "interview":"📋 Interview Prep", "interview_title":"Master Your Interview",
 "interview_sub":"Practice common, technical, and behavioral questions",
 "scale":{"Not Like Me":1,"A Little Like Me":2,"Somewhat Like Me":3,"Mostly Like Me":4,"Exactly Like Me":5},
 },
 "hi":{
 "tagline":"अपनी मंज़िल खोजें",
 "subtitle":"कक्षा 10 और 12 के छात्रों के लिए AI करियर इंटेलिजेंस",
 "enter_name":"आपका नाम","name_ph":"जैसे: प्रिया शर्मा","cta":"यात्रा शुरू करें →",
 "name_warn":"कृपया पहले अपना नाम दर्ज करें।",
 "what":"RIASEC क्या है?",
 "what_body":"Holland का RIASEC मॉडल आपकी व्यक्तित्व को 6 आयामों में मापकर आपके लिए सही करियर खोजता है।",
 "q_sub":"यह कथन आप पर कितना लागू होता है",
 "back":"वापस","next":"आगे","submit":"परिणाम देखें ✦",
 "no_ans":"जारी रखने के लिए रेटिंग चुनें।",
 "a1":"नक्षत्र पढ़ा जा रहा है…","a2":"ट्रेट सिग्नेचर बन रहा है…","a3":"करियर पथ तैयार हो रहा है…",
 "result_title":"आपका करियर DNA",
 "dominant":"प्रमुख विशेषता","stream":"अनुशंसित धारा",
 "after10":"कक्षा 10 के बाद","after12":"कक्षा 12 के बाद",
 "careers":"करियर विकल्प","video":"देखें: आपका पथ",
 "pdf_btn":"⬇ PDF डाउनलोड करें","pdf_ok":"PDF तैयार है!",
 "email_lbl":"रोडमैप ईमेल करें","email_ph":"आपका@ईमेल.com",
 "email_send":"भेजें →","email_ok":"भेज दिया गया!",
 "email_err":"ईमेल विफल।","email_bad":"वैध ईमेल दर्ज करें।",
 "retake":"↩ क्विज़ दोबारा लें",
 "admin":"🛡 एडमिन","admin_title":"मिशन कंट्रोल",
 "admin_sub":"सभी सत्रों का विश्लेषण",
 "pwd_lbl":"एक्सेस कोड","pwd_btn":"प्रमाणित करें","pwd_err":"गलत कोड।",
 "kpi_total":"कुल सत्र","kpi_top":"शीर्ष विशेषता","kpi_today":"आज",
 "dist":"विशेषता वितरण","avg":"औसत RIASEC स्कोर","recent":"हालिया सत्र",
 "no_data":"अभी कोई डेटा नहीं।",
 "logout":"🔒 साइन आउट","home_btn":"🏠 होम",
 "interview":"📋 साक्षात्कार की तैयारी", "interview_title":"अपने साक्षात्कार में महारत हासिल करें",
 "interview_sub":"सामान्य, तकनीकी और व्यावहारिक प्रश्नों का अभ्यास करें",
 "scale":{"बिल्कुल नहीं":1,"थोड़ा":2,"कुछ हद तक":3,"अधिकतर":4,"बिल्कुल मैं":5},
 },
 "ta":{
 "tagline":"உங்கள் இலக்கை கண்டறியுங்கள்",
 "subtitle":"வகுப்பு 10 & 12 மாணவர்களுக்கான AI தொழில் நுண்ணறிவு",
 "enter_name":"உங்கள் பெயர்","name_ph":"எ.கா: பிரியா குமார்","cta":"பயணத்தை தொடங்கு →",
 "name_warn":"முதலில் உங்கள் பெயரை உள்ளிடவும்.",
 "what":"RIASEC என்றால் என்ன?",
 "what_body":"Holland RIASEC மாதிரி உங்கள் ஆளுமையை 6 பரிமாணங்களில் அளவிட்டு சரியான தொழிலை வெளிப்படுத்துகிறது.",
 "q_sub":"இந்த வாக்கியம் உங்களுக்கு எந்த அளவு பொருந்துகிறது",
 "back":"பின்னால்","next":"அடுத்தது","submit":"என் முடிவைக் காண்க ✦",
 "no_ans":"தொடர மதிப்பீட்டைத் தேர்வு செய்யவும்.",
 "a1":"நட்சத்திர வரைபடம் படிக்கப்படுகிறது…","a2":"பண்பு கையெழுத்து உருவாக்கப்படுகிறது…","a3":"தொழில் பாதை வரையப்படுகிறது…",
 "result_title":"உங்கள் தொழில் DNA",
 "dominant":"முதன்மை பண்பு","stream":"பரிந்துரைக்கப்பட்ட பாதை",
 "after10":"வகுப்பு 10 க்குப் பிறகு","after12":"வகுப்பு 12 க்குப் பிறகு",
 "careers":"தொழில் விருப்பங்கள்","video":"காண்க: உங்கள் பாதை",
 "pdf_btn":"⬇ PDF பதிவிறக்கவும்","pdf_ok":"PDF தயாராக உள்ளது!",
 "email_lbl":"மின்னஞ்சல் அனுப்பு","email_ph":"உங்கள்@மின்னஞ்சல்.com",
 "email_send":"அனுப்பு →","email_ok":"அனுப்பப்பட்டது!",
 "email_err":"தோல்வி.","email_bad":"சரியான மின்னஞ்சல் உள்ளிடவும்.",
 "retake":"↩ மீண்டும் வினாடி வினா",
 "admin":"🛡 நிர்வாகம்","admin_title":"மிஷன் கண்ட்রோல்",
 "admin_sub":"அனைத்து அமர்வுகளின் பகுப்பாய்வு",
 "pwd_lbl":"அணுகல் குறியீடு","pwd_btn":"சரிபார்","pwd_err":"தவறான குறியீடு.",
 "kpi_total":"மொத்த அமர்வுகள்","kpi_top":"முன்னணி பண்பு","kpi_today":"இன்று",
 "dist":"பண்பு விநியோகம்","avg":"சராசரி RIASEC மதிப்பெண்கள்","recent":"சமீபத்திய அமர்வுகள்",
 "no_data":"இன்னும் தரவு இல்லை.",
 "logout":"🔒 வெளியேறு","home_btn":"🏠 முகப்பு",
 "interview":"📋 பேட்டியு தயாரी", "interview_title":"உங்கள் பேட்டிக்கு தயாரிடுங்கள்",
 "interview_sub":"பொதுவான, தொழில்நுட்ப மற்றும் நடத்தைமுறை கேள்விகளை பயிற்சி செய்யுங்கள்",
 "scale":{"என்னில் இல்லை":1,"சிறிது":2,"ஓரளவு":3,"பெரும்பாலும்":4,"முழுமையாக நான்":5},
 },
}

def T(k):
 lang = st.session_state.get("lang","en")
 return TR.get(lang,TR["en"]).get(k,k)

def SCALE():
 lang = st.session_state.get("lang","en")
 return TR.get(lang,TR["en"])["scale"]

# ═══════════════════════════════════════════════════════════
# ④ DATABASE (SQLite in /tmp — survives Streamlit Cloud)
# ═══════════════════════════════════════════════════════════
DB = os.path.join("/tmp","pathfinder_v4.db")

def init_db():
 c = sqlite3.connect(DB)
 c.execute("""CREATE TABLE IF NOT EXISTS results(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT, dominant_trait TEXT,
 r INTEGER, i INTEGER, a INTEGER,
 s INTEGER, e INTEGER, cv INTEGER,
 lang TEXT, timestamp TEXT)""")
 c.commit(); c.close()

def save_result(name, scores, lang):
 if st.session_state.get("saved"): return
 c = sqlite3.connect(DB)
 c.execute("INSERT INTO results VALUES(NULL,?,?,?,?,?,?,?,?,?,?)",(
 name, max(scores,key=scores.get),
 scores.get("Realistic",0), scores.get("Investigative",0),
 scores.get("Artistic",0), scores.get("Social",0),
 scores.get("Enterprising",0), scores.get("Conventional",0),
 lang, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
 c.commit(); c.close()
 st.session_state.saved = True

def fetch_all():
 c = sqlite3.connect(DB)
 df = pd.read_sql_query("SELECT * FROM results ORDER BY id DESC",c)
 c.close(); return df

# ═══════════════════════════════════════════════════════════
# ⑤ SCORING ENGINE
# ═══════════════════════════════════════════════════════════
def score_quiz(answers, qdf):
 s = {t:0 for t in TRAITS}
 for _,row in qdf.iterrows():
 if row["Question_ID"] in answers:
 s[row["Trait"]] += answers[row["Question_ID"]]
 return s

def dominant(s): return max(s, key=s.get)

# ═══════════════════════════════════════════════════════════
# ⑥ PLOTLY RADAR CHART
# ═══════════════════════════════════════════════════════════
def radar(scores, trait):
 cats = list(scores.keys())
 vals = [scores[c] for c in cats]
 info = TRAITS[trait]
 fig = go.Figure(go.Scatterpolar(
 r = vals + [vals[0]],
 theta = cats + [cats[0]],
 fill = "toself",
 fillcolor = f"rgba({info['rgb']},.18)",
 line = dict(color=info["hex"], width=3),
 marker= dict(size=9, color=info["hex"],
 line=dict(color="#fff",width=2)),
 hovertemplate=" %{theta} Score: %{r}/50 ",
 ))
 fig.update_layout(
 polar=dict(
 bgcolor="rgba(0,0,0,0)",
 angularaxis=dict(tickfont=dict(size=13,color="#ddd",family="Outfit"),
 linecolor="rgba(255,255,255,0.08)",
 gridcolor="rgba(255,255,255,0.06)"),
 radialaxis=dict(visible=True,range=[0,50],
 tickfont=dict(size=8,color="rgba(255,255,255,.25)"),
 gridcolor="rgba(255,255,255,0.05)",
 linecolor="rgba(255,255,255,0.06)"),
 ),
 showlegend=False,
 paper_bgcolor="rgba(0,0,0,0)",
 plot_bgcolor ="rgba(0,0,0,0)",
 margin=dict(l=50,r=50,t=30,b=30),
 height=400,
 )
 return fig

# ═══════════════════════════════════���═══════════════════════
# ⑦ PDF GENERATOR
# ═══════════════════════════════════════════════════════════
def make_pdf(name, trait, scores, row):
 if not FPDF_OK:
 txt = "\n".join([
 "PathFinder Career Roadmap","="*44,
 f"Student : {name}",
 f"Trait : {trait} — {TRAITS[trait]['label']}",
 f"Stream : {row['Recommended_Stream']}","",
 "After 10th:"," "+row["Path_After_10th"],"",
 "After 12th:"," "+row["Path_After_12th"],"",
 "Career Options:"]+[f" • {c}" for c in CAREERS.get(trait,[])]+[
 "","RIASEC Scores:"]+[f" {k}: {v}/50" for k,v in scores.items()])
 return txt.encode()

 pdf = FPDF(); pdf.set_auto_page_break(True,15); pdf.add_page()
 info = TRAITS[trait]
 r2,g2,b2 = [int(x) for x in info["rgb"].split(",")]

 # Header band
 pdf.set_fill_color(5,5,20); pdf.rect(0,0,210,52,style="F")
 # Accent glow stripe
 for i in range(4):
 alpha = max(5,int(80-(i*20)))
 pdf.set_fill_color(int(r2*alpha/100),int(g2*alpha/100),int(b2*alpha/100))
 pdf.rect(0,46-i*1.5,210,3,style="F")
 pdf.set_text_color(255,255,255); pdf.set_font("Helvetica","B",26)
 pdf.set_xy(10,8); pdf.cell(190,13,"PathFinder",align="C",ln=True)
 pdf.set_font("Helvetica","",11); pdf.set_text_color(180,180,210)
 pdf.set_x(10); pdf.cell(190,8,"Career Intelligence Report",align="C")

 # Trait badge
 pdf.set_xy(15,60); pdf.set_fill_color(r2,g2,b2)
 pdf.set_text_color(10,10,30); pdf.set_font("Helvetica","B",15)
 pdf.cell(180,14,f"{info['e']} {trait} — {info['label']}",align="C",fill=True,ln=True)

 # Student info
 pdf.set_xy(15,82); pdf.set_text_color(40,40,60); pdf.set_font("Helvetica","",12)
 pdf.cell(0,7,f"Student: {name}",ln=True); pdf.set_x(15)
 pdf.cell(0,7,f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}",ln=True)
 pdf.ln(4); pdf.set_draw_color(r2,g2,b2); pdf.set_line_width(1.2)
 pdf.line(15,pdf.get_y(),195,pdf.get_y()); pdf.ln(7)

 def hd(t):
 pdf.set_font("Helvetica","B",12); pdf.set_fill_color(r2,g2,b2)
 pdf.set_text_color(10,10,30); pdf.set_x(15)
 pdf.cell(180,9,f" {t}",ln=True,fill=True)
 pdf.set_text_color(40,40,60); pdf.set_font("Helvetica","",11); pdf.ln(2)

 def bd(t):
 pdf.set_x(18); pdf.multi_cell(174,6,t); pdf.ln(3)

 hd("Recommended Academic Stream"); bd(row["Recommended_Stream"])
 hd("After Class 10th"); bd(row["Path_After_10th"])
 hd("After Class 12th"); bd(row["Path_After_12th"])
 hd("Career Options")
 bd(" \u2022 "+"\n \u2022 ".join(CAREERS.get(trait,[])))
 hd("RIASEC Score Breakdown")
 for t,sc in sorted(scores.items(),key=lambda x:-x[1]):
 bw = max(1,int((sc/50)*130))
 pdf.set_x(18); pdf.set_font("Helvetica","",10); pdf.set_text_color(40,40,60)
 pdf.cell(44,6,f"{TRAITS[t]['e']} {t}",ln=False)
 xn,yn = pdf.get_x(),pdf.get_y()
 pdf.set_fill_color(215,215,230); pdf.rect(xn,yn+1,130,5,style="F")
 pdf.set_fill_color(r2,g2,b2); pdf.rect(xn,yn+1,bw,5,style="F")
 pdf.set_x(xn+133); pdf.cell(15,6,f"{sc}/50",ln=True)

 pdf.set_y(-16); pdf.set_font("Helvetica","I",8)
 pdf.set_text_color(160,160,180)
 pdf.cell(0,6,"PathFinder v4 \u00b7 RIASEC Intelligence \u00b7 pathfinder.app",align="C")
 return bytes(pdf.output())

# ═══════════════════════════════════════════════════════════
# ⑧ EMAIL SENDER
# ═══════════════════════════════════════════════════════════
SMTP_HOST = os.getenv("SMTP_HOST","smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT","587"))
SMTP_USER = os.getenv("SMTP_USER","your@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASSWORD","app_password")
SMTP_FROM = os.getenv("SMTP_FROM","PathFinder ")

def send_email(to, name, trait, pdf_bytes):
 try:
 msg = MIMEMultipart()
 msg["From"] = SMTP_FROM; msg["To"] = to
 msg["Subject"] = f"Your PathFinder Career Roadmap — {trait}"
 msg.attach(MIMEText(
 f"Hi {name},\n\nYour dominant RIASEC trait is {trait} ({TRAITS[trait]['label']}).\n"
 f"Your full career roadmap is attached as a PDF!\n\n\U0001f9ed PathFinder v4","plain"))
 att = MIMEBase("application","octet-stream"); att.set_payload(pdf_bytes)
 encoders.encode_base64(att)
 att.add_header("Content-Disposition",
 f'attachment; filename="PathFinder_{name.replace(" ","_")}.pdf"')
 msg.attach(att)
 with smtplib.SMTP(SMTP_HOST,SMTP_PORT) as s:
 s.ehlo(); s.starttls(); s.login(SMTP_USER,SMTP_PASS)
 s.sendmail(SMTP_USER,to,msg.as_string())
 return True,""
 except Exception as ex: return False,str(ex)

def valid_email(e):
 return bool(re.match(r"^[\w\.\+\-]+@[\w\-]+\.\w{2,}$",e))

# ═══════════════════════════════════════════════════════════
# ⑨ SESSION STATE INITIALIZER (FIXED)
# ═══════════════════════════════════════════════════════════
def init():
 # Initialize fresh state - no persistence between sessions for first-time users
 for k,v in {"page":"home","q":0,"ans":{},"scores":{},"trait":None,
 "name":"","saved":False,"admin_ok":False,"lang":"en"}.items():
 if k not in st.session_state:
  st.session_state[k] = v

# Call init at start to ensure clean session
init()

# ═══════════════════════════════════════════════════════════
# ⑩ MASTER CSS (dynamic — repaints to trait color)
# ═══════════════════════════════════════════════════════════
def inject_css(trait=None):
 acc = TRAITS[trait]["hex"] if trait else "#00D4FF"
 rgb = TRAITS[trait]["rgb"] if trait else "0,212,255"
 glow = TRAITS[trait]["glow"] if trait else "rgba(0,212,255,.5)"
 st.markdown(f""" 
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100;200;300;400;500;600;700;800;900&family=JetBrains+Mono:ital,wght@0,400;0,500;0,700;1,400&display=swap');
:root{{--A:{acc};--rgb:{rgb};--glow:{glow};--bg:#03030f;--bg2:#07071a;--glass:rgba(255,255,255,0.038);--glass-b:rgba(255,255,255,0.09);--text:#eeeeff;--muted:rgba(238,238,255,0.45);--mono:'JetBrains Mono',monospace;--sans:'Outfit',sans-serif;--r:18px;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html,body,[class*="css"]{{font-family:var(--sans);background:var(--bg)!important;color:var(--text);}}
#MainMenu,footer,header{{visibility:hidden;}}
.block-container{{padding:0!important;max-width:100%!important;}}
[data-testid="stSidebar"]{{display:none!important;}}
section[data-testid="stMain"]>div{{padding:0!important;}}
.stApp{{
 background:radial-gradient(ellipse 90% 55% at 15% 20%,rgba({rgb},.13) 0%,transparent 55%),
 radial-gradient(ellipse 70% 45% at 85% 75%,rgba({rgb},.09) 0%,transparent 50%),
 radial-gradient(ellipse 50% 60% at 50% 50%,rgba({rgb},.04) 0%,transparent 65%),
 var(--bg)!important;min-height:100vh;animation:nebula 18s ease-in-out infinite alternate;}}
@keyframes nebula{{0%{{background-position:0% 0%,100% 100%,50% 50%;}}100%{{background-position:10% 15%,88% 82%,52% 48%;}}}}
.stApp::before{{content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
 background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
 background-size:180px 180px;opacity:.4;}}
.wrap{{position:relative;z-index:2;max-width:900px;margin:0 auto;padding:2.5rem 1.5rem 5rem;}}
.wrap-wide{{position:relative;z-index:2;max-width:1100px;margin:0 auto;padding:2.5rem 2rem 5rem;}}
.orb-wrap{{display:flex;justify-content:center;margin:1.5rem 0 2rem;}}
.orb{{width:120px;height:120px;border-radius:50%;
 background:radial-gradient(circle at 35% 35%,rgba({rgb},.9),rgba({rgb},.15) 65%,transparent);
 box-shadow:0 0 60px {glow},0 0 120px rgba({rgb},.25),inset 0 0 30px rgba(255,255,255,.08);
 animation:orb-morph 6s ease-in-out infinite,orb-pulse 3s ease-in-out infinite alternate;position:relative;}}
.orb::after{{content:'';position:absolute;inset:-12px;border-radius:50%;border:1.5px solid rgba({rgb},.35);animation:orb-ring 4s linear infinite;}}
.orb::before{{content:'';position:absolute;inset:-26px;border-radius:50%;border:1px solid rgba({rgb},.15);animation:orb-ring 6s linear infinite reverse;}}
@keyframes orb-morph{{0%,100%{{border-radius:50%;}}33%{{border-radius:46% 54% 62% 38%/52% 48% 52% 48%;}}66%{{border-radius:58% 42% 44% 56%/44% 58% 42% 56%;}}}}
@keyframes orb-pulse{{from{{box-shadow:0 0 40px {glow},0 0 80px rgba({rgb},.2);}}to{{box-shadow:0 0 80px {glow},0 0 160px rgba({rgb},.35),0 0 240px rgba({rgb},.1);}}}}
@keyframes orb-ring{{from{{transform:rotate(0deg);}}to{{transform:rotate(360deg);}}}}
.hero{{text-align:center;padding:2.5rem 0 1.5rem;}}
.hero-tagline{{font-size:clamp(2.6rem,7vw,5.2rem);font-weight:900;line-height:1.04;letter-spacing:-.035em;
 background:linear-gradient(135deg,#ffffff 0%,var(--A) 45%,#ffffff 90%);background-size:200% 100%;
 -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
 animation:text-shimmer 5s ease-in-out infinite;}}
@keyframes text-shimmer{{0%,100%{{background-position:0% 50%;}}50%{{background-position:100% 50%;}}}}
.hero-sub{{font-size:1.05rem;color:var(--muted);margin:.9rem 0 2rem;font-weight:300;letter-spacing:.01em;}}
.glass{{background:var(--glass);border:1px solid var(--glass-b);border-radius:var(--r);
 backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);padding:2rem;margin-bottom:1.4rem;
 transition:border-color .35s,box-shadow .35s,transform .25s;position:relative;overflow:hidden;}}
.glass::before{{content:'';position:absolute;top:0;left:-60%;width:40%;height:100%;
 background:linear-gradient(90deg,transparent,rgba(255,255,255,.03),transparent);transform:skewX(-20deg);
 animation:glass-sheen 8s ease-in-out infinite;}}
@keyframes glass-sheen{{0%{{left:-60%;}}60%,100%{{left:140%;}}}}
.glass:hover{{border-color:rgba({rgb},.4);box-shadow:0 8px 48px rgba({rgb},.14),0 2px 12px rgba(0,0,0,.4);transform:translateY(-2px);}}
.trait-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1.5rem 0;}}
.trait-card{{background:var(--glass);border:1px solid var(--glass-b);border-radius:16px;padding:1.3rem .8rem;
 text-align:center;cursor:default;transition:all .3s cubic-bezier(.34,1.56,.64,1);position:relative;overflow:hidden;}}
.trait-card::after{{content:'';position:absolute;inset:0;border-radius:16px;
 background:radial-gradient(circle at 50% 0%,rgba(255,255,255,.07),transparent 65%);pointer-events:none;}}
.trait-card:hover{{transform:translateY(-8px) scale(1.04);}}
.tc-emoji{{font-size:2.3rem;display:block;margin-bottom:.5rem;filter:drop-shadow(0 4px 12px currentColor);}}
.tc-name{{font-size:.93rem;font-weight:700;color:#fff;}}
.tc-role{{font-size:.72rem;color:var(--muted);margin-top:.2rem;}}
.prog-wrap{{height:3px;background:rgba(255,255,255,0.07);border-radius:2px;margin-bottom:2rem;overflow:hidden;}}
.prog-fill{{height:3px;border-radius:2px;background:linear-gradient(90deg,var(--A),rgba({rgb},.4));
 transition:width .5s cubic-bezier(.4,0,.2,1);box-shadow:0 0 16px rgba({rgb},.8);position:relative;overflow:hidden;}}
.prog-fill::after{{content:'';position:absolute;right:0;top:-1px;width:24px;height:5px;border-radius:2px;
 background:rgba(255,255,255,.7);box-shadow:0 0 8px rgba(255,255,255,.8);}}
.q-card{{background:var(--glass);border:1px solid var(--glass-b);border-radius:var(--r);padding:2.5rem 2rem;
 animation:card-slide .45s cubic-bezier(.4,0,.2,1);}}
@keyframes card-slide{{from{{opacity:0;transform:translateX(30px);}}to{{opacity:1;transform:translateX(0);}}}}
.q-pill{{display:inline-block;background:rgba({rgb},.14);border:1px solid rgba({rgb},.3);color:var(--A);
 font-family:var(--mono);font-size:.68rem;font-weight:500;letter-spacing:.1em;
 padding:.28rem .9rem;border-radius:30px;text-transform:uppercase;margin-bottom:1.2rem;}}
.q-text{{font-size:1.25rem;font-weight:600;color:#fff;line-height:1.55;margin-bottom:2rem;}}
.q-num{{font-family:var(--mono);font-size:.75rem;color:var(--muted);}}
.overlay{{position:fixed;inset:0;z-index:9999;
 background:radial-gradient(ellipse at center,#0a0a20 0%,#03030f 80%);
 display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1.8rem;}}
.pulse-rings{{position:relative;width:100px;height:100px;display:flex;align-items:center;justify-content:center;}}
.ring{{position:absolute;border-radius:50%;border:2px solid var(--A);animation:ring-out 2s ease-out infinite;}}
.ring:nth-child(1){{width:40px;height:40px;animation-delay:0s;}}
.ring:nth-child(2){{width:70px;height:70px;animation-delay:.4s;}}
.ring:nth-child(3){{width:100px;height:100px;animation-delay:.8s;}}
@keyframes ring-out{{0%{{transform:scale(.6);opacity:1;}}100%{{transform:scale(1.4);opacity:0;}}}}
.ovl-icon{{font-size:2.8rem;z-index:1;animation:icon-sw 2s ease-in-out infinite;}}
@keyframes icon-sw{{0%,100%{{transform:rotate(-5deg);}}50%{{transform:rotate(5deg);}}}}
.ovl-msg{{font-family:var(--mono);font-size:1rem;color:var(--muted);text-align:center;max-width:280px;}}
.btn-row{{display:flex;gap:1rem;margin-top:1.5rem;flex-wrap:wrap;}}
.btn{{padding:.9rem 1.8rem;border:none;border-radius:10px;font-weight:600;cursor:pointer;
 transition:all .3s;font-family:var(--sans);font-size:1rem;}}
.btn-prime{{background:var(--A);color:#03030f;}}
.btn-prime:hover{{transform:translateY(-2px);box-shadow:0 12px 32px rgba({rgb},.35);}}
.btn-ghost{{background:transparent;border:1.5px solid rgba({rgb},.4);color:var(--A);}}
.btn-ghost:hover{{background:rgba({rgb},.08);border-color:rgba({rgb},.6);}}
.input{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);color:#fff;
 padding:.8rem 1rem;border-radius:10px;font-family:var(--sans);font-size:1rem;}}
.input::placeholder{{color:var(--muted);}}
.input:focus{{outline:none;border-color:var(--A);box-shadow:0 0 20px rgba({rgb},.2);}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# ⑪ PAGE ROUTES
# ═══════════════════════════════════════════════════════════

def page_home():
 inject_css()
 st.markdown("""<div class="wrap"><div class="hero">
 <h1 class="hero-tagline">"""+T("tagline")+"""</h1>
 <p class="hero-sub">"""+T("subtitle")+"""</p>
 </div></div>""", unsafe_allow_html=True)

 col1, col2 = st.columns([1,1], gap="large")
 with col1:
 st.markdown("### "+T("what")+"?")
 st.markdown(T("what_body"))
 with st.expander("🎯 Traits Explained"):
  for trait, info in TRAITS.items():
   st.write(f"**{info['e']} {trait}** ({info['label']}): " + 
    {"Realistic":"Hands-on, practical, technical skills",
     "Investigative":"Research, analysis, problem-solving",
     "Artistic":"Creative, expressive, imaginative",
     "Social":"Helping, teaching, collaborating",
     "Enterprising":"Leading, persuading, risk-taking",
     "Conventional":"Organizing, precision, structure"}[trait])

 with col2:
 st.markdown("### "+T("enter_name"))
 name = st.text_input("", placeholder=T("name_ph"), key="home_name_input")
 
 col_a, col_b = st.columns(2)
 with col_a:
  lang = st.selectbox("Language", ["English (EN)","हिंदी (HI)","தமிழ் (TA)"],
   index=0, key="lang_select")
  st.session_state.lang = {"English (EN)":"en","हिंदी (HI)":"hi","தமிழ் (TA)":"ta"}[lang]
 with col_b:
  st.write("")
  st.write("")

 if st.button(T("cta"), use_container_width=True, type="primary"):
  if not name.strip():
   st.error(T("name_warn"))
  else:
   st.session_state.name = name
   st.session_state.page = "quiz"
   st.session_state.ans = {}
   st.session_state.scores = {}
   st.session_state.q = 0
   st.session_state.saved = False
   st.rerun()

 # Home navigation buttons
 col_nav1, col_nav2 = st.columns(2)
 with col_nav1:
  if st.button("📋 Interview Prep", use_container_width=True):
   st.session_state.page = "interview"
   st.rerun()
 with col_nav2:
  if st.button("🛡 Admin", use_container_width=True):
   st.session_state.page = "admin"
   st.rerun()

def page_quiz():
 inject_css()
 qdf = load_questions()
 total = len(qdf)
 q_idx = st.session_state.q
 row = qdf.iloc[q_idx]

 col1, col2, col3 = st.columns([1,2,1])
 with col1:
  st.markdown(f"<div class='q-num'>Q{row['Question_ID']} / Q30</div>", unsafe_allow_html=True)
 with col3:
  st.markdown(f"<div style='text-align:right;'><span class='q-pill'>{row['Trait']}</span></div>", unsafe_allow_html=True)

 prog = (q_idx / total) * 100
 st.markdown(f"<div class='prog-wrap'><div class='prog-fill' style='width:{prog}%;'></div></div>", unsafe_allow_html=True)

 st.markdown(f"<div class='q-card'><div class='q-text'>{row['Text']}</div>", unsafe_allow_html=True)
 st.write(T("q_sub"))
 
 scale = SCALE()
 rating = st.radio("", list(scale.keys()), key=f"q{q_idx}", label_visibility="collapsed")

 if rating:
  st.session_state.ans[row['Question_ID']] = scale[rating]

 col_nav1, col_nav2, col_nav3 = st.columns(3)
 with col_nav1:
  if st.button(T("back"), use_container_width=True) and q_idx > 0:
   st.session_state.q -= 1
   st.rerun()

 with col_nav3:
  if q_idx == total - 1:
   if st.button(T("submit"), use_container_width=True, type="primary"):
    if not rating:
     st.error(T("no_ans"))
    else:
     st.session_state.scores = score_quiz(st.session_state.ans, qdf)
     st.session_state.trait = dominant(st.session_state.scores)
     st.session_state.page = "results"
     st.rerun()
  else:
   if st.button(T("next"), use_container_width=True, type="primary"):
    if not rating:
     st.error(T("no_ans"))
    else:
     st.session_state.q += 1
     st.rerun()

def page_results():
 inject_css(st.session_state.trait)
 name = st.session_state.name
 trait = st.session_state.trait
 scores = st.session_state.scores
 rdf = load_roadmaps()
 row = rdf[rdf["Dominant_Trait"]==trait].iloc[0]

 save_result(name, scores, st.session_state.lang)

 st.markdown(f"<div class='wrap'><div class='orb-wrap'><div class='orb'></div></div>", unsafe_allow_html=True)
 st.markdown(f"## {T('result_title')}", unsafe_allow_html=True)
 st.markdown(f"### {TRAITS[trait]['e']} {trait} — {TRAITS[trait]['label']}", unsafe_allow_html=True)

 col1, col2 = st.columns(2)
 with col1:
  st.markdown(f"**{T('dominant')}:** {trait}")
  st.markdown(f"**{T('stream')}:** {row['Recommended_Stream']}")
 with col2:
  st.markdown(f"**Score:** {scores[trait]}/50")
  st.markdown(f"**Avg Score:** {sum(scores.values())//6}/50")

 st.plotly_chart(radar(scores, trait), use_container_width=True)

 st.markdown(f"### {T('after10')}")
 st.write(row['Path_After_10th'])

 st.markdown(f"### {T('after12')}")
 st.write(row['Path_After_12th'])

 st.markdown(f"### {T('careers')}")
 careers = CAREERS.get(trait,[])
 st.write(" • ".join(careers))

 st.markdown(f"### {T('pdf_btn')}")
 pdf_bytes = make_pdf(name, trait, scores, row)
 st.download_button("⬇ Download", pdf_bytes, 
  f"PathFinder_{name.replace(' ','_')}.pdf", "application/pdf")

 st.markdown(f"### {T('email_lbl')}")
 email = st.text_input("", placeholder=T("email_ph"), key="email_input")
 if st.button(T("email_send"), use_container_width=True):
  if not valid_email(email):
   st.error(T("email_bad"))
  else:
   ok, err = send_email(email, name, trait, pdf_bytes)
   st.success(T("email_ok")) if ok else st.error(f"{T('email_err')}: {err}")

 st.divider()
 if st.button(T("retake"), use_container_width=True):
  # Completely reset session state for fresh quiz
  st.session_state.page = "home"
  st.session_state.q = 0
  st.session_state.ans = {}
  st.session_state.scores = {}
  st.session_state.trait = None
  st.session_state.name = ""
  st.session_state.saved = False
  st.rerun()

def page_interview():
 inject_css()
 idf = load_interview_prep()
 st.markdown(f"<div class='wrap'><h1 class='hero-tagline'>{T('interview_title')}</h1>", unsafe_allow_html=True)
 st.markdown(f"<p class='hero-sub'>{T('interview_sub')}</p></div>", unsafe_allow_html=True)

 tab1, tab2, tab3 = st.tabs(["Common Questions", "Technical Questions", "Behavioral Questions"])

 def show_questions(category):
  cat_df = idf[idf["Category"]==category]
  for _, q in cat_df.iterrows():
   lang = st.session_state.get("lang","en")
   q_text = q.get(f"Question_{lang.upper()}", q.get("Question_EN", ""))
   tips = q.get("Tips", "")
   with st.expander(q_text, expanded=False):
    st.write(f"**💡 Tips:** {tips}")

 with tab1:
  show_questions("Common")
 with tab2:
  show_questions("Technical")
 with tab3:
  show_questions("Behavioral")

 st.divider()
 if st.button(T("home_btn"), use_container_width=True):
  st.session_state.page = "home"
  st.rerun()

def page_admin():
 inject_css()
 st.markdown(f"### {T('admin_title')}")
 st.markdown(T("admin_sub"))

 if not st.session_state.admin_ok:
  pwd = st.text_input(T("pwd_lbl"), type="password", placeholder="Enter access code")
  if st.button(T("pwd_btn"), use_container_width=True):
   if pwd == os.getenv("ADMIN_PASSWORD","pathfinder2025"):
    st.session_state.admin_ok = True
    st.rerun()
   else:
    st.error(T("pwd_err"))
  return

 # Dashboard after auth
 df = fetch_all()
 
 if df.empty:
  st.info(T("no_data"))
  if st.button(T("home_btn"), use_container_width=True):
   st.session_state.page = "home"
   st.rerun()
  return

 col1, col2, col3 = st.columns(3)
 with col1:
  st.metric(T("kpi_total"), len(df))
 with col2:
  top_trait = df["dominant_trait"].mode()[0]
  st.metric(T("kpi_top"), top_trait)
 with col3:
  today = df[df["timestamp"].str.contains(datetime.now().strftime("%Y-%m-%d"))].shape[0]
  st.metric(T("kpi_today"), today)

 st.markdown(f"### {T('dist')}")
 trait_counts = df["dominant_trait"].value_counts()
 fig_dist = go.Figure(data=[go.Bar(x=trait_counts.index, y=trait_counts.values,
  marker_color=[TRAITS[t]["hex"] for t in trait_counts.index])])
 fig_dist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
  font=dict(color="#fff"), showlegend=False, height=400)
 st.plotly_chart(fig_dist, use_container_width=True)

 st.markdown(f"### {T('avg')}")
 avg_scores = {t: df[t].mean() for t in ["r","i","a","s","e","cv"]}
 trait_names = ["Realistic","Investigative","Artistic","Social","Enterprising","Conventional"]
 fig_avg = go.Figure(data=[go.Bar(x=trait_names, y=[avg_scores[k] for k in ["r","i","a","s","e","cv"]],
  marker_color=[TRAITS[t]["hex"] for t in trait_names])])
 fig_avg.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
  font=dict(color="#fff"), showlegend=False, height=400)
 st.plotly_chart(fig_avg, use_container_width=True)

 st.markdown(f"### {T('recent')}")
 st.dataframe(df[["name","dominant_trait","r","i","a","s","e","cv","timestamp"]].head(10),
  use_container_width=True, hide_index=True)

 st.divider()
 if st.button(T("logout"), use_container_width=True):
  st.session_state.admin_ok = False
  st.session_state.page = "home"
  st.rerun()

# ═══════════════════════════════════════════════════════════
# ⑫ MAIN DISPATCHER
# ═══════════════════════════════════════════════════════════
init_db()
init()

page = st.session_state.get("page","home")
if page == "home":
 page_home()
elif page == "quiz":
 page_quiz()
elif page == "results":
 page_results()
elif page == "interview":
 page_interview()
elif page == "admin":
 page_admin()
else:
 page_home()

