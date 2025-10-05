from turtle import right
import ttkbootstrap as tb
from tkinter import *
import sqlite3
import os



class App:
    def __init__(self):
        self.main_window = tb.Window(themename="cosmo")
        self.main_window.geometry("1000x560+500+150")
        self.main_window.title("Notlar")
        self.main_window.resizable(0,0)

        self.first_frame = tb.Frame(self.main_window)
        self.first_frame.pack(fill=X)

        table_scroll_right = Scrollbar(self.first_frame,orient="vertical")
        table_scroll_right.pack(fill=Y,side=RIGHT)

        table_scroll_bottom = Scrollbar(self.first_frame,orient="horizontal")
        table_scroll_bottom.pack(fill=X,side=BOTTOM)

        self.tvw = tb.Treeview(
            self.first_frame,height=15,bootstyle="primary",show="headings",
            yscrollcommand=table_scroll_right.set,
            xscrollcommand=table_scroll_bottom.set
            )
        self.tvw.pack(fill=X,pady=5,padx=5)

        self.tvw.bind("<ButtonRelease-1>",self.selectItem)

        table_scroll_right.config(command=self.tvw.yview)
        table_scroll_bottom.config(command=self.tvw.xview)

        self.tvw["columns"] =("id","durum","baslik","not")
        self.tvw["displaycolumns"] = ("durum","baslik","not")

        self.tvw.column("durum",width=30,stretch=False)
        self.tvw.column("baslik",width=250,stretch=False)
        self.tvw.column("not",width=1685,stretch=False)

        self.tvw.heading("durum",text="",anchor="w")
        self.tvw.heading("baslik",text="Başlık",anchor="w")
        self.tvw.heading("not",text="Not",anchor="w")

        self.tvw.tag_configure("yapildi",background="lightgreen")
        self.tvw.tag_configure("yapilmadi",background="white")

        if not os.path.exists("notes.db"):
            self.db_create()
            self.get_db()
        else:
            self.get_db()

        self.last_frame = tb.LabelFrame(self.main_window,text="Not Ekle",bootstyle="primary")
        self.last_frame.pack(fill=X,padx=5)

        self.baslik_label = tb.Label(self.last_frame,text="Başlık",bootstyle="info")
        self.baslik_label.pack(anchor="w",padx=10)
        self.baslik_entry = tb.Entry(self.last_frame)
        self.baslik_entry.pack(anchor="w",padx=10,fill=X)

        self.not_label = tb.Label(self.last_frame,text="Not",bootstyle="info")
        self.not_label.pack(anchor="w",padx=10)
        self.not_entry = tb.Entry(self.last_frame)
        self.not_entry.pack(anchor="w",padx=10,fill=X,pady=(0,5))

        self.add_button = tb.Button(self.last_frame,text="Ekle",bootstyle="success",command=self.add_note)
        self.add_button.pack(anchor="w",side="left",padx=10,pady=5)
        self.del_button = tb.Button(self.last_frame,text="Sil",bootstyle="success",command=self.del_note)
        self.del_button.pack(anchor="w",side="left",padx=10,pady=5)
        self.edit_button = tb.Button(self.last_frame,text="Güncelle",bootstyle="success",command=self.edit_note)
        self.edit_button.pack(anchor="w",side="left",padx=10,pady=5)
        self.clear_button = tb.Button(self.last_frame,text="Temizle",bootstyle="success",command=self.clear_entry)
        self.clear_button.pack(anchor="w",side="left",padx=10,pady=5)
        self.done_button = tb.Button(self.last_frame,text="Durum",bootstyle="success",command=self.done_note)
        self.done_button.pack(anchor="w",side="right",padx=10,pady=5)

        self.main_window.mainloop()

    def selectItem(self,e):
        self.selected_item = self.tvw.focus()
        item = self.tvw.item(self.selected_item)["values"]
        self.baslik_entry.delete(0,END)
        self.not_entry.delete(0,END)
        self.baslik_entry.insert(0,item[2])
        self.not_entry.insert(0,item[3])

    def add_note(self):
        durum = ''
        baslik = self.baslik_entry.get()
        note = self.not_entry.get()

        note_id = self.add_db(baslik,note)
        self.tvw.insert("",END, values=(note_id,durum,baslik,note),tags="yapilmadi")

        self.clear_entry()   

    def del_note(self):
        self.selected_item = self.tvw.focus()
        values = self.tvw.item(self.selected_item, "values")
        note_id = int(values[0])

        self.del_db(note_id)
        self.tvw.delete(self.selected_item)

        self.clear_entry()
    
    def edit_note(self):
        self.selected_item = self.tvw.focus()
        baslik = self.baslik_entry.get()
        note = self.not_entry.get()
        values = self.tvw.item(self.selected_item, "values")
        note_id = int(values[0])
        durum_icon = values[1]

        self.edit_db(note_id,baslik,note)
        self.tvw.item(self.selected_item,text="",values=(note_id,durum_icon,baslik,note))

        self.clear_entry()

    def done_note(self):
        self.selected_item = self.tvw.focus()
        baslik = self.baslik_entry.get()
        note = self.not_entry.get()
        values = self.tvw.item(self.selected_item,"values")
        note_id = int(values[0])
        durum_icon = values[1]

        self.done_db(note_id)
        if durum_icon == '':
            durum_icon = '✔'
            self.tvw.item(self.selected_item,text="",values=(note_id,durum_icon,baslik,note),tags="yapildi")
            self.clear_entry()
        else:
            durum_icon = ''
            self.tvw.item(self.selected_item,text="",values=(note_id,durum_icon,baslik,note),tags="yapilmadi")
            self.clear_entry()

    def clear_entry(self):
        self.baslik_entry.delete(0,END)
        self.not_entry.delete(0,END)
        
        
    def db_connect(self):
        self.connection = sqlite3.connect("notes.db")
        self.cursor = self.connection.cursor()
    
    def db_create(self):
        self.db_connect()
        self.cursor.execute("""CREATE TABLE notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        durum INTEGER DEFAULT 0,
        title TEXT,
        note TEXT
        )""")

    def get_db(self):
        self.db_connect()
        sql = "SELECT * FROM notes"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        for i in results:
            if i[3] == 1:
                durum_icon = '✔'
                self.tvw.insert("",END,values=(i[0],durum_icon,i[1],i[2]),tags="yapildi")
            else:
                durum_icon = ''
                self.tvw.insert("",END,values=(i[0],durum_icon,i[1],i[2]),tags="yapilmadi")
        self.connection.close()
    
    def add_db(self,baslik,note):
        self.db_connect()
        sql = "INSERT INTO notes(title,note) VALUES (?,?)"
        values = (baslik,note)
        self.cursor.execute(sql,values)
        self.connection.commit()
        note_id = self.cursor.lastrowid
        self.connection.close()
        return note_id
    
    def del_db(self,id):
        self.db_connect()
        sql = "DELETE FROM notes WHERE id=?"
        values = (id,)
        self.cursor.execute(sql,values)
        self.connection.commit()
        self.connection.close()

    def edit_db(self,id,baslik,note):
        self.db_connect()
        sql = "UPDATE notes SET title=?,note=? WHERE id=?"
        values = (baslik,note,id)
        self.cursor.execute(sql,values)
        self.connection.commit()
        self.connection.close()

    def done_db(self,id):
        self.db_connect()
        self.cursor.execute("SELECT durum FROM notes WHERE id=?",(id,))
        mevcut_durum = self.cursor.fetchone()[0]
        if mevcut_durum == 1:
            yeni_durum = 0
        else:
            yeni_durum = 1
        sql = "UPDATE notes SET durum=? WHERE id=?"
        values = (yeni_durum,id)
        self.cursor.execute(sql,values)
        self.connection.commit()
        self.connection.close()
                

app = App()