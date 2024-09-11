import streamlit as st
import time, datetime, io, random
import pandas as pd
import base64
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
from pdfminer3.pdfpage import PDFPage
from PIL import Image
import plotly.express as px
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
import pymysql
import pafy
from streamlit_tags import st_tags

# Fetch YouTube Video
def fetch_yt_video(link):
    video = pafy.new(link)
    return video.title

# Generate CSV Download Link
def get_table_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Required for encoding CSV to base64
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Read PDF
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

# Display PDF
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Course Recommender
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

# Connect to Database
connection = pymysql.connect(host='localhost', user='root', password='')
cursor = connection.cursor()

# Insert Data to DB
def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    DB_table_name = 'user_data'
    insert_sql = "INSERT INTO " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (
        name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills,
        courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

# Main Streamlit Web App
def run():
    st.set_page_config(
        page_title="Smart Resume Analyzer",
        page_icon='./Logo/SRA_Logo.ico',
    )
    
    st.title("Smart Resume Analyzer")
    st.sidebar.markdown("# Choose User")
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    
    img = Image.open('./Logo/SRA_Logo.jpg')
    img = img.resize((250, 250))
    st.image(img)
    
    # Database Initialization
    db_sql = """CREATE DATABASE IF NOT EXISTS SRA;"""
    cursor.execute(db_sql)
    connection.select_db("sra")

    DB_table_name = 'user_data'
    table_sql = """CREATE TABLE IF NOT EXISTS """ + DB_table_name + """
                (ID INT NOT NULL AUTO_INCREMENT,
                Name varchar(100) NOT NULL,
                Email_ID VARCHAR(50) NOT NULL,
                resume_score VARCHAR(8) NOT NULL,
                Timestamp VARCHAR(50) NOT NULL,
                Page_no VARCHAR(5) NOT NULL,
                Predicted_Field VARCHAR(25) NOT NULL,
                User_level VARCHAR(30) NOT NULL,
                Actual_skills VARCHAR(300) NOT NULL,
                Recommended_skills VARCHAR(300) NOT NULL,
                Recommended_courses VARCHAR(600) NOT NULL,
                PRIMARY KEY (ID));"""
    cursor.execute(table_sql)

    if choice == 'Normal User':
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            # Extract Resume Data
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic Info**")
                st.text('Name: ' + resume_data['name'])
                st.text('Email: ' + resume_data['email'])
                st.text('Contact: ' + resume_data['mobile_number'])
                st.text('Resume Pages: ' + str(resume_data['no_of_pages']))

                # Candidate Level
                cand_level = 'Experienced' if resume_data['no_of_pages'] >= 3 else 'Intermediate' if resume_data['no_of_pages'] == 2 else 'Fresher'
                st.markdown(f'You are at {cand_level} level!')

                st.subheader("**Skills Recommendation💡**")
                keywords = st_tags(label='### Skills that you have', value=resume_data['skills'], key='1')

                ds_keywords = ['tensorflow', 'keras', 'pytorch', 'machine learning']
                web_keywords = ['react', 'django', 'node jS', 'php']
                android_keywords = ['android', 'flutter', 'kotlin']
                ios_keywords = ['ios', 'swift', 'xcode']
                uiux_keywords = ['ux', 'figma', 'adobe xd']

                recommended_skills = []
                reco_field = ''
                rec_course = ''
                for i in resume_data['skills']:
                    if i.lower() in ds_keywords:
                        reco_field = 'Data Science'
                        st.success("**Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization', 'ML Algorithms', 'Pytorch']
                        rec_course = course_recommender(ds_course)
                        break
                    elif i.lower() in web_keywords:
                        reco_field = 'Web Development'
                        st.success("**Our analysis says you are looking for Web Development Jobs.**")
                        recommended_skills = ['React', 'Django', 'Node JS']
                        rec_course = course_recommender(web_course)
                        break

                st.subheader("**Resume Score📝**")
                resume_score = 0
                if 'Objective' in resume_text: resume_score += 20
                if 'Declaration' in resume_text: resume_score += 20
                if 'Hobbies' in resume_text: resume_score += 20
                if 'Achievements' in resume_text: resume_score += 20
                if 'Projects' in resume_text: resume_score += 20

                st.success(f'**Your Resume Writing Score: {resume_score}**')
                st.warning("**This score is calculated based on the content in your Resume.**")
                
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                insert_data(resume_data['name'], resume_data['email'], resume_score, timestamp,
                            resume_data['no_of_pages'], reco_field, cand_level, resume_data['skills'],
                            recommended_skills, rec_course)

                st.balloons()

    else:
        st.success('Welcome to Admin Side')
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'machine_learning_hub' and ad_password == 'mlhub123':
                st.success("Welcome Kushal")
                # Display Data
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()
                st.header("**User's👨‍💻 Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                 'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                 'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df, 'User_Data.csv', 'Download Report'), unsafe_allow_html=True)
                ## Admin Side Data
                query = 'select * from user_data;'
                plot_data = pd.read_sql(query, connection)

                ## Pie chart for predicted field recommendations
                labels = plot_data.Predicted_Field.unique()
                print(labels)
                values = plot_data.Predicted_Field.value_counts()
                print(values)
                st.subheader("📈 **Pie-Chart for Predicted Field Recommendations**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills')
                st.plotly_chart(fig)

                ### Pie chart for User's👨‍💻 Experienced Level
                labels = plot_data.User_level.unique()
                values = plot_data.User_level.value_counts()
                st.subheader("📈 ** Pie-Chart for User's👨‍💻 Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart📈 for User's👨‍💻 Experienced Level")
                st.plotly_chart(fig)


            else:
                st.error("Wrong ID & Password Provided")


run()
