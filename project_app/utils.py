from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import matplotlib.pyplot as plt
from config import right_ans_save,wrong_ans_save,full_save,upload_save,pie_image_dir,not_found_img
import os


class Section_Analyze():
    
    def Soup(self,html):
        soup  = BeautifulSoup(html,"html.parser")
        site_url = "https://cdn.digialm.com/"
        src_elements = soup.find_all(src=True)
        for elments in src_elements:
            elments['src'] = urljoin(site_url, elments['src'])
        return soup
    
    def Student_info(self,html):
        link = self.Soup(html)
        main_info = link.find(class_ = 'main-info-pnl')
        table = main_info.find('table')
        candiate_info = [i.text for i in (table.find_all('tr',limit=6))]
        table_index = [candiate_info[i] for i in range(0,len(candiate_info),2)]
        table_cont = [candiate_info[i] for i in range(1,len(candiate_info),2)]
        data = dict(zip(table_index,table_cont))
        df = pd.DataFrame(data=list(data.values()),index=list(data.keys()),columns=['Student_Information'])
        df_html  = df.to_html(classes='table table-striped', index=False)
        return df_html


    def total_marks(self,data):
    # choosen options
        
        total_que = len(data.find_all(class_ = 'questionPnlTbl'))
        choosen_option = []
        co_data = data.find_all(string= 'Chosen Option :')
        for i in range (len(co_data)):
            num = co_data[i].find_next(class_ = 'bold').text
            choosen_option.append(num)

        # now calculating total marks
        c = 0
        right_Ans = data('td', class_ = 'rightAns')
        list_range = [total_que, len(right_Ans)]
        list_range.sort()
        for i in range (list_range[0]):
            if right_Ans[i].text[0] == choosen_option[i]:
                c +=1
            right_que = c
            total_obt_marks = c * 2
        return total_obt_marks,right_que

    def minus_marks(self,data):
        #now finiding is there any minus marks 
        minus_marks_list = []
        min_soup = data.find_all(string ='Marks :')
        for i in range (len(min_soup)):
            min_num = min_soup[i].find_next(class_ = 'bold').text
            if min_num != '2':
                minus_marks_list.append(min_num)
        minus_marks = sum([float(i) for i in minus_marks_list])
        return minus_marks

    def final_marks(self,data):
        #final marks after dedcting minus marks
        obt_marks = self.total_marks(data)[0] + self.minus_marks(data)
        return obt_marks

    def wrong_que(self,data):
        total_que = len(data.find_all(class_ = 'questionPnlTbl'))
        wrong_que = total_que - self.total_marks(data)[1]
        return wrong_que

    def handle_sections(self,data):
        #creating sections
        sections_data = data.find_all('div',class_ = 'section-cntnr')
        sections_list = [i.text for i in (data.find_all('span',class_='bold'))]
        total_sections = len(sections_list)
        return sections_data,sections_list, total_sections
    
    def Analyzing_section(self,data):
        sop_data = self.Soup(data)
        sections_data, sections_list, total_sections = self.handle_sections(sop_data)
        sec_tot_que = [len(sections_data[i].find_all(class_ = 'questionPnlTbl')) for i in range(len(sections_data))]
        sect_dict = {}
        for i in range(total_sections):
            right_ans = self.total_marks(sections_data[i])[1]
            final_mark = self.final_marks(sections_data[i])
            wrong_ans = self.wrong_que(sections_data[i])
            total_sec_que = sec_tot_que[i]
            sect_dict.update({sections_list[i]:[total_sec_que,right_ans,wrong_ans,final_mark]})
        return sect_dict
    
    def pie_diagram(self,column,df):
        fig, ax = plt.subplots()
        ax.pie(df[column],labels=list(df.index),autopct='%1.1f%%')
        ax.axis('equal')
        image_name = column+".jpeg"
        plt.title(image_name)
        print(image_name)
        image_path = os.path.join(pie_image_dir,image_name)
        plt.savefig(image_path,bbox_inches='tight')
    
    def Dataframe(self,data):
        df = pd.DataFrame(self.Analyzing_section(data=data))
        df.index = ['Total Que','Right Ans','Wrong Ans','Marks obtained']
        table_html = df.to_html(classes='table table-striped')
        marks_obt = sum(df.loc(axis=0)['Marks obtained'])
        marks_only = df.loc(axis=0)[['Right Ans','Wrong Ans']]
        for i in list(marks_only.columns):
            self.pie_diagram(i,marks_only)
        return table_html,marks_obt
            
    def Ans_Analyze(self,data):
            sop_data = self.Soup(data)
            que = sop_data.find_all('div',class_='question-pnl')
            l_right = []
            l_wrng = []
            for i in range(100):
                qns = que[i]
                r_a = qns.find(class_='rightAns')
                co_soup = sop_data.find_all(string= 'Chosen Option :')
                g_a = co_soup[i].find_next(class_ = 'bold').text
                if r_a == None:
                    r_a = g_a = co_soup[i].find_next(class_ = 'bold')
                menu_tbl = qns.find_all(class_='menu-tbl')
                if r_a.text[0] == g_a:
                    for j in menu_tbl:
                        j['style'] = 'float: right; margin-bottom: 5px; margin-top: 5px; width: 29%; background-color: green;'
                    l_right.append(qns)

                else:
                    for k in menu_tbl:
                        k['style'] = 'float: right; margin-bottom: 5px; margin-top: 5px; width: 29%; background-color: red;'
                    l_wrng.append(qns)

            styles = []

            # Extract styles from inline style attributes
            for tag in sop_data.find_all(style=True):
                styles.append(tag['style'])

            # Extract styles from style tags
            for style_tag in sop_data.find_all('style'):
                styles.append(style_tag.string)

            css_data = " ".join(styles)

            right = ""
            wrong = ""
            
            for i in l_right:
                data_right = str(i)
                right += "\n" + data_right + "\n"

            with open(right_ans_save,'w',encoding='utf-8') as f:
                f.write("<style>"+css_data+ "</style>"+ right + "<b><a href='/'>GO BACK TO HOME</a></b>" + "<p> <a href= '/wrong_ans'> Wrong Answers </a></p>")
            
            for j in l_wrng:
                data_wrng = str(j)
                wrong += "\n" + data_wrng + "\n"
            
            with open(wrong_ans_save,'w',encoding='utf-8') as f:
                f.write( "<style>"+css_data+ "</style>" + wrong + "<b><a href='/'>GO BACK TO HOME</a></b>" + "<p> <a href= '/right_ans'> Right Answers </a></p>")
            
            with open(full_save,'w',encoding='utf-8') as f:
                f.write("<b><a href='/'>GO BACK TO HOME</a></b>" + "<p> <a href= '/right_ans'> Right Answers </a></p>"+ sop_data.decode_contents())
                
            return ("Successful" * 10)
    
    def remove_files(self,file):
        if os.path.exists(file):
            return os.remove(file)

    def Empty_folder(self):
        img_list = os.listdir(pie_image_dir)
        img_paths = [os.path.join(pie_image_dir,i) for i in img_list]

        [self.remove_files(i) for i in img_paths]
        [self.remove_files(i) for i in [right_ans_save,wrong_ans_save,full_save,upload_save]]
        return "Successfully empty"

    

        