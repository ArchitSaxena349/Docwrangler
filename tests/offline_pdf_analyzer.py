#!/usr/bin/env python3
"""
Offline PDF analyzer - works without OpenAI API
"""
import os
import re
from pathlib import Path
import PyPDF2

class OfflinePDFAnalyzer:
    def __init__(self):
        self.insurance_keywords = {
            'coverage': ['coverage', 'covered', 'benefit', 'benefits', 'sum insured'],
            'waiting_period': ['waiting period', 'waiting', 'moratorium'],
            'exclusions': ['exclusion', 'excluded', 'not covered', 'limitations'],
            'procedures': ['surgery', 'treatment', 'procedure', 'operation'],
            'amounts': ['amount', 'limit', 'maximum', 'sum', 'rupees', '₹'],
            'age': ['age', 'years', 'year old'],
            'claims': ['claim', 'reimbursement', 'cashless'],
            'maternity': ['maternity', 'pregnancy', 'childbirth'],
            'dental': ['dental', 'teeth', 'oral'],
            'cardiac': ['cardiac', 'heart', 'cardiovascular'],
            'orthopedic': ['orthopedic', 'bone', 'joint', 'knee', 'hip']
        }
    
    def extract_pdf_text(self, pdf_path):
        """Extract text from PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
            return ""
    
    def find_amounts(self, text):
        """Find monetary amounts in text"""
        # Pattern for Indian currency amounts
        patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # ₹50,000
            r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # Rs. 50,000
            r'rupees\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # rupees 50000
            r'(\d+(?:,\d+)*)\s*(?:rupees|₹|Rs)',  # 50,000 rupees
            r'(\d+)\s*lakh',  # 5 lakh
            r'(\d+)\s*crore'  # 1 crore
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.group(1)
                # Convert to number
                try:
                    if 'lakh' in match.group(0).lower():
                        amount = float(amount_str.replace(',', '')) * 100000
                    elif 'crore' in match.group(0).lower():
                        amount = float(amount_str.replace(',', '')) * 10000000
                    else:
                        amount = float(amount_str.replace(',', ''))
                    amounts.append((amount, match.group(0)))
                except:
                    pass
        
        return amounts
    
    def find_waiting_periods(self, text):
        """Find waiting periods in text"""
        patterns = [
            r'(\d+)\s*(?:months?|days?|years?)\s*waiting\s*period',
            r'waiting\s*period\s*(?:of\s*)?(\d+)\s*(?:months?|days?|years?)',
            r'(\d+)\s*(?:months?|days?|years?)\s*(?:from|after)\s*(?:policy|inception)'
        ]
        
        waiting_periods = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                waiting_periods.append(match.group(0))
        
        return waiting_periods
    
    def find_coverage_info(self, text, query_keywords):
        """Find coverage information related to query"""
        relevant_sections = []
        
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
                
            # Check if sentence contains query keywords
            sentence_lower = sentence.lower()
            relevance_score = 0
            
            for keyword in query_keywords:
                if keyword.lower() in sentence_lower:
                    relevance_score += 1
            
            # Also check for insurance-related keywords
            for category, keywords in self.insurance_keywords.items():
                for keyword in keywords:
                    if keyword in sentence_lower:
                        relevance_score += 0.5
            
            if relevance_score > 0:
                relevant_sections.append((sentence, relevance_score))
        
        # Sort by relevance and return top sections
        relevant_sections.sort(key=lambda x: x[1], reverse=True)
        return [section[0] for section in relevant_sections[:10]]
    
    def analyze_query(self, query, pdf_files):
        """Analyze query against PDF files"""
        print(f"🔍 Analyzing query: '{query}'")
        print("="*60)
        
        # Extract keywords from query
        query_keywords = re.findall(r'\b\w+\b', query.lower())
        
        results = {}
        
        for pdf_file in pdf_files:
            print(f"\n📄 Analyzing: {pdf_file}")
            
            # Extract text
            text = self.extract_pdf_text(pdf_file)
            if not text:
                continue
            
            # Find relevant information
            coverage_info = self.find_coverage_info(text, query_keywords)
            amounts = self.find_amounts(text)
            waiting_periods = self.find_waiting_periods(text)
            
            results[pdf_file] = {
                'coverage_info': coverage_info,
                'amounts': amounts,
                'waiting_periods': waiting_periods,
                'text_length': len(text)
            }
            
            # Display results
            print(f"   📊 Text length: {len(text):,} characters")
            print(f"   💰 Found {len(amounts)} monetary amounts")
            print(f"   ⏱️  Found {len(waiting_periods)} waiting periods")
            print(f"   📋 Found {len(coverage_info)} relevant sections")
            
            # Show top amounts
            if amounts:
                top_amounts = sorted(amounts, key=lambda x: x[0], reverse=True)[:3]
                print(f"   💰 Top amounts:")
                for amount, text_match in top_amounts:
                    print(f"      ₹{amount:,.0f} - {text_match}")
            
            # Show waiting periods
            if waiting_periods:
                print(f"   ⏱️  Waiting periods:")
                for period in waiting_periods[:3]:
                    print(f"      {period}")
            
            # Show most relevant coverage info
            if coverage_info:
                print(f"   📋 Most relevant section:")
                print(f"      {coverage_info[0][:200]}...")
        
        return results
    
    def simple_decision_logic(self, query, results):
        """Simple rule-based decision logic"""
        print(f"\n🤖 SIMPLE DECISION ANALYSIS")
        print("="*60)
        
        query_lower = query.lower()
        
        # Check for age in query
        age_match = re.search(r'(\d+)[-\s]*(?:year|yr|y)[-\s]*old|(\d+)[MF]', query)
        age = None
        if age_match:
            age = int(age_match.group(1) or age_match.group(2))
            print(f"👤 Detected age: {age} years")
        
        # Check for procedure
        procedures = ['surgery', 'treatment', 'procedure', 'operation']
        detected_procedure = None
        for proc in procedures:
            if proc in query_lower:
                detected_procedure = proc
                break
        
        if detected_procedure:
            print(f"🏥 Detected procedure: {detected_procedure}")
        
        # Check for policy duration
        duration_match = re.search(r'(\d+)[-\s]*(?:month|year)', query_lower)
        if duration_match:
            duration = int(duration_match.group(1))
            unit = 'months' if 'month' in query_lower else 'years'
            print(f"📅 Policy duration: {duration} {unit}")
        
        # Simple decision logic
        decision = "needs_review"
        confidence = 0.5
        justification = "Basic analysis completed. Manual review recommended."
        
        # Look for coverage amounts across all documents
        all_amounts = []
        for pdf_file, data in results.items():
            all_amounts.extend(data['amounts'])
        
        if all_amounts:
            max_amount = max(all_amounts, key=lambda x: x[0])
            print(f"💰 Maximum coverage found: ₹{max_amount[0]:,.0f}")
            
            if detected_procedure and 'surgery' in detected_procedure:
                decision = "likely_covered"
                confidence = 0.7
                justification = f"Surgery procedures typically covered up to ₹{max_amount[0]:,.0f}"
        
        print(f"\n📋 DECISION: {decision}")
        print(f"🎯 CONFIDENCE: {confidence:.1%}")
        print(f"💡 JUSTIFICATION: {justification}")
        
        return {
            'decision': decision,
            'confidence': confidence,
            'justification': justification,
            'max_amount': max_amount[0] if all_amounts else None
        }

def main():
    """Main function"""
    print("🏥 Offline Insurance PDF Analyzer")
    print("="*50)
    
    analyzer = OfflinePDFAnalyzer()
    
    # Find PDF files in data directory
    data_dir = Path('../data')
    if not data_dir.exists():
        data_dir = Path('./data')  # Try current directory structure
    
    if data_dir.exists():
        pdf_files = [str(data_dir / f) for f in os.listdir(data_dir) if f.endswith('.pdf')]
    else:
        # Fallback to current directory
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found")
        print("💡 Expected location: data/ directory")
        print("💡 Run from project root or tests/ directory")
        return
    
    print(f"📄 Found {len(pdf_files)} PDF files")
    
    # Test queries
    test_queries = [
        "46-year-old male, knee surgery, 3-month policy",
        "What is the maximum coverage amount?",
        "Waiting period for surgery",
        "Maternity benefits coverage",
        "Dental treatment limits"
    ]
    
    for query in test_queries:
        results = analyzer.analyze_query(query, pdf_files)
        decision = analyzer.simple_decision_logic(query, results)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()