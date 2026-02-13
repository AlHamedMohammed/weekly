"""
SIMPLE QUALITY MANAGER AGENT
ISO 9001 Expert - No RAG, No complex folders, Just works
"""

import os
import requests
import json
import re
from dataclasses import dataclass
from typing import Optional, List
from dotenv import load_dotenv

# Load API key
load_dotenv()

# ==================== CONFIG ====================
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/anthropic/claude-3.5-sonnet")
API_BASE = "https://openrouter.ai/api/v1"

# ==================== SYSTEM PROMPT ====================
SYSTEM_PROMPT = """You are a Senior Quality Manager, ISO 9001 Lead Auditor.

ROLE:
- You ONLY answer quality management questions
- You ALWAYS use the template below
- You cite ISO 9001:2015 clauses when relevant
- You NEVER invent company procedures

TEMPLATE - USE EXACTLY THIS:
---
**Context:** [Restate the question]

**Analysis:** [ISO 9001 analysis]

**Risks:** [Quality risks]

**Recommendation:** [Actionable steps]

**ISO Clause:** [e.g., 8.5.1, 9.1.3, or "Not applicable"]

**Conclusion:** [Summary]
---"""

# ==================== DATA MODELS ====================
@dataclass
class QualityResponse:
    context: str
    analysis: str
    risks: str
    recommendation: str
    iso_clause: str
    conclusion: str
    
    def display(self):
        print(f"\n---")
        print(f"**Context:** {self.context}")
        print(f"\n**Analysis:** {self.analysis}")
        print(f"\n**Risks:** {self.risks}")
        print(f"\n**Recommendation:** {self.recommendation}")
        print(f"\n**ISO Clause:** {self.iso_clause}")
        print(f"\n**Conclusion:** {self.conclusion}")
        print(f"---\n")

# ==================== API CLIENT ====================
import os
import requests
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/anthropic/claude-3.5-sonnet")
API_BASE = "https://openrouter.ai/api/v1"

# -----------------------------
# System prompt for the bot
# -----------------------------
SYSTEM_PROMPT = """
You are a Senior Quality Management Expert with extensive knowledge of ISO 9001:2015 and best practices in quality management systems (QMS).

Your role is to act as an advisor, auditor, and consultant. Provide guidance on ISO 9001 clauses, audit preparation, CAPA (Corrective and Preventive Actions), risk-based thinking, PDCA cycles, process improvement, and quality documentation.

Rules for your responses:
1. Always provide structured, professional, and concise answers.
2. Use clear headings, numbered lists, or bullet points.
3. Give actionable recommendations when applicable, especially for corrective or preventive actions.
4. If the question requires interpretation of ISO clauses, provide examples or practical implementation guidance.
5. If information is missing or outside your knowledge, clearly state: "Information not found or insufficient."
6. Avoid speculation, vague answers, or generic text.
7. Maintain a formal, professional, and consultative tone.
8. Always think and answer like a senior quality auditor reviewing an organization's QMS.
9. Include references to ISO 9001 clauses when relevant.
10. Prioritize clarity and precision over verbosity.
"""

# -----------------------------
# OpenRouter client definition
# -----------------------------
class OpenRouterClient:
    def __init__(self):
        if not API_KEY:
            raise ValueError("❌ OPENROUTER_API_KEY not found in .env file")
        
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    
    def ask(self, system_prompt, user_message):
        """Send a chat request to OpenRouter API"""
        try:
            response = requests.post(
                f"{API_BASE}/chat/completions",
                headers=self.headers,
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 800
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            else:
                return f"❌ API Error {response.status_code}: {response.text}"
                
        except Exception as e:
            return f"❌ Exception occurred: {str(e)}"

# -----------------------------
# Initialize client
# -----------------------------
client = OpenRouterClient()

# -----------------------------
# Function to ask the bot
# -----------------------------
def ask_quality_bot(question: str) -> str:
    return client.ask(SYSTEM_PROMPT, question)

# -----------------------------
# Main interactive loop
# -----------------------------
if __name__ == "__main__":
    print("\n📌 ISO 9001 Quality Assistant (Claude 3.5 Sonnet)\n")
    
    while True:
        user_input = input("Ask your question (or type 'exit'): ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        answer = ask_quality_bot(user_input)
        print("\nAnswer:\n")
        print(answer)
        print("\n" + "-"*60 + "\n")


# ==================== QUALITY AGENT ====================
class QualityAgent:
    def __init__(self):
        self.client = OpenRouterClient()
        print(f"✅ Quality Agent ready | Model: {MODEL}")
    
    def parse_response(self, text):
        """Extract sections from template"""
        sections = {
            'context': '', 'analysis': '', 'risks': '',
            'recommendation': '', 'iso_clause': '', 'conclusion': ''
        }
        
        # Simple regex extraction
        patterns = {
            'context': r'\*\*Context:\*\*\s*(.*?)(?=\*\*Analysis:|\Z)',
            'analysis': r'\*\*Analysis:\*\*\s*(.*?)(?=\*\*Risks:|\Z)',
            'risks': r'\*\*Risks:\*\*\s*(.*?)(?=\*\*Recommendation:|\Z)',
            'recommendation': r'\*\*Recommendation:\*\*\s*(.*?)(?=\*\*ISO Clause:|\Z)',
            'iso_clause': r'\*\*ISO Clause:\*\*\s*(.*?)(?=\*\*Conclusion:|\Z)',
            'conclusion': r'\*\*Conclusion:\*\*\s*(.*?)(?=\Z)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                sections[key] = match.group(1).strip()
        
        return sections
    
    def ask(self, question, context=None):
        """Ask a quality question"""
        print("⏳ Thinking...")
        
        # Build prompt
        user_prompt = f"Question: {question}"
        if context:
            user_prompt += f"\nContext: {context}"
        user_prompt += "\n\nUse the EXACT template with **bold headers**."
        
        # Get response
        response_text = self.client.ask(SYSTEM_PROMPT, user_prompt)
        
        # Parse response
        parsed = self.parse_response(response_text)
        
        # Create response object
        return QualityResponse(
            context=parsed['context'] or question,
            analysis=parsed['analysis'] or "Analysis not available",
            risks=parsed['risks'] or "No specific risks identified",
            recommendation=parsed['recommendation'] or "See ISO 9001:2015 requirements",
            iso_clause=parsed['iso_clause'] or "Not applicable",
            conclusion=parsed['conclusion'] or "Analysis complete"
        )
    
    def capa(self, issue):
        """Quick CAPA analysis"""
        return self.ask(
            f"Perform CAPA analysis for: {issue}",
            "This is a quality issue requiring root cause analysis and corrective actions."
        )
    
    def audit(self, finding):
        """Quick audit finding analysis"""
        return self.ask(
            f"Evaluate this audit finding: {finding}",
            "This is an ISO 9001 audit non-conformity."
        )

# ==================== SIMPLE TEST ====================
if __name__ == "__main__":
    # Quick test
    agent = QualityAgent()
    
    # Test 1: CAPA
    print("\n" + "="*50)
    print("📋 TEST 1: CAPA Analysis")
    print("="*50)
    response = agent.capa("Customer complaints about packaging increased 30%")
    response.display()
    
    # Test 2: Audit
    print("="*50)
    print("📋 TEST 2: Audit Finding")
    print("="*50)
    response = agent.audit("No management review records for 6 months")
    response.display()