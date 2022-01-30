import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json
import pandas as pd

class ExerciseData():
    
    class Data():
        def __init__(self,row,indexes):
            self.ID = row[indexes["ID"]]
            self.descriptor = row[indexes["Descriptor"]]
            self.type = row[indexes["Type"]]
            self.category = row[indexes["Category"]]
            self.difficulty = row[indexes["Difficulty"]]
            self.categoryobj = ""

    class CategoriesData():
        def __init__(self,row,indexes):
            self.ID = row[indexes["ID"]]
            self.category = row[indexes["Category"]]
            self.exerciseobjects={}
        
        def linkexercisedata(self,exercisedata):
            for exercise in exercisedata:
                if exercisedata[exercise].category==self.ID:
                    exercisedata[exercise].categoryobj=self
                    self.exerciseobjects[exercisedata[exercise].ID]=exercisedata[exercise]


    def __init__(self):
        self.exercisefile = pd.read_csv("exercisedatabase.csv")
        self.exercisefile = self.exercisefile.fillna('') #replace empty fields (which would normally show NaN) with ""
        self.exercisedata={}

        indexes = {}
        for l,header in enumerate(list(self.exercisefile)): #list(customer_df) returns all headings
            indexes[header]=l
        for i,row in self.exercisefile.iterrows():
            exercisedata_obj = self.Data(row,indexes)
            self.exercisedata[exercisedata_obj.ID]=exercisedata_obj

        self.categoriesfile = pd.read_csv("categoriesdatabase.csv")
        self.categoriesfile = self.categoriesfile.fillna('') #replace empty fields (which would normally show NaN) with ""
        self.categoriesdata={}
        categoriesindexes = {}
        for l,header in enumerate(list(self.categoriesfile)): #list(customer_df) returns all headings
            categoriesindexes[header]=l
        for i,row in self.categoriesfile.iterrows():
            exercisedata_obj = self.CategoriesData(row,categoriesindexes)
            exercisedata_obj.linkexercisedata(self.exercisedata)
            self.categoriesdata[exercisedata_obj.ID]=exercisedata_obj


class CustomerData():
    
    class Data():
        def __init__(self,row,indexes,pandas_data, pandas_index):
            self.pandas_index=pandas_index
            self.pandas_data=pandas_data
            self.name = row[indexes["Name"]]
            self.DoB = row[indexes["DoB"]]
            self.goals = row[indexes["Goals"]]
            self.email = row[indexes["Email"]]
            self.ID = row[indexes["ID"]]
            self.ability_level = row[indexes["Ability Level"]]

            self.categories_string = row[indexes["Categories"]]
            if self.categories_string != "":self.categories = json.loads(row[indexes["Categories"]])
            else:self.categories=[]

        def writetofile(self):
            print("i got here")
            print(str(self.categories))
            self.pandas_data.at[self.pandas_index,"Name"]=self.name
            self.pandas_data.at[self.pandas_index,"DoB"]=self.DoB
            self.pandas_data.at[self.pandas_index,"Goals"]=self.goals
            self.pandas_data.at[self.pandas_index,"Email"]=self.email
            self.pandas_data.at[self.pandas_index,"Categories"]=str(self.categories)
            self.pandas_data.to_csv("tempdata1.csv", index=False)

    def __init__(self):
        self.customer_file = pd.read_csv("tempdata1.csv")
        self.customer_file = self.customer_file.fillna('') #replace empty fields (which would normally show NaN) with ""
        self.customer_file['DoB'] = pd.to_datetime(self.customer_file['DoB'], dayfirst=True, errors='coerce')

        indexes={}
        for l,header in enumerate(list(self.customer_file)): #list(customer_df) returns all headings
            indexes[header]=l

        self.customerdata = {}
        # loop through each row of datastructure
        for i,row in self.customer_file.iterrows():
            customer_obj = self.Data(row,indexes,self.customer_file, i)
            self.customerdata[customer_obj.ID]=customer_obj




class Customers():
    def __init__(self, id, name, DoB, goals, email, ability_level, pandas_index):
        self.id = id
        self.name = name
        self.DoB = DoB
        self.goals = goals
        self.email = email
        self.ability_level=ability_level
        self.pandas_index = pandas_index

        #ability_level_groups=["Bicep Curls","Forward Lunge","Sit-Ups","Burpees","Deadlifts","Lateral Raises","Calf Raises"]
        #ability_level=json.loads(ability_level)
        #self.ability_levels=ability_level
        print(self.ability_level)
    
    '''
    FUNCTION: Add a set of tkinter textbox objects to each contract. Used to access the value of any changes the user has typed into those textboxes
    '''
    def add_table_row(self, name_textbox,DoB_textbox,goals_textbox,email_textbox):
        self.name_textbox=name_textbox
        self.DoB_textbox=DoB_textbox
        self.goals_textbox=goals_textbox
        self.email_textbox=email_textbox
    

    def edit_customer_data_button(self, customer_page,i):
            self.edit_info_button = ttk.Button(customer_page.frame, text='Edit Goals')
            self.edit_info_button.grid(row=i+2,column=4, padx=50)

    '''
    FUNCTION: To check whether any of the textboxes contain difference values from what is currently stored in the object
                if changes are found, then update the customer
    '''
    def check_difference(self):
        error_msg = ""
        changed = False
        items_changed = []
        
        # check whether current name value is different from what is in the textbox
        if self.name != self.name_textbox.get():
            changed = True
            self.name=self.name_textbox.get()
            items_changed.append("Name")
        
        # same as above, however the date field requires a validity check
        try:
            if changed==False and self.DoB != datetime.strptime(self.DoB_textbox.get(), '%d/%m/%Y'):
                changed = True
                self.DoB=datetime.strptime(self.DoB_textbox.get(), '%d/%m/%Y')
                items_changed.append("DoB")
        except Exception as e:
            error_msg+=f"{self.name}: date field is invalid\n"

        if changed==False and self.goals != self.goals_textbox.get():
            changed = True
            self.goals=self.goals_textbox.get()
            items_changed.append("Goals")
        if changed==False and self.email != self.email_textbox.get():
            changed = True
            self.email=self.email_textbox.get()
            items_changed.append("Email")
        
        return error_msg,items_changed


    '''
    Function: Read customer data from temporary CSV file (which is downloaded and later uploaded to the cloud). Create the table on the TKinter page
    IN:
    - self
    OUT:
    - customer_df: the pandas datastructure containing customer data
    - table_array: a 2D array of all the text boxes in the grid on the tkinter window
    '''
    def read_customer_data(self):

        indexes = {}
        # print all the headers across the screen at the top (will reference each column in the table created below)
        for l,header in enumerate(list(self.controller.customer_df)): #list(customer_df) returns all headings
            indexes[header]=l

        for g, heading in enumerate(["Name","Date Of Birth","Goals","Email"]):
            col_heading = tk.Label(self.frame, text=heading, bg=self.controller.backgroundColor, fg='black', font=self.controller.p1)
            if g==0:col_heading.grid(row=1,column=g, padx=(10,0), pady=(10,0), sticky="w")
            else:col_heading.grid(row=1,column=g, pady=(10,0), sticky="w")

        customers = {}
        table_array = []
        # loop through each row of datastructure
        for i,values in self.controller.customer_df.iterrows():

            name = values[indexes["Name"]]
            DoB = values[indexes["DoB"]]
            goals = values[indexes["Goals"]]
            email = values[indexes["Email"]]
            id = values[indexes["ID"]]
            ability_level = values[indexes["Ability Level"]]

            c = Customers(id,name,DoB,goals,email,ability_level,i)
            customers[id]=c

            self.name_textbox = tk.Entry(self.frame, width=20, fg='blue',font=("Arial",16,"bold"))
            self.name_textbox.insert(tk.END, name)
            self.name_textbox.grid(row=i+2,column=0, padx=(10,0))
            self.DoB_textbox = tk.Entry(self.frame, width=20, fg='blue',font=("Arial",16,"bold"))
            self.DoB_textbox.insert(tk.END, f'{DoB.day}/{DoB.month}/{DoB.year}')
            self.DoB_textbox.grid(row=i+2,column=1)
            self.goals_textbox = tk.Entry(self.frame, width=20, fg='blue',font=("Arial",16,"bold"))
            self.goals_textbox.insert(tk.END, goals)
            self.goals_textbox.grid(row=i+2,column=2)
            self.email_textbox = tk.Entry(self.frame, width=20, fg='blue',font=("Arial",16,"bold"))
            self.email_textbox.insert(tk.END, email)
            self.email_textbox.grid(row=i+2,column=3)

            c.edit_customer_data_button(self,i)

            c.add_table_row(self.name_textbox,self.DoB_textbox,self.goals_textbox,self.email_textbox)

            table_array.append([self.name_textbox,self.DoB_textbox,self.goals_textbox,self.email_textbox])

        return customers
