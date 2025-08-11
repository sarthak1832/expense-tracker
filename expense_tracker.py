import datetime
import sqlite3
from tkcalendar import DateEntry
from tkinter import *
import tkinter.messagebox as mb
import tkinter.ttk as ttk

# Connect to DB
connector = sqlite3.connect("Expense Tracker.db")
cursor = connector.cursor()
connector.execute(
    '''CREATE TABLE IF NOT EXISTS ExpenseTracker (
       ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
       Date DATETIME,
       Payee TEXT,
       Description TEXT,
       Amount FLOAT,
       ModeOfPayment TEXT
    )'''
)
connector.commit()

# Colors & Fonts
dataentery_frame_bg = 'Red'
buttons_frame_bg = 'Tomato'
hlb_btn_bg = 'IndianRed'
lbl_font = ('Georgia', 13)
entry_font = 'Times 13 bold'
btn_font = ('Gill Sans MT', 13)

# --- Functions ---
def list_all_expenses():
    table.delete(*table.get_children())
    all_data = connector.execute('SELECT * FROM ExpenseTracker')
    for values in all_data.fetchall():
        table.insert('', END, values=values)

def view_expense_details():
    if not table.selection():
        mb.showerror('No expense selected', 'Select an expense from the table')
        return
    values = table.item(table.focus())['values']
    expenditure_date = datetime.date(int(values[1][:4]), int(values[1][5:7]), int(values[1][8:]))
    date.set_date(expenditure_date)
    payee.set(values[2])
    desc.set(values[3])
    amnt.set(values[4])
    MoP.set(values[5])

def clear_fields():
    today_date = datetime.datetime.now().date()
    desc.set('')
    payee.set('')
    amnt.set(0.0)
    MoP.set('Cash')
    date.set_date(today_date)
    table.selection_remove(*table.selection())

def remove_expense():
    if not table.selection():
        mb.showerror('No record selected!', 'Select a record to delete')
        return
    values = table.item(table.focus())['values']
    if mb.askyesno('Are you sure?', f'Delete record of {values[2]}?'):
        connector.execute('DELETE FROM ExpenseTracker WHERE ID=?', (values[0],))
        connector.commit()
        list_all_expenses()
        mb.showinfo('Deleted', 'Record deleted successfully')

def remove_all_expenses():
    if mb.askyesno('Confirm', 'Delete all expenses?', icon='warning'):
        connector.execute('DELETE FROM ExpenseTracker')
        connector.commit()
        clear_fields()
        list_all_expenses()
        mb.showinfo('Deleted', 'All expenses deleted')

def add_another_expense():
    if not date.get() or not payee.get() or not desc.get() or not amnt.get() or not MoP.get():
        mb.showerror('Fields empty!', "Fill all fields before adding")
    else:
        connector.execute(
            'INSERT INTO ExpenseTracker (Date, Payee, Description, Amount, ModeOfPayment) VALUES (?, ?, ?, ?, ?)',
            (date.get_date(), payee.get(), desc.get(), amnt.get(), MoP.get())
        )
        connector.commit()
        clear_fields()
        list_all_expenses()
        mb.showinfo('Added', 'Expense added to database')

def edit_expense():
    if not table.selection():
        mb.showerror('No selection', 'Select an expense to edit')
        return
    view_expense_details()
    def edit_existing_expense():
        values = table.item(table.focus())['values']
        connector.execute('UPDATE ExpenseTracker SET Date=?, Payee=?, Description=?, Amount=?, ModeOfPayment=? WHERE ID=?',
                          (date.get_date(), payee.get(), desc.get(), amnt.get(), MoP.get(), values[0]))
        connector.commit()
        clear_fields()
        list_all_expenses()
        mb.showinfo('Updated', 'Expense updated')
        edit_btn.destroy()
    edit_btn = Button(data_entry_frame, text='Save edits', font=btn_font, width=30, bg=hlb_btn_bg, command=edit_existing_expense)
    edit_btn.place(x=10, y=395)

def selected_expense_to_words():
    if not table.selection():
        mb.showerror('No selection', 'Select an expense first')
        return
    values = table.item(table.focus())['values']
    message = f'You paid {values[4]} to {values[2]} for {values[3]} on {values[1]} via {values[5]}.'
    mb.showinfo('Expense in words', message)

def expense_to_words_before_adding():
    if not date.get() or not payee.get() or not desc.get() or not amnt.get() or not MoP.get():
        mb.showerror('Incomplete data', 'Fill all fields first')
        return
    message = f'You paid {amnt.get()} to {payee.get()} for {desc.get()} on {date.get_date()} via {MoP.get()}.'
    if mb.askyesno('Confirm add', f'{message}\n\nAdd to database?'):
        add_another_expense()

# --- GUI ---
root = Tk()
root.title('Expense Tracker')
root.geometry('1200x550')
root.resizable(0, 0)
Label(root, text='EXPENSE TRACKER', font=('Noto Sans CJK TC', 15, 'bold'), bg=hlb_btn_bg).pack(side=TOP, fill=X)

desc = StringVar()
amnt = DoubleVar()
payee = StringVar()
MoP = StringVar(value='Cash')

data_entry_frame = Frame(root, bg=dataentery_frame_bg)
data_entry_frame.place(x=0, y=30, relheight=0.95, relwidth=0.25)

buttons_frame = Frame(root, bg=buttons_frame_bg)
buttons_frame.place(relx=0.25, rely=0.05, relwidth=0.75, relheight=0.21)

tree_frame = Frame(root)
tree_frame.place(relx=0.25, rely=0.26, relwidth=0.75, relheight=0.74)

Label(data_entry_frame, text='Date:', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=50)
date = DateEntry(data_entry_frame, date=datetime.datetime.now().date(), font=entry_font)
date.place(x=160, y=50)

Label(data_entry_frame, text='Payee:', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=230)
Entry(data_entry_frame, font=entry_font, width=31, textvariable=payee).place(x=10, y=260)

Label(data_entry_frame, text='Description:', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=100)
Entry(data_entry_frame, font=entry_font, width=31, textvariable=desc).place(x=10, y=130)

Label(data_entry_frame, text='Amount:', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=180)
Entry(data_entry_frame, font=entry_font, width=14, textvariable=amnt).place(x=160, y=180)

Label(data_entry_frame, text='Mode of Payment:', font=lbl_font, bg=dataentery_frame_bg).place(x=10, y=310)
dd1 = OptionMenu(data_entry_frame, MoP, *['Cash', 'Cheque', 'Credit Card', 'Debit Card', 'Paytm', 'Google Pay', 'Razorpay'])
dd1.place(x=160, y=305)
dd1.configure(width=10, font=entry_font)

Button(data_entry_frame, text='Add expense', command=add_another_expense, font=btn_font, width=30, bg=hlb_btn_bg).place(x=10, y=395)
Button(data_entry_frame, text='Convert to words before adding', command=expense_to_words_before_adding, font=btn_font, width=30, bg=hlb_btn_bg).place(x=10, y=450)

Button(buttons_frame, text='Delete Expense', font=btn_font, width=25, bg=hlb_btn_bg, command=remove_expense).place(x=30, y=5)
Button(buttons_frame, text='Clear Fields', font=btn_font, width=25, bg=hlb_btn_bg, command=clear_fields).place(x=335, y=5)
Button(buttons_frame, text='Delete All', font=btn_font, width=25, bg=hlb_btn_bg, command=remove_all_expenses).place(x=640, y=5)
Button(buttons_frame, text='View Details', font=btn_font, width=25, bg=hlb_btn_bg, command=view_expense_details).place(x=30, y=65)
Button(buttons_frame, text='Edit Selected', command=edit_expense, font=btn_font, width=25, bg=hlb_btn_bg).place(x=335, y=65)
Button(buttons_frame, text='Convert to sentence', font=btn_font, width=25, bg=hlb_btn_bg, command=selected_expense_to_words).place(x=640, y=65)

table = ttk.Treeview(tree_frame, selectmode=BROWSE, columns=('ID', 'Date', 'Payee', 'Description', 'Amount', 'Mode of Payment'))
X_Scroller = Scrollbar(table, orient=HORIZONTAL, command=table.xview)
Y_Scroller = Scrollbar(table, orient=VERTICAL, command=table.yview)
X_Scroller.pack(side=BOTTOM, fill=X)
Y_Scroller.pack(side=RIGHT, fill=Y)
table.config(yscrollcommand=Y_Scroller.set, xscrollcommand=X_Scroller.set)

for col, text in enumerate(('S No.', 'Date', 'Payee', 'Description', 'Amount', 'Mode of Payment'), start=1):
    table.heading(f'#{col}', text=text, anchor=CENTER)

table.column('#0', width=0, stretch=NO)
table.column('#1', width=50, stretch=NO)
table.column('#2', width=95, stretch=NO)
table.column('#3', width=150, stretch=NO)
table.column('#4', width=325, stretch=NO)
table.column('#5', width=135, stretch=NO)
table.column('#6', width=125, stretch=NO)
table.place(relx=0, y=0, relheight=1, relwidth=1)

list_all_expenses()
root.mainloop()