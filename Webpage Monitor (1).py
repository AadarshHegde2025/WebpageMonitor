from glob import glob
import string
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import messagebox as mb
import tkinter as tk
from tkinter import ttk
import requests
import urllib3
import requests.packages
import time
import hashlib
from urllib.request import urlopen, Request
import collections
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import smtplib
import ssl
import shutil
import platform
import os
from difflib import SequenceMatcher
import threading
import logging
import nltk
from nltk.corpus import stopwords
from nltk.corpus import words
from nltk.tokenize import word_tokenize
import datetime

urllib3.disable_warnings()
# nltk.download('stopwords')

# Table and Scrollbar Framework

OS = platform.system()

class Mousewheel_Support(object): 

    # implemetation of singleton pattern
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, root, horizontal_factor = 2, vertical_factor=2):
        
        self._active_area = None
        
        if isinstance(horizontal_factor, int):
            self.horizontal_factor = horizontal_factor
        else:
            raise Exception("Vertical factor must be an integer.")

        if isinstance(vertical_factor, int):
            self.vertical_factor = vertical_factor
        else:
            raise Exception("Horizontal factor must be an integer.")

        if OS == "Linux" :
            root.bind_all('<4>', self._on_mousewheel,  add='+')
            root.bind_all('<5>', self._on_mousewheel,  add='+')
        else:
            # Windows and MacOS
            root.bind_all("<MouseWheel>", self._on_mousewheel,  add='+')

    def _on_mousewheel(self,event):
        if self._active_area:
            self._active_area.onMouseWheel(event)

    def _mousewheel_bind(self, widget):
        self._active_area = widget

    def _mousewheel_unbind(self):
        self._active_area = None

    def add_support_to(self, widget=None, xscrollbar=None, yscrollbar=None, what="units", horizontal_factor=None, vertical_factor=None):
        if xscrollbar is None and yscrollbar is None:
            return

        if xscrollbar is not None:
            horizontal_factor = horizontal_factor or self.horizontal_factor

            xscrollbar.onMouseWheel = self._make_mouse_wheel_handler(widget,'x', self.horizontal_factor, what)
            xscrollbar.bind('<Enter>', lambda event, scrollbar=xscrollbar: self._mousewheel_bind(scrollbar) )
            xscrollbar.bind('<Leave>', lambda event: self._mousewheel_unbind())

        if yscrollbar is not None:
            vertical_factor = vertical_factor or self.vertical_factor

            yscrollbar.onMouseWheel = self._make_mouse_wheel_handler(widget,'y', self.vertical_factor, what)
            yscrollbar.bind('<Enter>', lambda event, scrollbar=yscrollbar: self._mousewheel_bind(scrollbar) )
            yscrollbar.bind('<Leave>', lambda event: self._mousewheel_unbind())

        main_scrollbar = yscrollbar if yscrollbar is not None else xscrollbar
        
        if widget is not None:
            if isinstance(widget, list) or isinstance(widget, tuple):
                list_of_widgets = widget
                for widget in list_of_widgets:
                    widget.bind('<Enter>',lambda event: self._mousewheel_bind(widget))
                    widget.bind('<Leave>', lambda event: self._mousewheel_unbind())

                    widget.onMouseWheel = main_scrollbar.onMouseWheel
            else:
                widget.bind('<Enter>',lambda event: self._mousewheel_bind(widget))
                widget.bind('<Leave>', lambda event: self._mousewheel_unbind())

                widget.onMouseWheel = main_scrollbar.onMouseWheel

    @staticmethod
    def _make_mouse_wheel_handler(widget, orient, factor = 1, what="units"):
        view_command = getattr(widget, orient+'view')
        
        if OS == 'Linux':
            def onMouseWheel(event):
                if event.num == 4:
                    view_command("scroll",(-1)*factor, what)
                elif event.num == 5:
                    view_command("scroll",factor, what) 
                
        elif OS == 'Windows':
            def onMouseWheel(event):        
                view_command("scroll",(-1)*int((event.delta/120)*factor), what) 
        
        elif OS == 'Darwin':
            def onMouseWheel(event):        
                view_command("scroll",event.delta, what)
        
        return onMouseWheel

class Scrolling_Area(Frame, object):

    def __init__(self, master, width=None, anchor=N, height=None, mousewheel_speed = 2, scroll_horizontally=True, xscrollbar=None, scroll_vertically=True, yscrollbar=None, outer_background=None, inner_frame=Frame, **kw):
        Frame.__init__(self, master, class_=self.__class__)

        if outer_background:
            self.configure(background=outer_background)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._width = width
        self._height = height

        self.canvas = Canvas(self, background=outer_background, highlightthickness=0, width=width, height=height)
        self.canvas.grid(row=0, column=0, sticky=N+E+W+S)

        if scroll_vertically:
            if yscrollbar is not None:
                self.yscrollbar = yscrollbar
            else:
                self.yscrollbar = Scrollbar(self, orient=VERTICAL)
                self.yscrollbar.grid(row=0, column=1,sticky=N+S)
        
            self.canvas.configure(yscrollcommand=self.yscrollbar.set)
            self.yscrollbar['command']=self.canvas.yview
        else:
            self.yscrollbar = None

        if scroll_horizontally:
            if xscrollbar is not None:
                self.xscrollbar = xscrollbar
            else:
                self.xscrollbar = Scrollbar(self, orient=HORIZONTAL)
                self.xscrollbar.grid(row=1, column=0, sticky=E+W)
            
            self.canvas.configure(xscrollcommand=self.xscrollbar.set)
            self.xscrollbar['command']=self.canvas.xview
        else:
            self.xscrollbar = None

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.innerframe = inner_frame(self.canvas, **kw)
        self.innerframe.pack(anchor=anchor)
        
        self.canvas.create_window(0, 0, window=self.innerframe, anchor='nw', tags="inner_frame")

        self.canvas.bind('<Configure>', self._on_canvas_configure)

        Mousewheel_Support(self).add_support_to(self.canvas, xscrollbar=self.xscrollbar, yscrollbar=self.yscrollbar)

    @property
    def width(self):
        return self.canvas.winfo_width()

    @width.setter
    def width(self, width):
        self.canvas.configure(width= width)

    @property
    def height(self):
        return self.canvas.winfo_height()
        
    @height.setter
    def height(self, height):
        self.canvas.configure(height = height)
        
    def set_size(self, width, height):
        self.canvas.configure(width=width, height = height)

    def _on_canvas_configure(self, event):
        width = max(self.innerframe.winfo_reqwidth(), event.width)
        height = max(self.innerframe.winfo_reqheight(), event.height)

        self.canvas.configure(scrollregion="0 0 %s %s" % (width, height))
        self.canvas.itemconfigure("inner_frame", width=width, height=height)

    def update_viewport(self):
        self.update()

        window_width = self.innerframe.winfo_reqwidth()
        window_height = self.innerframe.winfo_reqheight()
        
        if self._width is None:
            canvas_width = window_width
        else:
            canvas_width = min(self._width, window_width)
            
        if self._height is None:
            canvas_height = window_height
        else:
            canvas_height = min(self._height, window_height)

        self.canvas.configure(scrollregion="0 0 %s %s" % (window_width, window_height), width=canvas_width, height=canvas_height)
        self.canvas.itemconfigure("inner_frame", width=window_width, height=window_height)

class Cell(Frame):
    """Base class for cells"""

# class Data_Cell(Cell):
#     def __init__(self, master, variable, anchor=W, bordercolor=None, borderwidth=1, padx=0, pady=0, background=None, foreground=None, font=None):
#         Cell.__init__(self, master, background=background, highlightbackground=bordercolor, highlightcolor=bordercolor, highlightthickness=borderwidth, bd= 0)

#         self._message_widget = Message(self, textvariable=variable, font=font, background=background, foreground=foreground)
#         self._message_widget.pack(expand=True, padx=padx, pady=pady, anchor=anchor)

class Data_Cell(Cell):
    def __init__(self, master, variable, anchor=W, bordercolor=None, 
             borderwidth=1, padx=0, pady=0, 
             background=None, foreground=None, font=None):
        Cell.__init__(self, master, background=background,highlightbackground=bordercolor, highlightcolor=bordercolor, highlightthickness=borderwidth, bd=0)

        self._message_widget = Label(self, textvariable=variable, 
                                 font=font, background=background,
                                 foreground=foreground,
                                 wraplength=600)
        self._message_widget.pack(expand=True, padx=padx, pady=pady,
                              anchor=anchor)

class Header_Cell(Cell):
    def __init__(self, master, text, bordercolor=None, borderwidth=1, padx=0, pady=0, background=None, foreground=None, font=None, anchor=CENTER, separator=True):
        Cell.__init__(self, master, background=background, highlightbackground=bordercolor, highlightcolor=bordercolor, highlightthickness=borderwidth, bd= 0)
        self.pack_propagate(False)

        self._header_label = Label(self, text=text, background=background, foreground=foreground, font=font)
        self._header_label.pack(padx=padx, pady=pady, expand=True)

        if separator and bordercolor is not None:
            separator = Frame(self, height=2, background=bordercolor, bd=0, highlightthickness=0, class_="Separator")
            separator.pack(fill=X, anchor=anchor)

        self.update()
        height = self._header_label.winfo_reqheight() + 2*padx
        width = self._header_label.winfo_reqwidth() + 2*pady

        self.configure(height=height, width=width)
        
class Table(Frame):
    def __init__(self, master, columns, column_weights=None, column_minwidths=None, height=500, minwidth=20, minheight=20, padx=5, pady=5, cell_font=None, cell_foreground="black", cell_background="white", cell_anchor=W, header_font=None, header_background="white", header_foreground="black", header_anchor=CENTER, bordercolor = "#999999", innerborder=True, outerborder=True, stripped_rows=("#EEEEEE", "white"), on_change_data=None, mousewheel_speed = 2, scroll_horizontally=False, scroll_vertically=True):
        outerborder_width = 1 if outerborder else 0

        Frame.__init__(self,master, bd= 0)

        self._cell_background = cell_background
        self._cell_foreground = cell_foreground
        self._cell_font = cell_font
        self._cell_anchor = cell_anchor
        
        self._stripped_rows = stripped_rows

        self._padx = padx
        self._pady = pady
        
        self._bordercolor = bordercolor
        self._innerborder_width = 1 if innerborder else 0

        self._data_vars = []

        self._columns = columns
        
        self._number_of_rows = 0
        self._number_of_columns = len(columns)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._head = Frame(self, highlightbackground=bordercolor, highlightcolor=bordercolor, highlightthickness=outerborder_width, bd= 0)
        self._head.grid(row=0, column=0, sticky=E+W)

        header_separator = False if outerborder else True

        for j in range(len(columns)):
            column_name = columns[j]

            header_cell = Header_Cell(self._head, text=column_name, borderwidth=self._innerborder_width, font=header_font, background=header_background, foreground=header_foreground, padx=padx, pady=pady, bordercolor=bordercolor, anchor=header_anchor, separator=header_separator)
            header_cell.grid(row=0, column=j, sticky=N+E+W+S)

        add_scrollbars = scroll_horizontally or scroll_vertically
        if add_scrollbars:
            if scroll_horizontally:
                xscrollbar = Scrollbar(self, orient=HORIZONTAL)
                xscrollbar.grid(row=2, column=0, sticky=E+W)
            else:
                xscrollbar = None

            if scroll_vertically:
                yscrollbar = Scrollbar(self, orient=VERTICAL)
                yscrollbar.grid(row=1, column=1, sticky=N+S)
            else:
                yscrollbar = None

            scrolling_area = Scrolling_Area(self, width=self._head.winfo_reqwidth(), height=height, scroll_horizontally=scroll_horizontally, xscrollbar=xscrollbar, scroll_vertically=scroll_vertically, yscrollbar=yscrollbar)
            scrolling_area.grid(row=1, column=0, sticky=E+W)

            self._body = Frame(scrolling_area.innerframe, highlightbackground=bordercolor, highlightcolor=bordercolor, highlightthickness=outerborder_width, bd= 0)
            self._body.pack()
            
            def on_change_data():
                scrolling_area.update_viewport()

        else:
            self._body = Frame(self, height=height, highlightbackground=bordercolor, highlightcolor=bordercolor, highlightthickness=outerborder_width, bd= 0)
            self._body.grid(row=1, column=0, sticky=N+E+W+S)

        if column_weights is None:
            for j in range(len(columns)):
                self._body.grid_columnconfigure(j, weight=1)
        else:
            for j, weight in enumerate(column_weights):
                self._body.grid_columnconfigure(j, weight=weight)

        if column_minwidths is not None:
            for j, minwidth in enumerate(column_minwidths):
                if minwidth is None:
                    header_cell = self._head.grid_slaves(row=0, column=j)[0]
                    minwidth = header_cell.winfo_reqwidth()

                self._body.grid_columnconfigure(j, minsize=minwidth)
        else:
            for j in range(len(columns)):
                header_cell = self._head.grid_slaves(row=0, column=j)[0]
                minwidth = header_cell.winfo_reqwidth()

                self._body.grid_columnconfigure(j, minsize=minwidth)

        self._on_change_data = on_change_data

    def _append_n_rows(self, n):
        number_of_rows = self._number_of_rows
        number_of_columns = self._number_of_columns

        for i in range(number_of_rows, number_of_rows+n):
            list_of_vars = []
            for j in range(number_of_columns):
                var = StringVar()
                list_of_vars.append(var)

                if self._stripped_rows:
                    cell = Data_Cell(self._body, borderwidth=self._innerborder_width, variable=var, bordercolor=self._bordercolor, padx=self._padx, pady=self._pady, background=self._stripped_rows[i%2], foreground=self._cell_foreground, font=self._cell_font, anchor=self._cell_anchor)
                else:
                    cell = Data_Cell(self._body, borderwidth=self._innerborder_width, variable=var, bordercolor=self._bordercolor, padx=self._padx, pady=self._pady, background=self._cell_background, foreground=self._cell_foreground, font=self._cell_font, anchor=self._cell_anchor)

                cell.grid(row=i, column=j, sticky=N+E+W+S)

            self._data_vars.append(list_of_vars)
            
        if number_of_rows == 0:
            for j in range(self.number_of_columns):
                header_cell = self._head.grid_slaves(row=0, column=j)[0]
                data_cell = self._body.grid_slaves(row=0, column=j)[0]
                data_cell.bind("<Configure>", lambda event, header_cell=header_cell: header_cell.configure(width=event.width), add="+")

        self._number_of_rows += n

    def _pop_n_rows(self, n):
        number_of_rows = self._number_of_rows
        number_of_columns = self._number_of_columns
        
        for i in range(number_of_rows-n, number_of_rows):
            for j in range(number_of_columns):
                self._body.grid_slaves(row=i, column=j)[0].destroy()
            
            self._data_vars.pop()
    
        self._number_of_rows -= n

    def Delete(self):
        number_of_columns = self._number_of_columns
        number_of_rows = self._number_of_rows
        for i in range(number_of_rows):
            for j in range(number_of_columns):
                self._body.grid_slaves(row=i, column=j)[0].destroy()
        self._data_vars.pop()
        self._number_of_rows -= 1

    def set_data(self, data):
        n = len(data)
        m = len(data[0])

        number_of_rows = self._number_of_rows

        if number_of_rows > n:
            self._pop_n_rows(number_of_rows-n)
        elif number_of_rows < n:
            self._append_n_rows(n-number_of_rows)

        for i in range(n):
            for j in range(m):
                self._data_vars[i][j].set(data[i][j])

        if self._on_change_data is not None: self._on_change_data()

    def get_data(self):
        number_of_rows = self._number_of_rows
        number_of_columns = self.number_of_columns
        
        data = []
        for i in range(number_of_rows):
            row = []
            row_of_vars = self._data_vars[i]
            for j in range(number_of_columns):
                cell_data = row_of_vars[j].get()
                row.append(cell_data)
            
            data.append(row)
        return data

    @property
    def number_of_rows(self):
        return self._number_of_rows

    @property
    def number_of_columns(self):
        return self._number_of_columns

    def row(self, index, data=None):
        if data is None:
            row = []
            row_of_vars = self._data_vars[index]

            for j in range(self.number_of_columns):
                row.append(row_of_vars[j].get())
                
            return row
        else:
            number_of_columns = self.number_of_columns
            
            if len(data) != number_of_columns:
                raise ValueError("data has no %d elements: %s"%(number_of_columns, data))

            row_of_vars = self._data_vars[index]
            for j in range(number_of_columns):
                row_of_vars[index][j].set(data[j])
                
            if self._on_change_data is not None: self._on_change_data()

    def column(self, index, data=None):
        number_of_rows = self._number_of_rows

        if data is None:
            column= []

            for i in range(number_of_rows):
                column.append(self._data_vars[i][index].get())
                
            return column
        else:            
            if len(data) != number_of_rows:
                raise ValueError("data has no %d elements: %s"%(number_of_rows, data))
            global number_of_columns
            for i in range(number_of_columns):
                self._data_vars[i][index].set(data[i])

            if self._on_change_data is not None: self._on_change_data()

    def clear(self):
        number_of_rows = self._number_of_rows
        number_of_columns = self._number_of_columns

        for i in range(number_of_rows):
            for j in range(number_of_columns):
                self._data_vars[i][j].set("")

        if self._on_change_data is not None: self._on_change_data()

    def delete_row(self, index):
        i = index
        while i < self._number_of_rows:
            row_of_vars_1 = self._data_vars[i]
            row_of_vars_2 = self._data_vars[i+1]

            j = 0
            while j <self.number_of_columns:
                row_of_vars_1[j].set(row_of_vars_2[j])

            i += 1

        self._pop_n_rows(1)

        if self._on_change_data is not None: self._on_change_data()

    def insert_row(self, data, index=END):
        self._append_n_rows(1)

        if index == END:
            index = self._number_of_rows - 1
        
        i = self._number_of_rows-1
        while i > index:
            row_of_vars_1 = self._data_vars[i-1]
            row_of_vars_2 = self._data_vars[i]

            j = 0
            while j < self.number_of_columns:
                row_of_vars_2[j].set(row_of_vars_1[j])
                j += 1
            i -= 1

        list_of_cell_vars = self._data_vars[index]
        for cell_var, cell_data in zip(list_of_cell_vars, data):
            cell_var.set(cell_data)

        if self._on_change_data is not None: self._on_change_data()

    def cell(self, row, column, data=None):
        """Get the value of a table cell"""
        if data is None:
            return self._data_vars[row][column].get()
        else:
            self._data_vars[row][column].set(data)
            if self._on_change_data is not None: self._on_change_data()

    def __getitem__(self, index):
        if isinstance(index, tuple):
            row, column = index
            return self.cell(row, column)
        else:
            raise Exception("Row and column indices are required")
        
    def __setitem__(self, index, value):
        if isinstance(index, tuple):
            row, column = index
            self.cell(row, column, value)
        else:
            raise Exception("Row and column indices are required")

    def on_change_data(self, callback):
        self._on_change_data = callback

if __name__ == "__main__":
    try:
        from tkinter import Tk
    except ImportError:
        from tkinter import Tk


#Instance Variables
url_to_html = dict({})
row_to_url = dict({})
#Call Counter To Delete/Add Row
call = 1
def AddWebsite():
    #Read from file called row number and enter correct row number
    global call
    row_number_mem_location = os.path.dirname(__file__) + "\\row_number.txt"
    website_mem_location = os.path.dirname(__file__) + "\\websites_url.txt"
    html_mem_location = os.path.dirname(__file__) + "\\html_mem.txt"
    #Get Webpage Info And Update Webpage Mem File
    try:
        url2 = input("Enter Website URL: ")
    except:
        print("Can't Hit Add Button Again During Input")
        return
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}
        response3 = requests.get(url2,headers=headers,verify=False)
    except:
        print("Website Does Not Exist or Is Unreachable")
        return
    table._append_n_rows(1)
    r = open(website_mem_location, "a")
    r.write(url2+'\n')
    r.close()
    #Add to Map Variable and Get The HTML for Website
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}
    response = requests.get(url2, headers=headers, verify=False)
    html = process_html(response.text)
    r = open(html_mem_location, "a")
    r.close()
    lines = html.split('\n')
    mystr = '\t'.join([line.strip() for line in lines])
    #mystr = html.replace('\n',"")
    z = open(html_mem_location,"a", encoding="utf-8")
    z.write(mystr+'\n')
    url_to_html[url2] = mystr #Add to map

    
    
    #Update Row Counter in memory
    with open(row_number_mem_location) as f:
        new_row = int(f.read()) + call
        new_row = str(new_row)
    f = open(row_number_mem_location, "w")
    f.write(new_row)
    f.close()
    old_row = int(new_row) - 1

    #Add to row_to_url
    row_to_url[old_row] = url2

    #Set Values in the Table
    table.__setitem__((old_row,0),str(old_row))
    table.__setitem__((old_row,1),url2)
    table.__setitem__((old_row,2),"Unchanged")
    
#Clearing Table
def ConfirmingClear():
    answer = mb.askyesno('Clear Table', 'Are you sure you want to clear table (This action cannot be undone)?')
    global root
    global table
    global row_to_url
    global url_to_html
    if (answer):
        CancelAfter()
        root.destroy()
        root = Tk()
        root.tk.call("source", os.path.dirname(__file__) + "/Azure-ttk-theme-main/azure.tcl")
        root.tk.call("set_theme", "light")
        root.title("Website Monitor")
        
        table = Table(root, ["Row #", "Webpage URL", "Status"], column_minwidths=[80, 600, 100])
        table.pack(padx=10,pady=10,side=LEFT)
        add_webpage = Button(root, text ="Add a Website", command = AddWebsite)
        add_webpage.pack()

        delete_webpage = Button(root, text ="Delete a Website", command = DeleteWebpage)
        delete_webpage.pack()

        notification_method = Button(root,text="Send Test Message to Email", command = SendTest)
        notification_method.pack()
        
        clear_table = Button(root, text="Clear Entire Table", command=ConfirmingClear)
        clear_table.pack()

        refresh = Button(root, text="Refresh Table",command=Refresh)
        refresh.pack()

        row_number_mem_location = os.path.dirname(__file__) + "\\row_number.txt"
        f = open(row_number_mem_location,"w")
        f.write("0")
        f.close()
        website_mem_location = os.path.dirname(__file__) + "\\websites_url.txt"
        os.remove(website_mem_location)
        html_mem_location = os.path.dirname(__file__) + "\\html_mem.txt"
        os.remove(html_mem_location)
        row_to_url.clear()
        url_to_html.clear()
        Updater()
        root.mainloop()
        

        

#Changing Themes
def change_theme():
    # NOTE: The theme's real name is azure-<mode>
    if root.tk.call("ttk::style", "theme", "use") == "azure-dark":
        # Set light theme
        root.tk.call("set_theme", "light")
    else:
        # Set dark theme
        root.tk.call("set_theme", "dark")

#Check URL
def url_checker(url, row):
    #GET THE HTML OF THE URL
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}
    response = requests.get(url, headers=headers, verify=False)
    new_html = process_html(response.text)
    html_mem_location = os.path.dirname(__file__) + "\\html_mem.txt"
    lines = new_html.split('\n')
    true_new_html = '\t'.join([line.strip() for line in lines])
    #true_new_html = new_html.replace('\n', "")
    #CHECK IF MAP HAS URL
    if (url in url_to_html.keys()):
        old_html_code = url_to_html.get(url)
        #IF IT HAS URL, CHECK IF HTML MATCHES THE NEW HTML
        if (old_html_code == true_new_html):
            return "Unchanged"
        elif (old_html_code != true_new_html and SequenceMatcher(None, old_html_code, true_new_html).quick_ratio() < .98):
            url_to_html[url] = true_new_html
            #Figure out how to update memory file here
            file = open(html_mem_location, "r", encoding="utf-8")
            lines = file.readlines()
            file.close()
            new_file = open(html_mem_location, "r", encoding="utf-8")
            replacement = ""
            text = new_file.read()
            text.replace(old_html_code, true_new_html)
            new_file.close()
            new_file = open(html_mem_location, "w", encoding="utf-8")
            new_file.write(text)
            # for line in new_file:
            #     line = line.strip()
            #     changes = line.replace(old_html_code, '\n'+true_new_html)
            #     replacement = replacement + changes
            # new_file.close()
            # new_file = open(html_mem_location, "w", encoding="utf-8")
            # #Parse replacement by line
            # split = replacement.split('\n')
            # print(len(split))
            # i = 0
            # while (i!=row):
            #     new_file.write(split[i])
            #     i+=1
            # new_file.write('\n')
            # while (i < get_len_rows()):
            #     new_file.write(split[i] + '\n')
            #     i+=1
            SendMail(url)
            return "UPDATED!"
        else:
            return "Difference but Unlikely"
    else:
        print("ERROR")

#UPDATER

def Updater():
    global root
    global table
    entered = False
    global after_id
    i = 0
    while (i < len(row_to_url)):
        entered = True
        try:
            table.__setitem__((i,2),url_checker(row_to_url.get(i), i))
        except:
            print("")
        i+=1
    if entered:
        today = datetime.datetime.now()
        date_time = today.strftime("%m/%d/%Y, %H:%M:%S")
        print("Table was just automatically refreshed at " + date_time + "!")
    after_id = root.after(10000, Updater)

def CancelAfter():
    global root
    root.after_cancel(after_id)

#Get Amount of Rows
def get_len_rows():
    row_number_mem_location = os.path.dirname(__file__) + "\\row_number.txt"
    with open(row_number_mem_location) as f:
        new_row = int(f.read())
    return new_row

def process_html(string):
    soup = BeautifulSoup(string, features="lxml")

    # make the html look good
    soup.prettify()

    #find body
    body = soup.find('body')

    # words = set(nltk.corpus.words.words())
    # final = " ".join(w for w in nltk.wordpunct_tokenize(str(body)) \
    #      if w.lower() in words or not w.isalpha())
    # final = ''.join([i for i in final if not i.isdigit()])

    # print(body)
    # if ("<form method=\"post\" action=\"/cart/add\"" in body):
    #     x = body.find("<form method=\"post\" action=\"/cart/add\"")
    #     body = body[x:len(body)]
    # #remove script tags
    # for s in soup.select('script'):
    #     s.extract()

    # # remove meta tags 
    # for s in soup.select('meta'):
    #     s.extract()
    # # remove head
    # for s in soup.select('head'):
    #     s.extract()
    

    # convert to a string, remove '\r', and return
    #return str(soup).replace('\r', '')
    return str(body)

def RefreshTable():
    row_to_url.clear()
    url_to_html.clear()
    #Our Mem File For Remembering Rows
    row_number_mem_location = os.path.dirname(__file__) + "\\row_number.txt"
    if (not os.path.isfile(row_number_mem_location)): #Check if mem file doesn't exist
        #Write a mem file
        f = open(row_number_mem_location, "w")
        f = open(row_number_mem_location, "w")
        f.write("0")
        f.close()
    else:
        #LOAD ALL ROW# DATA
        with open(row_number_mem_location) as f:
            new_row = int(f.read())
        i = 0
        while (i < new_row):
            table._append_n_rows(1)
            table.__setitem__((i,0),str(i))
            i+=1

    #Our Mem Check For Websites to Load in
    website_mem_location = os.path.dirname(__file__) + "\\websites_url.txt"
    if (os.path.isfile(website_mem_location)):
        with open(row_number_mem_location) as f:
            new_row = int(f.read())
        i = 0
        #Have to format data into an array, parsed by new line
        with open(website_mem_location) as f:
            data = f.read()
        all_websites = data.split('\n')
        all_websites.pop()
        while (i < len(all_websites)):
            table.__setitem__((i,1),all_websites[i])
            #Add map here, load keys from all websites array, load values from html mem file
            row_to_url[i] = all_websites[i]
            i+=1


    #Our Mem Check For HTML
    html_mem_location = os.path.dirname(__file__) + "\\html_mem.txt"
    if (os.path.isfile(html_mem_location)):
        with open(row_number_mem_location) as f:
            new_row = int(f.read())
        i = 0
        with open(html_mem_location, encoding="utf-8") as y:
            data = y.read()
        all_html = data.split('\n')
        all_html.pop()
        while (i < len(all_html)):
            url_to_html[row_to_url.get(i)] = all_html[i]
            i+=1


def Refresh():
    print("Attempting to Refresh")
    global root
    global table
    i = 0
    while (i < len(row_to_url)):
        table.__setitem__((i,2),url_checker(row_to_url.get(i), i))
        i+=1
    print("Refreshed")

def DeleteWebpage():
    global row_to_delete
    try:
        row_to_delete = input("Enter Row# To Delete: ")
    except:
        print("You Hit the Button While An Input Was Already Being Requested")
        return
    if (int(row_to_delete) >= get_len_rows() or int(row_to_delete) < 0):
        print("Row Does Not Exist")
        return
    else:
        # table._pop_n_rows(1)
        global table
        del(table)
        # Update Row Count
        row_number_mem_location = os.path.dirname(__file__) + "\\row_number.txt"
        website_mem_location = os.path.dirname(__file__) + "\\websites_url.txt"
        html_mem_location = os.path.dirname(__file__) + "\\html_mem.txt"
        with open(row_number_mem_location) as f:
            new_row = int(f.read()) - call
            new_row = str(new_row)
        f = open(row_number_mem_location, "w", encoding='utf-8')
        f.write(new_row)
        f.close()
        # Update Website Memory
        with open(website_mem_location, 'r', encoding='utf-8') as file:
            data = file.readlines()
        data.pop(int(row_to_delete))
        with open(website_mem_location, 'w',encoding='utf-8') as file:
            file.writelines( data )
        # Update HTML Memory
        with open(html_mem_location, 'r',encoding='utf-8') as file:
            data2 = file.readlines()
        data2.pop(int(row_to_delete))
        with open(html_mem_location, 'w',encoding='utf-8') as file:
            file.writelines( data2 )

        #UPDATE MAPS
        global row_to_url
        global url_to_html
        # url_to_delete = row_to_url.get(int(row_to_delete))
        # row_to_url.pop(int(row_to_delete))
        # url_to_html.pop(url_to_delete)
        row_to_url.clear()
        url_to_html.clear()
        CancelAfter()
        #Refresh Table
        global root
        root.destroy()
        root = Tk()
        root.tk.call("source", os.path.dirname(__file__) + "\\Azure-ttk-theme-main\\azure.tcl")
        root.tk.call("set_theme", "light")
        root.title("Website Monitor")
        table = Table(root, ["Row #", "Webpage URL", "Status"], column_minwidths=[80, 600, 100])
        table.pack(padx=10,pady=10,side=LEFT)
        
        CreateGUI()
        RefreshTable()
        Updater()

root = Tk()
root.tk.call("source", os.path.dirname(__file__) + "\\Azure-ttk-theme-main\\azure.tcl")
root.tk.call("set_theme", "light")
root.title("Website Monitor")
table = Table(root, ["Row #", "Webpage URL", "Status"], column_minwidths=[80, 600, 100])
table.pack(padx=10,pady=10,side=LEFT)

#Create Window
def CreateGUI():
    #Create all Buttons
    add_webpage = Button(root, text ="Add a Website", command = AddWebsite)
    add_webpage.pack()

    delete_webpage = Button(root, text ="Delete a Website", command = DeleteWebpage)
    delete_webpage.pack()

    notification_method = Button(root,text="Send Test Message to Email", command = SendTest)
    notification_method.pack()

    clear_table = Button(root, text="Clear Entire Table", command=ConfirmingClear)
    clear_table.pack()

    refresh = Button(root, text="Refresh Table",command=Refresh)
    refresh.pack()

def SendTest():
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls

    sender_email = "pythondevmanager@gmail.com" # replace with your email address
    receiver_email = ["pythondevmanager@gmail.com"] # TODO: replace with your recipients
    password = 'sqkoymixuwalxbit'  # replace with your 16-digit-character password 

    # assuming these two values are from your analysis
    score = 0.86
    today_date = '2021-08-08'

    # initialise message instance
    msg = MIMEMultipart()
    msg["Subject"] = "Test Message".format(today_date)
    msg["From"] = sender_email
    msg['To'] = ", ".join(receiver_email)

    ## Plain text
    text = "THIS IS A TEST"

    body_text = MIMEText(text, 'plain')  # 
    msg.attach(body_text)  # attaching the text body into msg

    html = """\
    <html>
    <body>
        <p>Hi,<br>
        <br>
        This message was sent from Webpage Monitor App to inform as a test to ensure notification system is working.>
        Thank you. <br>
        </p>
    </body>
    </html>
    """

    body_html = MIMEText(html.format(today_date, score), 'html')  # parse values into html text
    msg.attach(body_html)  # attaching the text body into msg


    # context = ssl.create_default_context()
    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.connect(smtp_server, port)
        server.ehlo()  # check connection
        server.starttls()  # Secure the connection
        server.ehlo()  # check connection
        server.login(sender_email, password)

        # Send email here
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("SENT TEST MESSAGE")

    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        #server.quit()
        print()

#Sending Email
def SendMail(url):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls

    sender_email = "pythondevmanager@gmail.com" # replace with your email address
    receiver_email = ["pythondevmanager@gmail.com"] # TODO: replace with your recipients
    password = 'sqkoymixuwalxbit'  # replace with your 16-digit-character password 

    # assuming these two values are from your analysis
    score = 0.86
    today_date = '2021-08-08'

    # initialise message instance
    msg = MIMEMultipart()
    msg["Subject"] = "Website " + url + " Updated".format(today_date)
    msg["From"] = sender_email
    msg['To'] = ", ".join(receiver_email)

    ## Plain text
    text = "THE WEBSITE " + url + " HAS BEEN UPDATED"

    body_text = MIMEText(text, 'plain')  # 
    msg.attach(body_text)  # attaching the text body into msg

    html = """\
    <html>
    <body>
        <p>Hi,<br>
        <br>
        This message was sent from Webpage Monitor App to inform you that the website above has been updated<br>
        Thank you. <br>
        </p>
    </body>
    </html>
    """

    body_html = MIMEText(html.format(today_date, score), 'html')  # parse values into html text
    msg.attach(body_html)  # attaching the text body into msg


    # context = ssl.create_default_context()
    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.connect(smtp_server, port)
        server.ehlo()  # check connection
        server.starttls()  # Secure the connection
        server.ehlo()  # check connection
        server.login(sender_email, password)

        # Send email here
        server.sendmail(sender_email, receiver_email, msg.as_string())

    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        #server.quit()
        print()

# def BackupMem():
#     path = os.path.dirname(__file__) + "\\BackupMem"
#     if (not os.path.isdir(path)):
#         os.mkdir(path)
#     row_number_mem_location = os.path.dirname(__file__) + "\\row_number.txt"
#     website_mem_location = os.path.dirname(__file__) + "\\websites_url.txt"
#     html_mem_location = os.path.dirname(__file__) + "\\html_mem.txt"
#     if (os.path.exists(row_number_mem_location)):
#         shutil.copyfile(row_number_mem_location, path+"\\row_number.txt")
#     if (os.path.exists(website_mem_location)):
#         shutil.copyfile(website_mem_location, path+"\\websites_url.txt")
#     if (os.path.exists(html_mem_location)):
#         shutil.copyfile(html_mem_location, path+"\\html_mem.txt")
#     root.after(10000, BackupMem)

CreateGUI()
RefreshTable()
Updater()
# BackupMem()

#Loop the window
root.mainloop()