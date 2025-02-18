import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
from downloader import MovieDownloader
import threading
import re


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.current_line = ""

    def write(self, string):
        cleaned_string = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', string)
        
        if '\r' in cleaned_string:
            parts = cleaned_string.split('\r')
            self.current_line = parts[-1]
        else:
            self.current_line += cleaned_string

        self.text_widget.after(0, self._update_text)

    def _update_text(self):
        self.text_widget.delete('end-1l', 'end')
        self.text_widget.insert(tk.END, self.current_line + '\n')
        self.text_widget.see(tk.END)

    def flush(self):
        pass


class MainApp:
    def __init__(self, root, torrent_downloader):
        self.root = root
        self.root.title("Main Window")
        self.settings = {"prefix": ""}
        self.td = torrent_downloader
        self.download_thread = None
        
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.name_label = ttk.Label(self.main_frame, text="Name:")
        self.name_label.grid(row=0, column=0, sticky=tk.W)
        
        self.name_entry = ttk.Entry(self.main_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5)
        
        self.submit_btn = ttk.Button(self.main_frame, text="Submit", command=self.on_submit)
        self.submit_btn.grid(row=0, column=2, padx=5)
        
        self.list_frame = ttk.Frame(self.main_frame)
        self.list_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky=tk.W)
        
        self.output_area = scrolledtext.ScrolledText(self.main_frame, height=10, wrap=tk.WORD)
        
        sys.stdout = StdoutRedirector(self.output_area)
        
    def on_submit(self):
        self.clear_list()
        self.output_area.grid_remove()
        
        name = self.name_entry.get()
        
        torrent_list = self.td.get_torrents(name)
        
        for idx, item in enumerate(torrent_list):
            btn = ttk.Button(
                self.list_frame,
                text=f"{self.settings['prefix']} {item}",
                command=lambda x=item: self.on_item_click(torrent_list[x])
            )
            btn.pack(fill=tk.X, pady=2)
    
    def on_item_click(self, param):
        self.clear_list()
        
        links = self.td.get_download_options(param)
        for idx, item in enumerate(links):
            btn = ttk.Button(
                self.list_frame,
                text=f"{self.settings['prefix']} {item}",
                command=lambda x=item: self.on_download_click(links[x])
            )
            btn.pack(fill=tk.X, pady=2)
    
    def on_download_click(self, param):
        self.clear_list()

        self.download_thread = threading.Thread(
            target = self.td.download_torrent,
            args = (param, ),
            daemon = True
        )
        self.download_thread.start()

        self.output_area.grid(row=2, column=0, columnspan=4, sticky=tk.NSEW)
    
    def clear_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    torrent_downloader = MovieDownloader()
    app = MainApp(root, torrent_downloader)
    root.mainloop()