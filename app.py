import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import matplotlib.pyplot as plt

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
API_KEY = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
st.sidebar.subheader("Don't have a Google API Key?")
st.sidebar.write("Visit [OpenAI API Keys page](https://platform.openai.com/settings/profile?tab=api-keys) and log in with your openai account. Then click on 'Create API Key'.")



# Check if API key is provided
if not API_KEY:
    st.error("Please enter your OpenAI API Key.")
    st.stop()

client = OpenAI(api_key=API_KEY)


# Function to get response from Gemini AI
def get_openai_response(system_prompt, user_prompt):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    # model = genai.GenerativeModel('gemini-pro')
    # response = model.generate_content(input)
    return completion.choices[0].message.content

# Function to extract text from uploaded PDF file
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Prompt Template
system_prompt = """
Assume yourself as the best ATS system and below is your score calculation criteria:

ATS Score Calculation Criteria
1. Relevance: Matching the job description's essential criteria with candidate qualifications.

2. Experience: Evaluating the depth and relevance of work experience.

3.Skills: Assessment of both hard and soft skills based on job requirements.

4. Education: Matching the educational background with job prerequisites.

5. Keywords: Ensuring the presence of crucial keywords in the resume and application.

6. Application Quality: Assessing the completeness and professionalism of the application.


1. Keyword Matching (40% of the score):
Exact Match: Keywords that appear exactly as in the job description.
Synonyms: Recognizing variations and synonyms of keywords.
Frequency: How often the keywords appear in the resume.
Context: Keywords used in relevant contexts (e.g., “managed a team” vs. “team”).

2. Relevance of Experience (15% of the score):
Job Titles: Matching past job titles with the job applied for.
Job Descriptions: Matching past job responsibilities with the job applied for.
Industry: Experience in the same or a related industry.

3. Skills (20% of the score)
Hard Skills: Specific technical skills required for the job.
Soft Skills: Important interpersonal and organizational skills.
Skill Level: Proficiency levels indicated for each skill.

4. Education and Certifications (10% of the score)
Degree Level: Matching the required level of education (e.g., Bachelor's, Master's).
Field of Study: Relevant academic background.
Certifications: Professional certifications relevant to the job.

5. Job Tenure and Career Progression (5% of the score)
Stability: Duration of employment at previous jobs.
Advancement: Evidence of promotions and career growth.

6. Project and its relevance to JD (10%)

Example of Score Calculation Breakdown
```
1. Keyword Matching (28/60)
Exact Match: 8/35 
Synonyms and Variants: 10/15
Frequency: 10/10

2. Relevant Experience (5/22.5)
Relevant Experience: 5/22.5 

3. Skills (10/30)
Hard Skills: 8/20 
Soft Skills: 2/10

4. Education and Certifications (14/22.5)
Degree Level: 10/12.5
Field of Study: 2/5 
Certifications: 2/5

5. Job Tenure and Career Progression (5/7.5)
Stability: 4/5 
Advancement: 1/2.5 

6. Projects Relevance (10/15)
Relevance of Technologies used in project: 8/10
Complexity of project: 2/5


Overall Score = (sum of all numerators of each section)/(sum of all denomenator of all sections)

Overall Score = 77/150
```

Now calculate the ATS score for JD against Resume and give me ATS section wise score and feedback or action item for each section in ATS

Caution: Don't halusinate anything, extract keywords that are mentioned in pdfs only.  
Don't assume that resume will be inline with JD, always consider that resume and JD as 2 independent things and extract data accordingly.

You must consider the job market is very competitive and you should provide the best assistance for improving the resumes. Assign the percentage Matching based on JD and the missing keywords with high accuracy.

Also your output will be evaluated on following things:
1. Always denominator should be 150 points
2. And the score calculated should be consistent and should have rationale based on the sub criteria that is mentioned in the prompt
3. The result should always be a string.

"""

user_prompt = """
resume:{resume}
description:{jd}

I want the response in the string format having the below format
{{"Overall Score":"sum of acheived points/150","Overall Score percent":"%", "Keyword Matching score":"<Achieved points>/60",
"Keyword Matching percent":"%",
 "MissingKeywords":[], "Keywords feedback":"", "Relevant Experience Score":"<Achieved points>/22.5", "Relevant Experience Feedback":"","Relevant Experience percent":"%", "Skills Score":"<Achieved points>/30", "Skills percent":"%",  "Hard Skills Score":"<Achieved points>/20", "Hard Skills Feedback":"", "Soft Skills Score":"<Achieved points>/10", "Soft Skills Feedback":"",
"Education and Certifications Score":"<Achieved points>/22.5", 
"Education and Certifications percent":"%",
"Education and Certifications feedback": "", "Job Tenure and Career Progression Score": "<Achieved points>/7.5",
"Job Tenure and Career Progression percent":"%",
 "Job Tenure and Career Progression Feedback":"", "Projects Relevance Score": "<Achieved points>/15", "Projects Relevance percent":"%", "Projects Relevance Feedback": "",}}
"""

def get_percent_value(input):
    return float(input.strip('%'))

## Streamlit app
st.title("Resume ATS Score")
st.markdown("Made with ❤️")
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        resume = input_pdf_text(uploaded_file)
        response = get_openai_response(system_prompt, user_prompt.format(resume=resume, jd=jd))
        st.write(response)
        json_result = json.loads(response)
        print(json_result)
        # Data
        data = {"Overall Score":get_percent_value(json_result["Overall Score percent"]), "Keywords score": get_percent_value(json_result["Keyword Matching percent"]), "Skills score": get_percent_value(json_result["Skills percent"]), "Experience score": get_percent_value(json_result["Relevant Experience percent"]), "Education and Certifications Score":get_percent_value(json_result["Education and Certifications percent"]),"Job Tenure and Career Progression Score":get_percent_value(json_result["Job Tenure and Career Progression percent"]), "Projects Relevance Score": get_percent_value(json_result["Projects Relevance percent"])}

        # Streamlit App
        st.title("Feedback on resume:")

        # Create a list to hold the Streamlit columns
        columns = st.columns(4)

        # Counter for current column index
        col_index = 0

        # Iterate through the data
        for category, score in data.items():

            # Get the current column to use
            with columns[col_index]:
                st.write(f"**{category}:**")

                # Create and display the pie chart (same as before)
                fig, ax = plt.subplots(figsize=(2, 2))
                wedgeprops = {'width': 0.2, 'edgecolor': 'w'}
                textprops = {'fontsize': 12}
                ax.pie([score, 100 - score], wedgeprops=wedgeprops, startangle=90, colors=['skyblue', 'lightgray'])
                centre_circle = plt.Circle((0, 0), 0.70, fc='white')
                fig.gca().add_artist(centre_circle)
                ax.axis('equal')
                ax.text(0, 0, f"{score}%", ha='center', va='center', fontsize=14)
                st.pyplot(fig)

            # Move to the next column, wrapping to the next row if needed
            col_index = (col_index + 1) % 4

        for key, value in json_result.items():
            st.write(f"**{key}:** \n\n{value}")

