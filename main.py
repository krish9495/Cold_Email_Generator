from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader

from langchain_core.prompts import PromptTemplate

# # model
llm=ChatGroq(
    model='llama-3.3-70b-versatile',
    temperature=0,
    groq_api_key='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'
)


# # webscraping using webbaseloader
loader=WebBaseLoader("https://www.google.com/about/careers/applications/jobs/results/88073492611637958-senior-technical-program-manager-semantic-perception?tag=ai-spotlight")
page_data=loader.load().pop().page_content
# # print(page_data)


# # prompt template extraction detail of JD

prompt_extract=PromptTemplate.from_template(
    template="""
    ###SCRAPED TEXT FROM THE WEBSITE:
    {page_data}
    ###INSTRUCTION
    The scraped text is from the career's page of a website.
    Your job is to extract the job postings and return them in JSON format containi
    following keys:
    'role' ,
    'experience'
    'skills' and 'description.
    Only return the valid JSON.
    VALID JSON (NO PREAMBLE):
    """
)
chain_extract=prompt_extract|llm
res=chain_extract.invoke(input={'page_data':page_data})
# print(res.content)

# this res.content is string objetc we need to parse it into json 

from langchain_core.output_parsers import JsonOutputParser
json_parser=JsonOutputParser()
job_description=json_parser.parse(res.content)

# print(job_description)


#taking resume 
import fitz  # PyMuPDF
import os

def extract_resume_text(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"No file found at {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

resume_text=extract_resume_text(r'C:\Users\avani\Downloads\Resume_june.pdf')
# print(text)


# labelling the resume content into section 

import re

def label_resume_sections(resume_text):
    # Define common section headers (case-insensitive)
    sections = [
        "objective",
        "summary",
        "education",
        "skills",
        "experience",
        "projects",
        "certifications",
        "achievements",
        "activities",
        "interests",
        "contact",
    ]

    # Build a regex pattern to split on these headers
    pattern = r'(?i)^\s*(' + '|'.join(sections) + r')\s*$'

    # Split the text into lines for easier processing
    lines = resume_text.split('\n')

    labeled_sections = {}
    current_section = "General"
    labeled_sections[current_section] = []

    for line in lines:
        line_strip = line.strip()
        # Check if line matches a section header
        if re.match(pattern, line_strip):
            current_section = line_strip.capitalize()
            labeled_sections[current_section] = []
        else:
            labeled_sections[current_section].append(line_strip)

    # Join lines back per section
    for section in labeled_sections:
        labeled_sections[section] = '\n'.join(filter(None, labeled_sections[section]))

    return labeled_sections


sections = label_resume_sections(resume_text)

for sec, content in sections.items():
    print(f"--- {sec} ---\n{content}\n")




# prompt template for writing the cold mail
from langchain.prompts import PromptTemplate

cold_email_prompt = PromptTemplate.from_template("""
You are an expert assistant helping job seekers write cold emails.

Below is a job description and a candidate resume. Write a short, personalized, and professional cold email the candidate can send to apply for the job. Mention relevant skills or experiences. Keep the tone confident and respectful.

[JOB DESCRIPTION]
{job_description}

[RESUME]
{resume_text}

Write the email below:
""")

chain_email=cold_email_prompt|llm
res=chain_email.invoke({'job_description':job_description,'resume_text':resume_text})
print(res.content)