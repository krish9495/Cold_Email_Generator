import streamlit as st
from utils import clean_text
from chain import Chain
from resume import Resume
from langchain_community.document_loaders import WebBaseLoader
import tempfile
import os

def trim_text(text, max_chars=1000):
    return text[:max_chars] if text else ""

def create_streamlit_app(llm, resume, clean_text):
    st.title("Cold Mail Generator")
    url_input = st.text_input("Enter a URL:")
    resume_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
    additional_info = st.text_area("Additional Information (Optional):", "")
    submit_button = st.button("Submit")

    if submit_button:
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            chain = Chain()
            jobs = chain.extract_jobs(trim_text(data, max_chars=2000))
            
            if resume_file is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    temp_file.write(resume_file.getvalue())
                    temp_file_path = temp_file.name
                resume_text = Resume.extract_resume_text(temp_file_path)
                os.unlink(temp_file_path)  # Clean up the temporary file
            else:
                st.error("Please upload a resume.")
                return

            user = {
                "resume_text": trim_text(resume_text, max_chars=1000),
                "additional_info": trim_text(additional_info, max_chars=500)
            }

            if not jobs or not isinstance(jobs, list):
                st.error("No job information could be extracted from the provided URL.")
                return

            for job in jobs:
                cold_email = chain.write_mail(job, user)
                st.write(f"Generated Cold Email for {job.get('title', 'Position')}: ")
                st.write(cold_email)
                st.write("---")

        except FileNotFoundError:
            st.error("Resume file not found. Please upload a valid resume.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    create_streamlit_app(None, None, clean_text)



