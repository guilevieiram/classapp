from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
import numpy as np
import sqlite3
import smtplib
from email.message import EmailMessage
import os

'''
this is a git test to figure out things
'''

class App():

    def __init__(self, root, db_name):
        
        self.root = root
        self.root.geometry('+%d+%d'%(50,50))
        self.root.title("Recipe Classification")
        self.font = 'Nunito'
        self.color = '#eb4034'
        self.color_light = '#f28c85'
        self.connection = sqlite3.connect(db_name)
        self.table = ''
        self.db = db_name

        self.user = None
        self.user_list = None

        self.method_id = 0
        self.badge = ''

        self.width = 1100

        self.tech_btn = {}


    # public backend methods
    def import_data(self, folder_name='data'):
        self.techniques_df = pd.read_pickle(folder_name + '/techniques')
        self.methods_df = pd.read_pickle(folder_name + '/methods')
        self.badges_df = pd.read_pickle(folder_name + '/badges')
        self.recipes_df = pd.read_pickle(folder_name + '/recipes')

    def create_table(self, table_name='class_methods'):
        self.table = table_name
        c = self.connection.cursor()

        sql = "CREATE TABLE IF NOT EXISTS " + table_name + " ("
        sql += " user, method_id, description, "
        sql += ','.join(list('"' + self.techniques_df['name'] + '"'))
        sql += ")"

        c.execute(sql)
        self.connection.commit()
        pass

    def set_user(self, user):
        self.user = user
    
    def set_user_list(self, user_list):
        self.user_list = user_list

    def set_starting_method_id(self):
        c = self.connection.cursor()

        sql = "SELECT count(*) FROM " + self.table
        sql += " WHERE user == '" + self.user + "'"
        c.execute(sql)
        number_of_lines = (c.fetchall())[0][0]

        if number_of_lines == 0:
            index = self.user_list.index(self.user)
            start = 200 * index
        else:
            sql = "SELECT method_id FROM " + self.table
            sql += " WHERE user == '" + self.user + "'"
            c.execute(sql)
            list = c.fetchall()
            list = [element[0] for element in list]
            max_method_index = max(list)
            start = max_method_index + 1

        self.method_id = start


    # public frontend methods
    def create_header(self):
        self.header = Frame(self.root, width = self.width, height=120, bg='white')
        self.header.grid(columnspan=10, rowspan=2, row=0)

        path = r'data/cuukin_icon.png'
        self._create_logo(path)

        logo_text = Label(self.root, text='Cuukin', font = (self.font,24, "bold"), fg = self.color , bg = 'white')
        logo_text.grid(column=1, row=0, rowspan = 2, columnspan=2,  sticky=W)
        
        program_name = Label(self.root, text='Recipes Classification', font = (self.font,24,'bold'), fg = self.color , bg = 'white')
        program_name.grid(column=5, row=0, columnspan=4, rowspan=2, sticky=E)

    def create_recipe_bar(self):

        recipe_name = self.recipes_df['title'][self.methods_df.at[self.method_id,'recipe_id']]

        self.recipe_bar = Frame(self.root, width = self.width, height=80, bg='white')
        self.recipe_bar.grid(columnspan=10, rowspan=1, row=2)

        recipe_text = Label(self.root, text='Recipe:', font = (self.font,14, 'bold'), fg = self.color , bg = 'white')
        recipe_text.grid(column=0, row=2)

        self._recipe_name = StringVar()
        self._recipe_name.set(recipe_name)
        recipe_name = Label(self.root, textvariable=self._recipe_name, font = (self.font,12), bg = 'white')
        recipe_name.grid(column=1, row=2, columnspan= 4)

        method_id_text = Label(self.root, text='Method Id:', font = (self.font,14, 'bold'), fg = self.color , bg = 'white')
        method_id_text.grid(column=8, row=2, columnspan =2)
        
        self._method_id_name = StringVar()
        self._method_id_name.set(str(self.method_id))
        method_id_name = Label(self.root, textvariable=self._method_id_name, font = (self.font,12), bg = 'white')
        method_id_name.grid(column=9, row=2)

    def create_classification_columns(self):

        self.titles = Frame(root, width = self.width, height=30, bg='white')
        self.titles.grid(columnspan=10, rowspan=1, row=3)

        description_title = Label(self.root, text='Description:', font = (self.font,14), fg = self.color , bg = 'white')
        description_title.grid(column=0, row=3, columnspan=2, sticky=W, padx=20)

        bagdes_title = Label(self.root, text='Badges:', font = (self.font,14), fg = self.color , bg = 'white')
        bagdes_title.grid(column=2, row=3, columnspan=3, sticky=W, padx=20)

        techniques_title = Label(self.root, text='Techniques:', font = (self.font,14), fg = self.color , bg = 'white')
        techniques_title.grid(column=6, row=3, columnspan=2) 

        self.body = Frame(self.root, width = self.width, height=300, bg='white')
        self.body.grid(columnspan=10, rowspan=13, row=4)

        self._create_description_column()

        self._create_badges_column()
    
    def create_buttons(self, row = 16):

        self.navigation = Frame(self.root, width = self.width, height=20, bg='white')
        self.navigation.grid(columnspan=10, rowspan=1, row=row)

        exit_text =  StringVar()
        exit_btn = Button(self.root, textvariable=exit_text, font=(self.font,10), bg=self.color, fg='white',
                                height=1, width=15, borderwidth = 0,
                                command=lambda : self._exit())
        exit_text.set("Save and Exit")
        exit_btn.grid(column=0, row=row)

        next_text =  StringVar()
        next_btn = Button(self.root, textvariable=next_text, font=(self.font,10), bg=self.color, fg='white',
                                height=1, width=10, borderwidth = 0,
                                command=lambda n=1: self._increment_method_id(n))
        next_text.set("Next")
        next_btn.grid(column=9, row=row)

        prev_text =  StringVar()
        prev_btn = Button(self.root, textvariable=prev_text, font=(self.font,10), bg=self.color, fg='white',
                                height=1, width=10, borderwidth = 0,
                                command=lambda n=-1: self._increment_method_id(n))
        prev_text.set("Previous")
        prev_btn.grid(column=8, row=row)

        send_text =  StringVar()
        send_btn = Button(self.root, textvariable=send_text, font=(self.font,10), bg=self.color, fg='white',
                                height=1, width=15, borderwidth = 0,
                                command=lambda : self._send_result())
        send_text.set("Send results to Gui")
        send_btn.grid(column=1, row=row, columnspan=2)


    # private backend methods
    def _show_table(self, table_name='class_methods'):
        sql = "SELECT * FROM " + table_name
        df = pd.read_sql_query(sql, self.connection)
        print(df.head(10))

    def _close_connection(self):
        self.connection.commit()
        self.connection.close()

    def _submit_classification(self, technique, table_name='class_methods'):
        c = self.connection.cursor()

        technique = technique.replace(" ","_")

        techniques_list = list(self.techniques_df['name'])
        techniques_binary_dict = dict((tech.replace(" ","_"), 0) for tech in techniques_list)
        techniques_binary_dict[technique] = 1
        techniques_binary_dict['method_id'] = self.method_id
        techniques_binary_dict['description'] = self.methods_df.at[self.method_id, 'description']
        techniques_binary_dict['user'] = self.user

        columns = ','.join(['"' + tech + '"' for tech in techniques_list])
        place_holder = ','.join([':' + tech.replace(" ","_")  for tech in techniques_list])
        sql = "INSERT INTO " + table_name + " (user, method_id, description, "
        sql += columns + ") VALUES (:user, :method_id, :description, " + place_holder + ")"

        c.execute(sql, techniques_binary_dict)
        self.connection.commit()


    # private frontend methods
    def _create_description_column(self, column=0, row=4):
        description =  self.methods_df.at[self.method_id, 'description']

        self.description_window = Text(self.root, font=(self.font, 12), width=30, height=15, borderwidth = 0, wrap=WORD)
        self.description_window.insert(1.0,  description)
        self.description_window.grid(column = column, row = row, columnspan=2, rowspan = 10, padx=20, sticky=W)

    def _create_badges_column(self, column=2, row=4):
        badges_list = list(self.badges_df['name'])

        badge_btn = {}
        for badge in badges_list:
            badge_text =  StringVar()
            badge_btn[badge] = Button(self.root, textvariable=badge_text, font=(self.font,10), bg=self.color_light, fg='black',
                                    height=1, width=20, borderwidth = 0, 
                                    command=lambda b=badge: self._update_badge(b))
            badge_text.set(badge)
            badge_btn[badge].grid(column=column, row=row, sticky = E + W, columnspan=3, padx=20)
            row += 1 

    def _update_techniques_list(self, column=6, row=4):
        techniques_list = list(self.techniques_df[self.techniques_df['badge_name']==self.badge]['name'])
        techniques_num = len(techniques_list)

        for key in self.tech_btn.keys():
            self.tech_btn[key].destroy()

        for technique in techniques_list:
            tech_text = StringVar()
            self.tech_btn[technique] = Button(self.root, textvariable=tech_text, font=(self.font,10), bg=self.color_light, fg='black',
                                height=1, width=13, borderwidth = 0, 
                                command=lambda t=technique: self._update_technique(t))
            tech_text.set(technique)       

        # make buttons in a 3 column shape automatically by reshaping numpy array

        num_missing_spots = 3 - techniques_num % 3
        for i in range(num_missing_spots): techniques_list.append('')
        tech_array = np.array(techniques_list)
        tech_array = tech_array.reshape((-1,3))

        index = 0

        for y in range(tech_array.shape[0]):
            for x in range(tech_array.shape[1]):
                if index == techniques_num: break
                self.tech_btn[techniques_list[index]].grid(column= column + x, row = row + y, columnspan=2)
                index += 1

    def _create_logo(self, path):

        logo = Image.open(path)
        logo.resize((5,5), Image.ANTIALIAS)
        logo = ImageTk.PhotoImage(logo)
        logo_label = Label(image=logo)
        logo_label.image = logo
        logo_label.grid(column = 0, row = 0, rowspan=2, sticky=N)

    def _clear_techniques_table(self):
        for key in self.tech_btn.keys():
            self.tech_btn[key].destroy()

    def _update(self):
        description =  self.methods_df.at[self.method_id, 'description']
        recipe_name = self.recipes_df['title'][self.methods_df.at[self.method_id,'recipe_id']]
        
        self._method_id_name.set(str(self.method_id))
        self._recipe_name.set(recipe_name)

        self.description_window.delete(1.0, END)
        self.description_window.insert(1.0,  description)


# buttons actions methods
    def _exit(self):
        #self._show_table()
        self._close_connection()
        self.root.destroy()

    def _increment_method_id(self, number):
        self.method_id += number
        self._update()
    
    def _update_technique(self, technique):
        self._submit_classification(technique)
        self._clear_techniques_table()

    def _update_badge(self, badge):
        self.badge = badge
        self._update_techniques_list()

    def _send_result(self):

        #setup parameters for email
        email_password = os.environ.get('EMAIL_PASSWORD_PYTHON')
        email_address = os.environ.get('EMAIL_USER')

        subject = f'Classapp Data Base [{self.user}]'
        body = f'Here is the classification DB from {self.user}.\n\n'
        body += f'Kind regards,\n\nPython Gui.'

        #getting attachment
        with open(self.db, 'rb') as f:
            file_data = f.read()
            file_name = f.name

        #setting up message
        message = EmailMessage()
        message['Subject'] = subject
        message['From'] = email_address
        message['To'] = email_address

        message.set_content(body)
        message.add_attachment(file_data, maintype='application', subtype='octec-stream', filename=file_name)
        
        #login and send
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_address, email_password)
            smtp.send_message(message)

        # exiting app after email was sent
        self._exit()

# "get user" window
def get_user(user_list):

    '''
    this part of the code is ugly. I am not proud of it but it does the job so who cares???
    '''
    user = []

    def assign_user(event): 
        user.append(drop_down.get())

    user_tab_root = Tk()
    user_tab_root.title("Who's playing?")

    
    canvas = Frame(user_tab_root, width = 300, height=150, bg='white')
    canvas.grid(rowspan=3, row=0)

    question = Label(user_tab_root, text='Select user from list:', font='Nunito' + 'bold' + '20', bg='white', fg = '#eb4034')
    question.grid(column=0, row=0, padx=20, pady=10)

    drop_down = ttk.Combobox(user_tab_root, values = user_list)
    drop_down.grid(column=0, row=1, padx=20, pady=10)   

    drop_down.bind("<<ComboboxSelected>>", assign_user)
    
    exit_button = Button(user_tab_root, text = 'Continue', command=lambda :user_tab_root.destroy(),
                            font=('Nunito',10), bg='#eb4034', fg='white',
                                height=1, width=15, borderwidth = 0)

    exit_button.grid(column=0, row=2, padx=20, pady=10)

    user_tab_root.mainloop()

    return user[0]


# Main Loop
if __name__ == "__main__":

    user_list = ['GV', 'EM', 'FR',  'HC', 'NA', 'RC', 'WZ', 'JF', 'MG']

    user = get_user(user_list)

    root = Tk()
    
    classapp = App(root, 'data.db')

    # DB methods
    classapp.import_data(folder_name='data')
    classapp.create_table(table_name='class_methods')
    classapp.set_user(user)
    classapp.set_user_list(user_list)
    classapp.set_starting_method_id()

    # Design methods
    classapp.create_header()
    classapp.create_recipe_bar()
    classapp.create_classification_columns()
    classapp.create_buttons()

    classapp.root.mainloop()