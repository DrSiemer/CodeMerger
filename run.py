import webview
import threading
import time
import sys
import src.codemerger

def on_main_window_loaded(window):
    """Callback fired when the main window's content finishes loading."""
    print(f"[LOG] {time.strftime('%H:%M:%S')} - MAIN INTERFACE APPEARED ON SCREEN")

def start_app_logic(main_window):
    """Runs the main application logic in a background thread."""
    print(f"[LOG] {time.strftime('%H:%M:%S')} - Starting heavy application logic...")

    # Simulate your current application startup delay/load
    src.codemerger.main()

    print(f"[LOG] {time.strftime('%H:%M:%S')} - Application logic initialized.")
    # You may need to trigger main_window.show() here if it's hidden
    main_window.show()

def main():
    print(f"[LOG] {time.strftime('%H:%M:%S')} - Initializing Splash Screen...")

    # Create Splash Screen
    splash = webview.create_window(
        'CodeMerger Splash',
        html='<h1 style="text-align:center; font-family:sans-serif;">CodeMerger is loading...</h1>',
        width=400, height=200, frameless=True, hidden=False
    )

    # Create Main Window (Hidden initially)
    print(f"[LOG] {time.strftime('%H:%M:%S')} - Initializing Main Window...")
    main_win = webview.create_window(
        'CodeMerger',
        url='http://localhost:5173',
        width=1200, height=800, hidden=True
    )

    # Bind load event to log when the interface appears
    main_win.events.loaded += lambda: on_main_window_loaded(main_win)

    # Run heavy startup logic in a thread
    thread = threading.Thread(target=start_app_logic, args=(main_win,), daemon=True)
    thread.start()

    print(f"[LOG] {time.strftime('%H:%M:%S')} - Calling webview.start()...")
    webview.start()

    # Once the loop ends (user closes app)
    splash.destroy()
    print(f"[LOG] {time.strftime('%H:%M:%S')} - Application process terminated.")

if __name__ == '__main__':
    main()