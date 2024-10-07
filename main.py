# Importing all necessary modules
import sqlite3
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
from datetime import datetime, timedelta

# Connecting to Database
connector = sqlite3.connect('library.db')
cursor = connector.cursor()

connector.execute(
    'CREATE TABLE IF NOT EXISTS Library (BK_NAME TEXT, BK_ID TEXT PRIMARY KEY NOT NULL, AUTHOR_NAME TEXT, BK_STATUS TEXT, CARD_ID TEXT, ISSUE_DATE TEXT)'
)

# Functions
def issuer_card():
    return sd.askstring('Issuer Card ID', 'Enter the Issuer\'s Card ID:')

def display_records():
    tree.delete(*tree.get_children())
    cursor.execute('SELECT * FROM Library')
    for record in cursor.fetchall():
        tree.insert('', END, values=record)

def clear_fields():
    bk_status.set('Available')
    bk_id.set(''); bk_name.set(''); author_name.set(''); card_id.set('')
    bk_id_entry.config(state='normal')

def add_record():
    if bk_status.get() == 'Issued':
        card_id.set(issuer_card())
    
    try:
        connector.execute('INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID) VALUES (?, ?, ?, ?, ?)',
                          (bk_name.get(), bk_id.get(), author_name.get(), bk_status.get(), card_id.get()))
        connector.commit()
        clear_fields(); display_records()
        mb.showinfo('Success', 'Record added successfully')
    except sqlite3.IntegrityError:
        mb.showerror('Error', 'Book ID already exists')

def view_record():
    if not tree.selection():
        mb.showerror('Error', 'Please select a record to view')
        return

    current = tree.item(tree.focus())['values']
    bk_name.set(current[0]); bk_id.set(current[1])
    author_name.set(current[2]); bk_status.set(current[3])
    card_id.set(current[4])

def update_record():
    cursor.execute('UPDATE Library SET BK_NAME=?, AUTHOR_NAME=?, BK_STATUS=?, CARD_ID=? WHERE BK_ID=?',
                   (bk_name.get(), author_name.get(), bk_status.get(), card_id.get(), bk_id.get()))
    connector.commit()
    clear_fields(); display_records()

def remove_record():
    if not tree.selection():
        mb.showerror('Error', 'Please select a record to delete')
        return

    current = tree.item(tree.focus())['values'][1]
    cursor.execute('DELETE FROM Library WHERE BK_ID=?', (current,))
    connector.commit()
    clear_fields(); display_records()

# Issue Book Functionality
def change_availability():
    if not tree.selection():
        mb.showerror('Error', 'Please select a book')
        return

    current_item = tree.item(tree.focus())['values']
    bk_id = current_item[1]; status = current_item[3]

    if status == 'Issued':
        cursor.execute('UPDATE Library SET BK_STATUS=?, CARD_ID=?, ISSUE_DATE=? WHERE BK_ID=?',
                       ('Available', 'N/A', 'N/A', bk_id))
        mb.showinfo('Returned', 'Book returned successfully')
    else:
        cursor.execute('UPDATE Library SET BK_STATUS=?, CARD_ID=?, ISSUE_DATE=? WHERE BK_ID=?',
                       ('Issued', issuer_card(), datetime.now().strftime('%Y-%m-%d'), bk_id))
        mb.showinfo('Issued', 'Book issued successfully')

    connector.commit()
    display_records()

# Fine Calculation Function
def calculate_fine():
    if not tree.selection():
        mb.showerror('Error', 'Please select a book')
        return

    current_item = tree.item(tree.focus())['values']
    issue_date = current_item[5]

    if issue_date == 'N/A':
        mb.showinfo('Fine', 'No fine, book is available')
        return

    days_overdue = (datetime.now() - datetime.strptime(issue_date, '%Y-%m-%d')).days - 14
    if days_overdue > 0:
        fine = days_overdue * 2
        mb.showinfo('Fine', f'Total fine: ₹{fine}')
    else:
        mb.showinfo('Fine', 'No fine applicable')

# Search Book
def search_book():
    search_term = sd.askstring('Search Book', 'Enter Book Name or Book ID:')
    tree.delete(*tree.get_children())
    cursor.execute('SELECT * FROM Library WHERE BK_NAME LIKE ? OR BK_ID LIKE ?', (f'%{search_term}%', f'%{search_term}%'))
    for record in cursor.fetchall():
        tree.insert('', END, values=record)

# GUI Setup
root = Tk()
root.title('Library Management System')
root.geometry('1010x530')

# Initialize tkinter variables AFTER root is created
bk_status = StringVar(); bk_name = StringVar()
bk_id = StringVar(); author_name = StringVar()
card_id = StringVar()

Label(root, text='LIBRARY MANAGEMENT SYSTEM', bg='SteelBlue', fg='white', font=('Arial', 15, 'bold')).pack(side=TOP, fill=X)

# Frames
left_frame = Frame(root, bg='LightSkyBlue')
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)

RT_frame = Frame(root, bg='DeepSkyBlue')
RT_frame.place(relx=0.3, y=30, relwidth=0.7, height=100)

RB_frame = Frame(root, bg='DodgerBlue')
RB_frame.place(relx=0.3, y=130, relwidth=0.7, relheight=0.84)

# Left Frame Widgets
Label(left_frame, text='Book ID:', font=('Georgia', 13), bg='LightSkyBlue').place(x=30, y=60)
bk_id_entry = Entry(left_frame, textvariable=bk_id, font=('Times New Roman', 12))
bk_id_entry.place(x=150, y=60)

Label(left_frame, text='Book Name:', font=('Georgia', 13), bg='LightSkyBlue').place(x=30, y=100)
Entry(left_frame, textvariable=bk_name, font=('Times New Roman', 12)).place(x=150, y=100)

Label(left_frame, text='Author Name:', font=('Georgia', 13), bg='LightSkyBlue').place(x=30, y=140)
Entry(left_frame, textvariable=author_name, font=('Times New Roman', 12)).place(x=150, y=140)

Label(left_frame, text='Status:', font=('Georgia', 13), bg='LightSkyBlue').place(x=30, y=180)
OptionMenu(left_frame, bk_status, 'Available', 'Issued').place(x=150, y=180)

Button(left_frame, text='Add Record', bg='SteelBlue', fg='white', font=('Gill Sans MT', 13), command=add_record).place(x=30, y=220)
Button(left_frame, text='Update Record', bg='SteelBlue', fg='white', font=('Gill Sans MT', 13), command=update_record).place(x=30, y=260)
Button(left_frame, text='Delete Record', bg='SteelBlue', fg='white', font=('Gill Sans MT', 13), command=remove_record).place(x=30, y=300)
Button(left_frame, text='Clear Fields', bg='SteelBlue', fg='white', font=('Gill Sans MT', 13), command=clear_fields).place(x=30, y=340)

# Right Frame Widgets
Button(RT_frame, text='Search Book', bg='SteelBlue', fg='white', font=('Gill Sans MT', 13), command=search_book).place(x=50, y=30)
Button(RT_frame, text='Change Availability', bg='SteelBlue', fg='white', font=('Gill Sans MT', 13), command=change_availability).place(x=200, y=30)
Button(RT_frame, text='Calculate Fine', bg='SteelBlue', fg='white', font=('Gill Sans MT', 13), command=calculate_fine).place(x=400, y=30)

# Table for displaying records
tree = ttk.Treeview(RB_frame, columns=('Book Name', 'Book ID', 'Author', 'Status', 'Card ID', 'Issue Date'), show='headings')
tree.heading('Book Name', text='Book Name')
tree.heading('Book ID', text='Book ID')
tree.heading('Author', text='Author')
tree.heading('Status', text='Status')
tree.heading('Card ID', text='Card ID')
tree.heading('Issue Date', text='Issue Date')
tree.pack(fill=BOTH, expand=True)

display_records()

root.mainloop()
