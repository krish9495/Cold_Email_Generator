import fitz  # PyMuPDF
import os
import re

class Resume:
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

    