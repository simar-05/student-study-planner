import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

BG = '#f2d5ed'
PURPLE = '#92278f'
DARK = '#29212d'
WHITE = '#ffffff'
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assignments.json')

root = tk.Tk()
root.title('MyStudySpace - Student Study Planner')
root.geometry('1000x720')
root.minsize(780, 570)
root.configure(bg=BG)

style = ttk.Style(root)
style.configure('Treeview', rowheight=32, font=('Arial', 11))
style.configure('Treeview.Heading', font=('Arial', 11, 'bold'))

assignments = []
sort_choice = 'Title (A-Z)'
filter_choice = 'All'
last_change = None
current_screen = 'welcome'


def save_data():
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(assignments, f, indent=2)
        return True
    except OSError as exc:
        messagebox.showerror('Save error', f'Could not save assignments: {exc}')
        return False


def load_data():
    global assignments
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                assignments = data
        except (OSError, ValueError) as exc:
            messagebox.showwarning('Load warning', f'Could not load saved assignments: {exc}')


def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()


def heading(parent, text):
    tk.Label(parent, text=text, bg=BG, fg=DARK,
             font=('Arial', 24, 'bold')).pack(pady=(12, 18))


def button(parent, text, command, **kwargs):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg="#ffffff",
        fg="#222222",
        activebackground="#e8c5e5",
        activeforeground="#222222",
        font=("Arial", 12, "bold"),
        padx=14,
        pady=8,
        relief="raised",
        cursor="hand2",
        **kwargs
    )

def frame():
    global current_screen
    clear_screen()
    body = tk.Frame(root, bg=BG, padx=25, pady=18)
    body.pack(fill='both', expand=True)
    return body


def header(parent, home=True):
    bar = tk.Frame(parent, bg=BG)
    bar.pack(fill='x')
    tk.Label(bar, text='🎓 MyStudySpace', bg=BG, fg=DARK,
             font=('Arial', 18, 'bold')).pack(side='left')
    if home:
        button(bar, 'Home / Dashboard', show_dashboard).pack(side='right')


def show_welcome():
    global current_screen
    current_screen = 'welcome'
    body = frame()
    body.pack_propagate(False)
    tk.Label(body, text='🎓', bg=BG, font=('Arial', 64)).pack(pady=(85, 5))
    heading(body, 'MyStudySpace')
    tk.Label(body, text='Organize your assignments, track deadlines, and stay on top of your coursework.',
             bg=BG, fg=DARK, font=('Arial', 14), wraplength=700).pack(pady=20)
    button(body, "Let's Get Started →", show_dashboard).pack(pady=(38, 24))
    tk.Label(body, text='Click Get Started to open your dashboard. Add assignments, view details, and track progress.',
             bg=BG, fg=DARK, wraplength=700, font=('Arial', 11)).pack(pady=(12, 0))


def visible_assignments():
    entries = [(i, a) for i, a in enumerate(assignments)]
    if filter_choice != 'All':
        entries = [(i, a) for i, a in entries if a.get('status', 'Incomplete') == filter_choice]
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2, 'None': 3}
    if sort_choice == 'Due date (earliest)':
        entries.sort(key=lambda item: item[1].get('due_date') or '9999-12-31')
    elif sort_choice == 'Due date (latest)':
        entries.sort(key=lambda item: item[1].get('due_date') or '0000-00-00', reverse=True)
    elif sort_choice == 'Priority (high-low)':
        entries.sort(key=lambda item: priority_order.get(item[1].get('priority', 'None'), 3))
    elif sort_choice == 'Priority (low-high)':
        entries.sort(key=lambda item: priority_order.get(item[1].get('priority', 'None'), 3), reverse=True)
    elif sort_choice == 'Title (Z-A)':
        entries.sort(key=lambda item: item[1].get('name', '').lower(), reverse=True)
    else:
        entries.sort(key=lambda item: item[1].get('name', '').lower())
    return entries


def show_dashboard():
    global current_screen
    current_screen = 'dashboard'
    body = frame()
    header(body, home=False)
    heading(body, 'My Assignments')
    toolbar = tk.Frame(body, bg=BG)
    toolbar.pack(fill='x', pady=(0, 12))
    button(toolbar, 'View All Assignments', show_dashboard).pack(side='left', padx=(0, 8))
    button(toolbar, 'Sort / Filter Assignments', show_sort_filter).pack(side='left')
    tk.Label(toolbar, text=f'{len(assignments)} total assignments', bg=BG, fg=DARK,
             font=('Arial', 11)).pack(side='right')

    columns = ('Assignment', 'Course', 'Due Date', 'Priority', 'Status')
    table_frame = tk.Frame(body, bg=BG)
    table_frame.pack(fill='both', expand=True)
    table = ttk.Treeview(table_frame, columns=columns, show='headings', selectmode='extended')
    widths = [250, 150, 130, 110, 120]
    for name, width in zip(columns, widths):
        table.heading(name, text=name)
        table.column(name, width=width, minwidth=80, anchor='center' if name != 'Assignment' else 'w')
    scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)
    table.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')
    for i, a in visible_assignments():
        table.insert('', 'end', iid=str(i), values=(a.get('name', ''), a.get('course', ''),
                     a.get('due_date') or 'No due date', a.get('priority', 'None'),
                     a.get('status', 'Incomplete')))

    def selected_ids():
        return [int(item) for item in table.selection()]

    def show_details():
        ids = selected_ids()
        if not ids:
            messagebox.showinfo('Select an assignment', 'Select an assignment first, then click View Details.')
            return
        a = assignments[ids[0]]
        details = tk.Toplevel(root)
        details.title('Assignment Details')
        details.geometry('560x450')
        details.configure(bg=BG)
        details.transient(root)
        details.grab_set()
        tk.Label(details, text=a.get('name', ''), bg=BG, fg=DARK,
                 font=('Arial', 20, 'bold'), wraplength=500).pack(pady=(22, 12))
        for label, value in (
            ('Course', a.get('course') or 'Not specified'),
            ('Due Date', a.get('due_date') or 'No due date'),
            ('Priority', a.get('priority', 'None')),
            ('Status', a.get('status', 'Incomplete')),
        ):
            tk.Label(details, text=f'{label}: {value}', bg=BG, fg=DARK,
                     font=('Arial', 12)).pack(anchor='w', padx=28, pady=4)
        tk.Label(details, text='What to do / Assignment Instructions', bg=BG,
                 fg=DARK, font=('Arial', 13, 'bold')).pack(anchor='w', padx=28, pady=(18, 5))
        description = tk.Text(details, height=6, wrap='word', bg=WHITE, fg=DARK,
                              font=('Arial', 12), padx=10, pady=8)
        description.insert('1.0', a.get('description') or 'No instructions added for this assignment.')
        description.config(state='disabled')
        description.pack(fill='both', expand=True, padx=28, pady=(0, 12))
        button(details, 'Close', details.destroy).pack(pady=(0, 18))

    def mark_selected():
        global last_change
        ids = selected_ids()
        if not ids:
            messagebox.showwarning('No selection', 'Select one or more assignments to mark complete.')
            return
        changes = [(i, assignments[i].get('status', 'Incomplete')) for i in ids]
        for i in ids:
            assignments[i]['status'] = 'Complete'
        if save_data():
            last_change = changes
        show_dashboard()

    def mark_all():
        global last_change
        incomplete = [(i, a.get('status', 'Incomplete')) for i, a in enumerate(assignments)
                      if a.get('status', 'Incomplete') != 'Complete']
        if not incomplete:
            messagebox.showinfo('Nothing to update', 'All assignments are already complete.')
            return
        if not messagebox.askyesno('Confirm mark all', f'Mark {len(incomplete)} assignments complete?'):
            return
        for i, _ in incomplete:
            assignments[i]['status'] = 'Complete'
        if save_data():
            last_change = incomplete
        show_dashboard()

    actions = tk.Frame(body, bg=BG)
    actions.pack(fill='x', pady=15)
    button(actions, '+ Add Assignment', show_add).pack(side='left', padx=5)
    button(actions, 'View Details', show_details).pack(side='left', padx=5)
    button(actions, 'Mark Selected Complete', mark_selected).pack(side='left', padx=5)
    button(actions, 'Mark All Complete', mark_all).pack(side='left', padx=5)
    button(actions, 'Undo Completion', undo_completion).pack(side='right', padx=5)
    tk.Label(body, text='Tip: Select a row to view details or mark it complete. Hold Command to select multiple rows.',
             bg=BG, fg=DARK, font=('Arial', 10)).pack(anchor='w')


def undo_completion():
    global last_change
    if not last_change:
        messagebox.showinfo('Nothing to undo', 'No recent completion change is available to undo.')
        return
    for i, old_status in last_change:
        if i < len(assignments):
            assignments[i]['status'] = old_status
    if save_data():
        last_change = None
    show_dashboard()


def show_add():
    global current_screen
    current_screen = 'add'
    body = frame()
    header(body)
    heading(body, 'Add Assignment')
    tk.Label(body, text='* Required: assignment title and course name. Due date and priority are optional. About 1 minute to fill out.',
             bg=BG, fg=DARK, font=('Arial', 11), wraplength=850).pack(pady=(0, 18))
    form = tk.Frame(body, bg=BG)
    form.pack()
    fields = {}
    for row, (key, label) in enumerate((('name', 'Assignment Title *'), ('course', 'Course Name *'),
                                         ('due_date', 'Due Date (YYYY-MM-DD)'),)):
        tk.Label(form, text=label, bg=BG, fg=DARK, font=('Arial', 12)).grid(row=row, column=0, sticky='w', pady=10, padx=10)
        entry = tk.Entry(form, width=40, bg=WHITE, fg=DARK, insertbackground=DARK, font=('Arial', 12))
        entry.grid(row=row, column=1, pady=10, padx=10)
        fields[key] = entry
    tk.Label(form, text='Priority (optional)', bg=BG, fg=DARK, font=('Arial', 12)).grid(row=3, column=0, sticky='w', pady=10, padx=10)
    priority = ttk.Combobox(form, values=['None', 'Low', 'Medium', 'High'], state='readonly', width=37, font=('Arial', 12))
    priority.set('None')
    priority.grid(row=3, column=1, pady=10, padx=10)
    tk.Label(body, text='What to do / Assignment Instructions (optional)', bg=BG,
             fg=DARK, font=('Arial', 12)).pack(pady=(10, 4))
    instructions = tk.Text(body, height=4, width=65, wrap='word', bg=WHITE,
                           fg=DARK, insertbackground=DARK, font=('Arial', 12))
    instructions.pack()
    preview_text = tk.StringVar(value='Preview is not saved. Review your details before saving.')
    tk.Label(body, textvariable=preview_text, bg=WHITE, fg=DARK, font=('Arial', 11),
             justify='left', wraplength=700, padx=15, pady=12).pack(pady=18)

    def read_form():
        name = fields['name'].get().strip()
        course = fields['course'].get().strip()
        date = fields['due_date'].get().strip()
        if not name or not course:
            messagebox.showerror('Missing required fields', 'Assignment title and course name are required.')
            return None
        if date:
            try:
                parsed = datetime.strptime(date, '%Y-%m-%d')
                if parsed.strftime('%Y-%m-%d') != date:
                    raise ValueError()
            except ValueError:
                messagebox.showerror('Invalid date', 'Use a valid date in YYYY-MM-DD format, or leave it blank.')
                return None
        return {'name': name, 'course': course, 'due_date': date,
                'priority': priority.get(), 'status': 'Incomplete',
                'description': instructions.get('1.0', 'end-1c').strip()}

    def preview():
        a = read_form()
        if a:
            preview_text.set(f"PREVIEW ONLY — not saved yet\nAssignment: {a['name']}\nCourse: {a['course']}\n"
                             f"Due Date: {a['due_date'] or 'No due date'}\nPriority: {a['priority']}\n"
                             f"Instructions: {a['description'] or 'None added'}")

    def save():
        a = read_form()
        if not a:
            return
        assignments.append(a)
        if save_data():
            messagebox.showinfo('Saved', 'Assignment saved successfully!')
            show_dashboard()
        else:
            assignments.pop()

    def cancel():
        if (any(fields[key].get().strip() for key in fields) or instructions.get('1.0', 'end-1c').strip()) and not messagebox.askyesno(
                'Discard unsaved changes?', 'Return to dashboard without saving this assignment?'):
            return
        show_dashboard()

    controls = tk.Frame(body, bg=BG)
    controls.pack(pady=8)
    button(controls, 'Preview Assignment', preview).pack(side='left', padx=6)
    button(controls, 'Save Assignment', save).pack(side='left', padx=6)
    button(controls, 'Cancel / Back Home', cancel).pack(side='left', padx=6)
    fields['name'].focus_set()


def show_sort_filter():
    global current_screen
    current_screen = 'sort'
    body = frame()
    header(body)
    heading(body, 'Sort and Filter Assignments')
    tk.Label(body, text='Sort By', bg=BG, fg=DARK, font=('Arial', 16, 'bold')).pack(pady=(15, 5))
    sort_var = tk.StringVar(value=sort_choice)
    for option in ('Due date (earliest)', 'Due date (latest)', 'Priority (high-low)',
                   'Priority (low-high)', 'Title (A-Z)', 'Title (Z-A)'):
        tk.Radiobutton(body, text=option, variable=sort_var, value=option, bg=BG, fg=DARK,
                       selectcolor=WHITE, font=('Arial', 12), anchor='w').pack(anchor='center')
    tk.Label(body, text='Filter By Status', bg=BG, fg=DARK, font=('Arial', 16, 'bold')).pack(pady=(18, 5))
    filter_var = tk.StringVar(value=filter_choice)
    for label, value in (('All', 'All'), ('Incomplete only', 'Incomplete'), ('Complete only', 'Complete')):
        tk.Radiobutton(body, text=label, variable=filter_var, value=value, bg=BG, fg=DARK,
                       selectcolor=WHITE, font=('Arial', 12)).pack()

    def apply():
        global sort_choice, filter_choice
        sort_choice = sort_var.get()
        filter_choice = filter_var.get()
        show_dashboard()

    controls = tk.Frame(body, bg=BG)
    controls.pack(pady=20)
    button(controls, 'Save Changes', apply).pack(side='left', padx=8)
    button(controls, 'Cancel / Back Home', show_dashboard).pack(side='left', padx=8)


load_data()
show_welcome()
root.mainloop()

