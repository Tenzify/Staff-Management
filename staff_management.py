import datetime
import tkinter as tk
from tkinter import ttk
import pandas as pd
import sqlite3
from sqlite3 import Error
 
def load_staff_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM staff;")
    rows = cursor.fetchall()

    columns = ['id', 'IGN', 'Rank', 'Creation Date', 'Last Promotion Date']
    staff_data = pd.DataFrame(rows, columns=columns)
    staff_data.set_index('id', inplace=True)

    return staff_data

class StaffManager(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.ranks = ['Trial Mod', 'Mod', 'Mod+', 'SrMod', 'JrAdmin', 'Admin', 'SrAdmin']
        
        # Connect to the database
        self.conn = create_connection('staff_data.db')
        create_table(self.conn)
        
        self.staff_data = self.load_staff_data()
        self.create_widgets()
        self.update_tree()  
        self.pack()

    def load_staff_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM staff;")
        rows = cursor.fetchall()

        columns = ['id', 'IGN', 'Rank', 'Creation Date', 'Last Promotion Date']
        staff_data = pd.DataFrame(rows, columns=columns)
        staff_data.set_index('id', inplace=True)

        return staff_data

    def insert_staff(self, ign, rank, creation_date, last_promotion_date):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO staff (IGN, Rank, Creation_Date, Last_Promotion_Date) VALUES (?, ?, ?, ?);",
                       (ign, rank, creation_date, last_promotion_date))
        self.conn.commit()
        return cursor.lastrowid

    def update_staff(self, staff_id, rank, last_promotion_date):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE staff SET Rank = ?, Last_Promotion_Date = ? WHERE id = ?;",
                       (rank, last_promotion_date, staff_id))
        self.conn.commit()

    def delete_staff(self, staff_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM staff WHERE id = ?;", (staff_id,))
        self.conn.commit()

    def create_widgets(self):
        # ... El resto del código de la función create_widgets ...

        self.tree = ttk.Treeview(self)
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Configure the columns
        self.tree['columns'] = ('IGN', 'Rank', 'Creation Date', 'Last Promotion Date')
        self.tree.column('#0', stretch=tk.NO, minwidth=0, width=50)
        self.tree.column('IGN', stretch=tk.NO, minwidth=0, width=150)
        self.tree.column('Rank', stretch=tk.NO, minwidth=0, width=100)
        self.tree.column('Creation Date', stretch=tk.NO, minwidth=0, width=120)
        self.tree.column('Last Promotion Date', stretch=tk.NO, minwidth=0, width=120)

        # Configure the column headings
        self.tree.heading('#0', text='Index', anchor=tk.W)
        self.tree.heading('IGN', text='IGN', anchor=tk.W)
        self.tree.heading('Rank', text='Rank', anchor=tk.W)
        self.tree.heading('Creation Date', text='Creation Date', anchor=tk.W)
        self.tree.heading('Last Promotion Date', text='Last Promotion Date', anchor=tk.W)

        # Create the add staff frame
        add_frame = tk.Frame(self)
        add_frame.pack(side=tk.TOP, fill=tk.X)

        # Create the add staff entry widget
        self.add_entry = tk.Entry(add_frame)
        self.add_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Create the rank selection dropdown
        self.rank_var = tk.StringVar()
        self.rank_var.set(self.ranks[0])
        rank_dropdown = tk.OptionMenu(add_frame, self.rank_var, *self.ranks)
        rank_dropdown.pack(side=tk.LEFT)

        # Create the add staff button
        add_button = tk.Button(add_frame, text='Add Staff', command=self.add_staff)
        add_button.pack(side=tk.LEFT)

        # Create the promote and demote buttons
        promote_button = tk.Button(self, text='Promote', command=self.promote_staff)
        promote_button.pack(side=tk.LEFT)
        demote_button = tk.Button(self, text='Demote', command=self.demote_staff)
        demote_button.pack(side=tk.LEFT)

        # Create the expel button
        expel_button = tk.Button(self, text='Expel', command=self.expel_staff)
        expel_button.pack(side=tk.RIGHT)


    def add_staff(self):
        ign = self.add_entry.get()
        rank = self.rank_var.get()
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        new_idx = len(self.staff_data)

        staff_id = self.insert_staff(ign, rank, current_date, current_date)
        self.staff_data.loc[staff_id] = [ign, rank, current_date, current_date]
        self.update_tree()

    def promote_staff(self):
        staff_id = self.get_selected_row_index()
        if staff_id is not None and staff_id >= 0:
            current_rank = self.staff_data.at[staff_id, 'Rank']
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')

            if current_rank in self.ranks[:-1]:
                new_rank = self.ranks[self.ranks.index(current_rank) + 1]
                self.staff_data.at[staff_id, 'Rank'] = new_rank
                self.staff_data.at[staff_id, 'Last Promotion Date'] = current_date
                self.update_staff(staff_id, new_rank, current_date)
                self.update_tree()

    def demote_staff(self):
        staff_id = self.get_selected_row_index()
        if staff_id is not None and staff_id >= 0:
            current_rank = self.staff_data.at[staff_id, 'Rank']
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')

            if current_rank in self.ranks[1:]:
                new_rank = self.ranks[self.ranks.index(current_rank) - 1]
                self.staff_data.at[staff_id, 'Rank'] = new_rank
                self.staff_data.at[staff_id, 'Last Promotion Date'] = current_date
                self.update_staff(staff_id, new_rank, current_date)
                self.update_tree()

    def expel_staff(self):
        staff_id = self.get_selected_row_index()
        if staff_id is not None and staff_id >= 0:
            self.staff_data = self.staff_data.drop(staff_id)
            self.staff_data.reset_index(drop=True, inplace=True)
            self.delete_staff(staff_id)
            self.update_tree()


    def update_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for idx, row in self.staff_data.iterrows():
            self.tree.insert('', 'end', text=str(idx), values=(row['IGN'], row['Rank'], row['Creation Date'], row['Last Promotion Date']))

    def get_selected_row_index(self):
        selected = self.tree.selection()
        if selected:
            return int(self.tree.item(selected[0], 'text'))
        return None
    
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS staff (
                              id INTEGER PRIMARY KEY,
                              IGN TEXT NOT NULL,
                              Rank TEXT NOT NULL,
                              Creation_Date TEXT NOT NULL,
                              Last_Promotion_Date TEXT NOT NULL
                          );''')
    except Error as e:
        print(e)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Battle Network - Staff List")
    app = StaffManager(root)
    root.mainloop()
