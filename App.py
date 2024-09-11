import subprocess
import sys

# Run the custom initialization script
subprocess.check_call([sys.executable, 'nltk_init.py'])

import streamlit as st
import pandas as pd
import base64, random
import time, datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io
from streamlit_tags import st_tags
from PIL import Image
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
import pafy
import plotly.express as px
import os
import nltk


def fetch_yt_video(link):
    video = pafy.new(link)
    return video.title

def get_table_download_link(df, filename, text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()

    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("**Courses & Certificates🎓 Recommendations**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

# CSV file to store the user data
CSV_FILE = "user_data.csv"

def insert_data_csv(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['Name', 'Email', 'Resume Score', 'Timestamp', 'No of Pages', 'Predicted Field', 'User Level', 'Skills', 'Recommended Skills', 'Recommended Courses'])
    else:
        df = pd.read_csv(CSV_FILE)

    new_data = {
        'Name': name,
        'Email': email,
        'Resume Score': res_score,
        'Timestamp': timestamp,
        'No of Pages': no_of_pages,
        'Predicted Field': reco_field,
        'User Level': cand_level,
        'Skills': skills,
        'Recommended Skills': recommended_skills,
        'Recommended Courses': courses
    }

    df = df.append(new_data, ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon='./Logo/SRA_Logo.ico',
)

def run():
    st.title("Smart Resume Analyser")
    st.sidebar.markdown("# Choose User")
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    img = Image.open('./Logo/SRA_Logo.jpg')
    img = img.resize((250, 250))
    st.image(img)

    if choice == 'Normal User':
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()

            if resume_data:
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data.get('name', 'User'))
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: ' + resume_data.get('name', 'N/A'))
                    st.text('Email: ' + resume_data.get('email', 'N/A'))
                    st.text('Contact: ' + resume_data.get('mobile_number', 'N/A'))
                    st.text('Resume pages: ' + str(resume_data.get('no_of_pages', 'N/A')))
                except:
                    pass

                cand_level = ''
                if resume_data.get('no_of_pages', 0) == 1:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''', unsafe_allow_html=True)
                elif resume_data.get('no_of_pages', 0) == 2:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''', unsafe_allow_html=True)
                elif resume_data.get('no_of_pages', 0) >= 3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!</h4>''', unsafe_allow_html=True)

                st.subheader("**Skills Recommendation💡**")
                keywords = st_tags(label='### Skills that you have', text='See our skills recommendation', value=resume_data.get('skills', []), key='1')

                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit']
                web_keyword = ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
                ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode', 'objective c']
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes', 'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator', 'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'user experience']

                recommended_skills = []
                reco_field = ''
                rec_course = []
                for i in resume_data.get('skills', []):
                    if i.lower() in ds_keyword:
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling', 'Data Mining', 'Clustering & Classification', 'Data Analytics', 'ML Algorithms']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='2')
                        rec_course = course_recommender(ds_course)
                        break
                    elif i.lower() in web_keyword:
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React', 'Django', 'Node JS', 'PHP', 'Laravel']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='3')
                        rec_course = course_recommender(web_course)
                        break
                    elif i.lower() in android_keyword:
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android Development Jobs **")
                        recommended_skills = ['Java', 'Kotlin', 'Android SDK', 'Flutter']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='4')
                        rec_course = course_recommender(android_course)
                        break
                    elif i.lower() in ios_keyword:
                        reco_field = 'iOS Development'
                        st.success("** Our analysis says you are looking for iOS Development Jobs **")
                        recommended_skills = ['Swift', 'Objective-C', 'Xcode']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='5')
                        rec_course = course_recommender(ios_course)
                        break
                    elif i.lower() in uiux_keyword:
                        reco_field = 'UI/UX Design'
                        st.success("** Our analysis says you are looking for UI/UX Design Jobs **")
                        recommended_skills = ['Wireframing', 'Prototyping', 'User Research', 'Usability Testing']
                        recommended_keywords = st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='6')
                        rec_course = course_recommender(uiux_course)
                        break

                st.subheader("** Recommended Courses 📚**")
                st.markdown(get_table_download_link(pd.DataFrame(rec_course, columns=['Courses']), 'courses.csv', 'Download Courses'), unsafe_allow_html=True)
                st.subheader("** Other Resume Data📁**")
                st.write("Recommendations of Videos related to Resume Writing")
                st.video(resume_videos)
                st.write("Recommendations of Videos related to Interviews")
                st.video(interview_videos)

                # Save data to CSV
                insert_data_csv(
                    resume_data.get('name', 'N/A'),
                    resume_data.get('email', 'N/A'),
                    resume_data.get('score', 'N/A'),
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    resume_data.get('no_of_pages', 'N/A'),
                    reco_field,
                    cand_level,
                    resume_data.get('skills', []),
                    recommended_skills,
                    rec_course
                )
    else:
        st.write("Admin functionalities are under development.")

if __name__ == "__main__":
    run()
