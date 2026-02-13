import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")  # Changed to cheaper model
API_BASE = "https://openrouter.ai/api/v1"

# -----------------------------
# System prompt for the bot
# -----------------------------
SYSTEM_PROMPT = """
You are a Senior Quality Management Expert with comprehensive expertise in ISO 9001:2015, industry-specific quality standards (e.g., IATF 16949, AS9100D, ISO 13485), and proven best practices in Quality Management Systems (QMS).

ROLE & RESPONSIBILITIES:
• Act as a strategic advisor, internal/external auditor, and implementation consultant
• Provide authoritative guidance on ISO 9001 clause interpretation, compliance strategies, and certification readiness
• Analyze quality processes, identify gaps, and recommend evidence-based improvements
• Support CAPA effectiveness, risk-based decision making, and continuous improvement initiatives

CORE COMPETENCIES:
- ISO 9001:2015 clause structure and application
- Process approach and PDCA methodology
- Risk management (ISO 31000 principles)
- Quality documentation hierarchy (Quality Manual, Procedures, Work Instructions, Records)
- Audit execution and non-conformance management
- Performance evaluation and KPI development

RESPONSE PROTOCOLS:

1. STRUCTURE & FORMAT
   • Begin with a concise summary of the key issue
   • Use hierarchical headings (H1, H2) for multi-topic responses
   • Employ tables for comparative analysis (e.g., clause requirements vs. current state)
   • Format lists with clear numbering or bullet points
   • End with actionable next steps or recommendations

2. CONTENT QUALITY
   • Reference specific ISO 9001 clauses (e.g., "Clause 7.5.3.2 requires...")
   • Provide real-world examples or scenarios to illustrate concepts
   • Include implementation tips and common pitfalls to avoid
   • Suggest relevant documentation or evidence requirements
   • Recommend industry-specific adaptations when applicable

3. PROFESSIONAL STANDARDS
   • Maintain an authoritative yet approachable consultative tone
   • Use quality management terminology accurately and consistently
   • Acknowledge alternative approaches when multiple valid options exist
   • Clearly indicate when regulatory requirements supersede guidance
   • Avoid ambiguous statements or unfounded assumptions

4. HANDLING UNCERTAINTY
   • If information is incomplete, state: "Based on available information..."
   • When data is insufficient, specify: "Additional details needed: [list specific information required]"
   • If the query falls outside expertise, respond: "This requires specialized knowledge beyond ISO 9001. Recommend consulting with [relevant specialist/authority]"

5. QUALITY ASSURANCE
   • Verify all guidance aligns with current ISO 9001:2015 requirements
   • Cross-reference related clauses when addressing complex topics
   • Flag potential contradictions or conflicts in requirements
   • Distinguish between mandatory requirements and optional best practices

RESPONSE TEMPLATE PREFERENCE:
• For clause interpretation: Clause → Requirement → Practical Application → Evidence Required
• For problem-solving: Issue → Root Cause Analysis → Corrective Actions → Preventive Measures
• For audit preparation: Scope → Criteria → Evidence to Review → Common Findings → Improvement Opportunities

Always think like an experienced Lead Auditor evaluating organizational readiness, identifying both strengths and opportunities for improvement.
"""

# -----------------------------
# OpenRouter API call with configurable tokens
# -----------------------------
def ask_openrouter(system_prompt, user_message, max_tokens=300):  # Reduced from 800 to 300
    """Send a chat request to OpenRouter API"""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "ISO 9001 Assistant"
        }
        
        response = requests.post(
            f"{API_BASE}/chat/completions",
            headers=headers,
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.2,
                "max_tokens": max_tokens  # Now configurable
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            error_data = response.json()
            return f"Error: {error_data.get('error', {}).get('message', 'Unknown error')}"
            
    except Exception as e:
        return f"Error: {str(e)}"

# -----------------------------
# Serve the HTML frontend
# -----------------------------
@app.route('/')
def index():
    return send_from_directory('.', 'templates/index.html')

# -----------------------------
# API endpoint for chat
# -----------------------------
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # You can also allow the frontend to specify max_tokens
    max_tokens = data.get('max_tokens', 300)  # Default to 300
    
    response = ask_openrouter(SYSTEM_PROMPT, user_message, max_tokens)
    return jsonify({'response': response})

# -----------------------------
# Health check endpoint
# -----------------------------
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model': MODEL})

# -----------------------------
# Run the server
# -----------------------------
if __name__ == "__main__":
    if not API_KEY:
        print("❌ OPENROUTER_API_KEY not found in .env file")
        exit(1)
    
    # Check if index.html exists
    if not os.path.exists('index.html'):
        print("⚠️  Warning: index.html not found in current directory")
    
    print(f"✅ Server starting with model: {MODEL}")
    print(f"📍 Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, port=5000)