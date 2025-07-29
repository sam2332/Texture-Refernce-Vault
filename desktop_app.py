#!/usr/bin/env python3
"""
Tkinter Desktop wrapper for Texture Reference Vault Flask application.
This is a fallback version using Tkinter (built into Python) when PyQt6/PySide6 fails.
"""

import sys
import threading
import time
import os
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import requests
from urllib.parse import urlparse

# Import your Flask app
from app import create_app

class TextureVaultDesktop:
    def __init__(self):
        self.flask_app = None
        self.flask_thread = None
        self.port = 5000
        self.root = tk.Tk()
        
        self.init_ui()
        self.start_flask_server()
        
    def init_ui(self):
        """Initialize the Tkinter user interface"""
        self.root.title("Texture Reference Vault")
        self.root.geometry("400x150")
        self.root.resizable(False, False)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Texture Reference Vault", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Starting Flask server...")
        self.status_label.pack(pady=(0, 15))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        # Open in browser button
        self.open_button = ttk.Button(button_frame, text="Open", 
                                     command=self.open_in_browser, state='disabled',
                                     width=12)
        self.open_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_application,
                                     width=12)
        self.stop_button.pack(side=tk.LEFT)
        
        # Start checking Flask server
        self.check_flask_server()
        
    def stop_application(self):
        """Stop the application"""
        try:
            # Send shutdown request to Flask server
            requests.post(f'http://127.0.0.1:{self.port}/shutdown', timeout=1)
        except:
            pass  # Server might already be stopped
        
        self.root.quit()
        self.root.destroy()
    
    def start_flask_server(self):
        """Start Flask server in a separate thread"""
        def run_flask():
            try:
                self.flask_app = create_app('development')
                self.flask_app.run(host='127.0.0.1', port=self.port, debug=False, use_reloader=False)
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"Flask server error: {str(e)}"))
        
        self.flask_thread = threading.Thread(target=run_flask, daemon=True)
        self.flask_thread.start()
        
        # Start periodic status check
        self.root.after(1000, self.periodic_check)
    
    def periodic_check(self):
        """Periodically check Flask server status"""
        self.check_flask_server()
        self.root.after(2000, self.periodic_check)  # Check every 2 seconds
    
    def check_flask_server(self):
        """Check if Flask server is ready"""
        try:
            response = requests.get(f'http://127.0.0.1:{self.port}', timeout=1)
            if response.status_code == 200:
                self.status_label.config(text="✅ Server running")
                self.open_button.config(state='normal')
            else:
                self.status_label.config(text="⚠️ Server error")
        except requests.exceptions.RequestException:
            self.status_label.config(text="🔄 Starting server...")
            self.open_button.config(state='disabled')
    
    def open_in_browser(self):
        """Open the Flask application in the default web browser"""
        url = f'http://127.0.0.1:{self.port}'
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open browser: {str(e)}")
    
    def run(self):
        """Start the Tkinter main loop"""
        self.root.mainloop()

def main():
    """Main application entry point"""
    try:
        app = TextureVaultDesktop()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Error", f"Application failed to start: {str(e)}")

if __name__ == '__main__':
    main()
