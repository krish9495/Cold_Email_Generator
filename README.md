# TailorMail 📨 – AI-Powered Cold Email Generator

**TailorMail** is a Streamlit-based web application that automatically generates personalized cold emails for job applications. It combines the power of **LangChain**, **LLMs (OpenAI/Groq)**, and **resume parsing** to craft tailored outreach emails using your uploaded resume and a job/company URL.

## 🚀 Features

- 📄 **Upload Resume**: Accepts PDF resumes and parses relevant sections.
- 🌐 **Enter Job URL**: Scrapes job descriptions or company details directly from web pages.
- 🧠 **LLM Integration**: Uses LangChain + LLMs (e.g., OpenAI or Groq) to generate tailored cold emails.
- ✍️ **Custom Prompts**: Allows optional user input to guide tone/style.
- ⚡ **Instant Output**: Delivers a professional cold email in seconds.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python (modular architecture)
- **LLMs**: OpenAI / Groq via LangChain
- **Resume Parsing**: PyMuPDF, custom logic
- **Web Scraping**: LangChain `WebBaseLoader`
- **Environment**: `.env` for API key security

---

## 📂 Project Structure

``` bash
Cold_Email_Generator/
├── app/
│ ├── main.py # Streamlit app
│ ├── chain.py # LangChain pipeline
│ ├── resume.py # Resume parsing utilities
│ ├── utils.py # Text cleaning helpers
│ └── .env # Store your API keys securely
└── main.py # Entry point (optional)
```

---

## 💻 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/Cold_Email_Generator.git
```
### 2. Add Your API Key
Create a .env file in the app/ directory:
``` bash
GROQ_API_KEY=your_groq_or_openai_key_here

```
### 3. Run the App
``` bash
streamlit run app/main.py
```
🧪 Example Use Case
Upload your resume in PDF format.

Paste a job or company URL.

(Optional) Add extra instructions like "Make it casual but confident".

Click Submit and get a ready-to-send cold email!
