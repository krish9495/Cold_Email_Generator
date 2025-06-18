import os
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama3-8b-8192"
        )

    def extract_jobs(self, text):
        # First, try to clean and preprocess the text
        cleaned_text = self._clean_job_text(text)
        
        prompt = PromptTemplate.from_template(
            """
You are an expert job information extractor. Analyze the following job posting text and extract key information.

IMPORTANT INSTRUCTIONS:
1. Look for job title, company name, location, and job description
2. If you cannot find specific information, make reasonable inferences from the context
3. Always return valid JSON format
4. If multiple jobs are mentioned, extract all of them
5. Return ONLY the JSON array, no other text

REQUIRED JSON FORMAT:
[
  {{
    "title": "extracted or inferred job title",
    "company": "extracted or inferred company name",
    "location": "extracted or inferred location",
    "description": "key responsibilities and requirements summary"
  }}
]

JOB POSTING TEXT:
{text}

EXTRACTED JSON:
"""
        )
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({"text": cleaned_text})
            
            # Extract content from response
            if hasattr(response, "content"):
                raw_output = response.content.strip()
            else:
                raw_output = str(response).strip()
            
            print("LLM raw output:", raw_output)
            
            # Try multiple methods to extract JSON
            job_data = self._extract_json_from_response(raw_output)
            
            # If we got valid data, return it
            if job_data and len(job_data) > 0 and any(job.get('title') != 'Position Available' for job in job_data):
                return job_data
            
            # If extraction failed, try a different LLM approach
            print("First extraction attempt failed, trying alternative approach...")
            alternative_result = self._try_alternative_extraction(cleaned_text)
            if alternative_result:
                return alternative_result
            
            # Final fallback
            return self._fallback_extraction(cleaned_text)
                
        except Exception as e:
            print(f"Error in extract_jobs: {e}")
            return self._fallback_extraction(cleaned_text)
    
    def _clean_job_text(self, text):
        """Clean and preprocess job posting text"""
        # Remove excessive whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', '', text)
        # Limit text length to avoid token limits
        if len(text) > 4000:
            text = text[:4000] + "..."
        return text.strip()
    
    def _extract_json_from_response(self, response):
        """Try multiple methods to extract JSON from LLM response"""
        # Method 1: Look for JSON array pattern
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Method 2: Try to parse entire response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Method 3: Look for JSON object pattern
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                single_job = json.loads(json_match.group(0))
                return [single_job]  # Wrap in array
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _try_alternative_extraction(self, text):
        """Try a different approach with more specific prompting"""
        alternative_prompt = PromptTemplate.from_template(
            """
Please analyze this job posting and answer these specific questions:

1. What is the job title or position name?
2. What is the company name?
3. Where is the job located?
4. What are the main responsibilities or requirements?

Job Posting:
{text}

Based on your analysis, format the response as:
TITLE: [job title]
COMPANY: [company name]  
LOCATION: [location]
DESCRIPTION: [brief summary of role and requirements]
"""
        )
        
        try:
            chain = alternative_prompt | self.llm
            response = chain.invoke({"text": text})
            
            if hasattr(response, "content"):
                content = response.content
            else:
                content = str(response)
                
            # Parse the structured response
            title_match = re.search(r'TITLE:\s*(.+)', content, re.IGNORECASE)
            company_match = re.search(r'COMPANY:\s*(.+)', content, re.IGNORECASE)
            location_match = re.search(r'LOCATION:\s*(.+)', content, re.IGNORECASE)
            description_match = re.search(r'DESCRIPTION:\s*(.+)', content, re.IGNORECASE | re.DOTALL)
            
            if title_match or company_match:  # At least one should match
                return [{
                    "title": title_match.group(1).strip() if title_match else "Position Available",
                    "company": company_match.group(1).strip() if company_match else "Company Not Specified",
                    "location": location_match.group(1).strip() if location_match else "Location Not Specified",
                    "description": description_match.group(1).strip() if description_match else text[:300] + "..."
                }]
                
        except Exception as e:
            print(f"Alternative extraction failed: {e}")
            
        return None
    
    def _fallback_extraction(self, text):
        """Fallback method using simple text analysis"""
        # Try to extract basic information using regex patterns
        title_patterns = [
            r'(?i)(?:job title|position|role)[:\s]+([^\n\r]+)',
            r'(?i)(?:hiring|seeking|looking for)[:\s]+([^\n\r]+)',
            r'(?i)(?:we are hiring|we are looking for)[:\s]+([^\n\r]+)'
        ]
        
        company_patterns = [
            r'(?i)(?:company|organization)[:\s]+([^\n\r]+)',
            r'(?i)(?:at|@)\s+([A-Z][a-zA-Z\s&]+(?:Inc|LLC|Corp|Ltd|Company)?)',
        ]
        
        location_patterns = [
            r'(?i)(?:location|based in|office)[:\s]+([^\n\r]+)',
            r'(?i)(?:remote|hybrid|on-site|office)[:\s]*(?:in|at)[:\s]+([^\n\r]+)',
        ]
        
        # Extract using patterns
        title = self._extract_with_patterns(text, title_patterns) or "Position Available"
        company = self._extract_with_patterns(text, company_patterns) or "Company Not Specified"
        location = self._extract_with_patterns(text, location_patterns) or "Location Not Specified"
        
        # Create description from first 300 characters
        description = text[:300] + "..." if len(text) > 300 else text
        
        return [{
            "title": title.strip(),
            "company": company.strip(),
            "location": location.strip(),
            "description": description.strip()
        }]
    
    def _extract_with_patterns(self, text, patterns):
        """Extract information using regex patterns"""
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    def write_mail(self, job: dict, user: dict):
        prompt = PromptTemplate.from_template(
            """
You are a professional job seeker writing a cold email. Create a compelling, personalized email that highlights relevant experience.

JOB DETAILS:
- Position: {title}
- Company: {company}
- Location: {location}
- Description: {description}

CANDIDATE PROFILE:
{resume_text}

ADDITIONAL INFORMATION:
{additional_info}

Write a professional cold email with:
1. Engaging subject line
2. Brief introduction
3. Relevant skills/experience highlights
4. Value proposition
5. Professional closing

Format the email properly with subject line and body.
"""
        )

        inputs = {
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "description": job.get("description", ""),
            "resume_text": user.get("resume_text", ""),
            "additional_info": user.get("additional_info", ""),
        }

        try:
            chain = prompt | self.llm
            response = chain.invoke(inputs)
            
            if hasattr(response, "content"):
                return response.content
            else:
                return str(response)
        except Exception as e:
            print(f"Error generating email: {e}")
            return "Error generating email. Please try again."