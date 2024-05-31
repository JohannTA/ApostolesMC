import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
import threading
import tempfile
import time
import shutil
import os
import git
import mysql.connector

# Configuración de la base de datos
DATABASE_CONFIG = {
    "database": "*",
    "user": "*",
    "password": "*",
    "host": "*",
    "port": 10422  
}
PROGRAM_VERSION = "1.0.0"

def check_program_version():
    conn = None
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT version FROM programa WHERE estado = TRUE;")
        active_version = cur.fetchone()
        
        if active_version is None:
            messagebox.showerror("Error", "No hay versiones activas del programa.")
            return False
        elif active_version[0] != PROGRAM_VERSION:
            messagebox.showerror("Versión Desactualizada", "Programa desactualizado, por favor instale la última versión.")
            return False
        return True
    except mysql.connector.Error as e:
        messagebox.showerror("Error de Base de Datos", str(e))
        return False
    finally:
        if conn:
            conn.close()

def actualizar_mods():
    if not check_program_version():
        return
    def run_update():
        try:
            text_area.config(state='normal')
            text_area.insert(tk.END, "Obteniendo información...\n")
            text_area.config(state='disabled')
            repo_url = 'https://github.com/JohannTA/ApostolesMC'
            with tempfile.TemporaryDirectory() as tmpdirname:
                repo_path = tmpdirname
                repo = git.Repo.clone_from(repo_url, repo_path)
                
                version_dir = os.path.join(repo_path, 'Versiones')
                latest_version = max([d for d in os.listdir(version_dir) if os.path.isdir(os.path.join(version_dir, d))])
                
                for i in range(50):
                    time.sleep(0.1)
                    progress_bar['value'] += 1
                    root.update_idletasks()
                text_area.config(state='normal')
                text_area.insert(tk.END, "Información obtenida. Preparando actualización de mods...\n")
                text_area.config(state='disabled')

                mods_files = os.listdir(mod_directory)
                new_mod_files = os.listdir(os.path.join(version_dir, latest_version))
                total_files = len(mods_files) + len(new_mod_files)
                increment_per_file = 50 / total_files

                source_path = os.path.join(version_dir, latest_version)

                for item in mods_files:
                    item_path = os.path.join(mod_directory, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    progress_bar['value'] += increment_per_file
                    time.sleep(0.1)
                    root.update_idletasks()

                for filename in new_mod_files:
                    shutil.copy(os.path.join(source_path, filename), mod_directory)
                    progress_bar['value'] += increment_per_file
                    time.sleep(0.1)
                    root.update_idletasks()

                text_area.config(state='normal')
                text_area.insert(tk.END, "Mods actualizados correctamente a la versión más reciente.\n", 'success')
                text_area.config(state='disabled')
        except Exception as e:
            text_area.config(state='normal')
            text_area.insert(tk.END, f"Error: {e}\n", 'error')
            text_area.config(state='disabled')
        finally:
            progress_bar['value'] = 100
            root.after(500, lambda: progress_bar.config(value=0))

    update_thread = threading.Thread(target=run_update)
    update_thread.start()

def open_github():
    webbrowser.open('https://github.com/JohannTA')

def change_mod_directory():
    global mod_directory
    directory = filedialog.askdirectory()
    if directory:
        mod_directory = directory
        text_area.config(state='normal')
        text_area.insert(tk.END, f"Directorio de mods cambiado a: {mod_directory}\n", 'directory_change')
        text_area.config(state='disabled')

root = tk.Tk()
root.title("ModARC")
root.configure(bg='#34495e')

style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', font=('Helvetica', 10, 'bold'), background='#2980b9', foreground='white', borderwidth=1)
style.configure('TLabel', font=('Helvetica', 9, 'normal'), background='#34495e', foreground='white')
style.configure('TProgressbar', thickness=20, relief='flat', background='#3498db', troughcolor='#34495e')

instruction_label = ttk.Label(root, text="Seleccione el directorio de mods o utilice el predeterminado. Use 'Cambiar Directorio' para seleccionar un directorio diferente.",
                              font=('Helvetica', 9), background='#34495e', foreground='white', wraplength=400)
instruction_label.grid(row=0, column=0, columnspan=3, pady=10)

text_area = tk.Text(root, height=10, wrap=tk.WORD, borderwidth=0, relief="flat", state='disabled')
text_area.grid(row=1, column=0, columnspan=3, pady=10, padx=10)
text_area.configure(bg='#34495e', fg='white', font=('Helvetica', 10, 'normal'), insertbackground='white')
text_area.tag_configure('success', foreground='green')
text_area.tag_configure('error', foreground='red')
text_area.tag_configure('info', foreground='blue')
text_area.tag_configure('directory_change', foreground='green')

progress_bar = ttk.Progressbar(root, length=200, mode='determinate')
progress_bar.grid(row=2, column=0, columnspan=3, pady=5, padx=10, sticky='ew')

update_button = ttk.Button(root, text="Actualizar Mods", command=actualizar_mods)
update_button.grid(row=3, column=0, pady=10, padx=10)

change_dir_button = ttk.Button(root, text="Cambiar Directorio", command=change_mod_directory)
change_dir_button.grid(row=3, column=1, pady=10, padx=10)

exit_button = ttk.Button(root, text="Salir", command=root.destroy)
exit_button.grid(row=3, column=2, pady=10, padx=10)

footer_label = ttk.Label(root, text="Developed by jojam", font=('Helvetica', 9, 'bold'))
footer_label.grid(row=4, column=0, pady=10, padx=10, sticky='w')
footer_label.bind("<Button-1>", lambda e: open_github())

version_label = ttk.Label(root, text="Version 1.0.0", font=('Helvetica', 9, 'bold'))
version_label.grid(row=4, column=2, pady=10, padx=10, sticky='e')

root.update_idletasks()
window_width = root.winfo_width()
window_height = root.winfo_height()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
root.geometry(f'+{center_x}+{center_y}')

root.mainloop()
