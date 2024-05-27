import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Smart ATS",
    page_icon="👨‍💼",
    layout="centered",
)

# Sidebar to input Google API Key
st.sidebar.title("ATS Score Calculator")
API_KEY = st.sidebar.text_input("Enter your Google API Key", type="password")
st.sidebar.subheader("Don't have a Google API Key?")
st.sidebar.write("Visit [Google Makersuite](https://makersuite.google.com/app/apikey) and log in with your Google account. Then click on 'Create API Key'.")

# Check if API key is provided
if not API_KEY:
    st.error("Please enter your Google API Key.")
    st.stop()

# Function to configure Gemini AI model with the provided API key
def configure_gemini_api(api_key):
    genai.configure(api_key=api_key)

# Configure Gemini AI model with the provided API key
configure_gemini_api(API_KEY)

# Function to get response from Gemini AI
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

# Function to extract text from uploaded PDF file
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Prompt Template
input_prompt = """
Assume yourself as the best ATS system and below is your score calculation criteria:

ATS Score Calculation Criteria
1. Relevance: Matching the job description's essential criteria with candidate qualifications.

2. Experience: Evaluating the depth and relevance of work experience.

3.Skills: Assessment of both hard and soft skills based on job requirements.

4. Education: Matching the educational background with job prerequisites.

5. Keywords: Ensuring the presence of crucial keywords in the resume and application.

6. Application Quality: Assessing the completeness and professionalism of the application.


1. Keyword Matching (40-50% of the score):
Exact Match: Keywords that appear exactly as in the job description.
Synonyms: Recognizing variations and synonyms of keywords.
Frequency: How often the keywords appear in the resume.
Context: Keywords used in relevant contexts (e.g., “managed a team” vs. “team”).

2. Relevance of Experience (20-30% of the score):
Job Titles: Matching past job titles with the job applied for.
Job Descriptions: Matching past job responsibilities with the job applied for.
Industry: Experience in the same or a related industry.

3. Skills (15-25% of the score)
Hard Skills: Specific technical skills required for the job.
Soft Skills: Important interpersonal and organizational skills.
Skill Level: Proficiency levels indicated for each skill.

4. Education and Certifications (10-20% of the score)
Degree Level: Matching the required level of education (e.g., Bachelor's, Master's).
Field of Study: Relevant academic background.
Certifications: Professional certifications relevant to the job.

5. Job Tenure and Career Progression (10-15% of the score)
Stability: Duration of employment at previous jobs.
Advancement: Evidence of promotions and career growth.

6. Custom Scoring Rules (Variable percentage)
Company Culture Fit: Attributes that align with company values.
Project Experience: Specific project experience relevant to the job.
Other Employer Preferences: Custom criteria set by the employer.

Example of Score Calculation Breakdown

1. Job Posting Keywords (50 points)
Exact Match: 20 points
Synonyms and Variants: 10 points
Frequency: 10 points
Context: 10 points

2. Relevant Experience (30 points)
Job Titles: 10 points
Job Descriptions: 10 points
Industry: 10 points
Skills (25 points)

3. Skills (20 points)
Hard Skills: 15 points
Soft Skills: 5 points
Skill Level: 5 points

4. Education and Certifications (20 points)
Degree Level: 10 points
Field of Study: 5 points
Certifications: 5 points

5. Job Tenure and Career Progression (15 points)
Stability: 10 points
Advancement: 5 points

6. Projects Relevance (15 points)

7. Company Culture Fit: 5 points

Now calculate the ATS score for JD against Resume and give me ATS section wise score and feedback or action item for each section in ATS

Caution: Don't halusinate anything, extract keywords that are mentioned in pdfs only.  
Don't assume that resume will be inline with JD, always consider that resume and JD as 2 independent things and extract data accordingly.

Evaluate the format of resume as well and suggest the ATS friendly format along with suggestions and scores for each section and consolidated scores

After giving suggestions,  as per suggestions update the relevant content in resume and give the resume content. use content mentioned only in resume, don't add anything else extra while updating resume. 
While generating updated resume:
1. Use content from source resume only, don't add anything new that is not mentioned in source resume
2. Prioritise the skills that are mentioned in resume and just reorder the JD skills to first
3. Update career objectiveline that is suitable for JD but don't over promise things

You must consider the job market is very competitive and you should provide the best assistance for improving the resumes. Assign the percentage Matching based on JD and the missing keywords with high accuracy.
resume:{resume}
description:{jd}

I want the response in one single string having the structure
{{"Overall Score":"", "Keyword Matching score":"", "MissingKeywords":[], "keywords feedback":"", "Relevant Experience Score":"", "Relevant Experience Feedback":"","Skills Score":"", "Hard Skills Score":"", "Hard Skills Feedback":"", "Soft Skills Score":"", "Soft Skills Feedback":"",
"Education and Certifications Score":"", "Education and Certifications feedback": "", "Job Tenure and Career Progression Score": "", "Job Tenure and Career Progression Feedback":"", "Projects Relevance Score": "", "Projects Relevance Feedback": "","Company Culture Fit Score":"", "Company Culture Fit Score feedback":""}}
"""


# # Prompt Template
# input_prompt = """
# Hey Act Like a skilled or very experienced ATS (Application Tracking System)
# with a deep understanding of the tech field, software engineering, data science, data analyst
# and big data engineering. Your task is to evaluate the resume based on the given job description.
# You must consider the job market is very competitive and you should provide the 
# best assistance for improving the resumes. Assign the percentage Matching based 
# on JD and the missing keywords with high accuracy.
# resume:{text}
# description:{jd}

# I want the response in one single string having the structure
# {{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
# """

## Streamlit app
st.title("Resume ATS Score")
st.markdown("Made by 😎 [Hardik](https://www.linkedin.com/in/hardikjp/)")
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        resume = input_pdf_text(uploaded_file)
        response = get_gemini_response(input_prompt.format(resume=resume, jd=jd))
        st.subheader("Response:")
        parsed_response = json.loads(response)
        for key, value in parsed_response.items():
            st.write(f"**{key}:** \n\n{value}")
