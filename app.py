from flask import Flask,render_template,jsonify,request,send_file
from project_app.utils import Section_Analyze
import pandas as pd
import numpy as np
import requests
from config import upload_save, not_found_img,right_ans_save, wrong_ans_save,full_save,img_paths
app = Flask(__name__)


@app.route("/")
def home():
    sec_class = Section_Analyze()
    sec_class.Empty_folder()
    return render_template("home.html")

@app.route("/upload", methods =['get','post'])
def upload_file():

    if 'fileInput' not in request.files:
        return 'No file found'
    
    file = request.files ['fileInput']
    if file.filename == '':
        return 'No selected file'
    file.save(upload_save)
    return "File Uploaded Successfully <p> <a href='/up_analyze'> Analyze File <p>"

@app.route("/up_analyze")
def upload_analyz():
    with open (upload_save, "rb") as f:
        data = f.read()
    section = Section_Analyze()
    df,marks_obt = section.Dataframe(data)
    candidate_info = "No data"
    candidate_info = section.Student_info(data)
    bg_analysis = section.Ans_Analyze(data)
    return render_template("index.html",table_cand_info = candidate_info,
                           table_html=df,result = marks_obt,img_path_list = img_paths)

@app.route("/input",methods =['get','POST'])
def analyze():
    candidate_info = pd.DataFrame(data= np.zeros(10))
    marks = ""
    img_pas = []
    if request.method == 'POST':
        data = request.form
        link = data["response_link"]
        response = requests.get(link)
        print(response.status_code)
        if response.status_code == 200:
            html = response.content
            marks,img_pas ="Not evaluated please re-try","No path found"
            app = Section_Analyze()
            dataframe,marks = app.Dataframe(html)
            print(marks)
            bg_end = app.Ans_Analyze(html)
            candidate_info = app.Student_info(html)
        else:
            return send_file(not_found_img,mimetype='image/jpg')

    else:
        dataframe = 'Input data not found'
    return render_template('index.html',table_cand_info = candidate_info,
                           table_html=dataframe,result = marks,img_path_list = img_paths)

@app.route("/Ans_analyze")
def ans_analyze():
    return render_template("analysis.html")


@app.route("/right_ans")
def right_ans():
    return render_template("right_ans.html")


@app.route("/wrong_ans")
def wrong_ans():
    return render_template("wrong_Ans.html")

@app.route("/full_anlyz")
def full_ans():
    return render_template("full_analyz.html")

if __name__ =="__main__":
    app.run (host="127.0.1.1",port=8080, debug=True)