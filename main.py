import threading
import tkinter as tk
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from datetime import datetime

# Configuration
min_wait = 1 #default 5
max_wait = 4 #default 15
captcha_wait = 10 #default 20
reload_wait = 3 #default 7

# Load emails and shuffle
with open("emails.txt", "r") as file:
    emails = [line.strip() for line in file.readlines() if line.strip()]
random.shuffle(emails)

# Setup Chrome options
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")

# Global Variables
driver = None
running = False  # Controls execution
paused = False   # Controls pause state
processed_count = 0  # Track progress
voting_thread = None  # Store reference to thread

# Log file setup
log_file = "log.txt"

def log_to_file(email):
    """Logs timestamp and email to log.txt."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_file, "a") as f:
        f.write(f"{timestamp} {email}\n")

def log_message(message):
    """Updates progress label in GUI."""
    status_label.config(text=message)
    root.update_idletasks()

def update_progress():
    """Updates progress bar and displays processed count out of total emails."""
    progress_var.set(processed_count)
    progress_label.config(text=f"Processed {processed_count}/{len(emails)} emails")
    root.update_idletasks()

def process_votes():
    """Main function to process votes."""
    global running, paused, processed_count, driver

    if running:
        return  # Prevent multiple starts

    running = True

    if driver is None:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        url = "https://app.viralsweep.com/vrlswp/embed/20a210-200524?rndid=200524_340302&framed=1&ref=&hsh=&hash="
        log_message(f"Opening {url}")
        driver.get(url)

    while processed_count < len(emails):
        if not running:
            break  # Stop loop if "Stop" is pressed

        while paused:
            log_message("Paused...")
            time.sleep(1)  # Wait while paused

        email = emails[processed_count]
        wait_time = random.randint(min_wait, max_wait)
        log_message(f"Waiting {wait_time} seconds before selecting BEACHMONT entry...")
        time.sleep(wait_time)

        log_message(f"Processing email {processed_count + 1}/{len(emails)}: {email}")
        log_to_file(email)

        js_script = f"""
        function startVoting() {{
            function waitForElement(selector, callback, interval = 500, maxAttempts = 20) {{
                let attempts = 0;
                let checkExist = setInterval(() => {{
                    let element = document.querySelector(selector);
                    if (element) {{
                        clearInterval(checkExist);
                        callback(element);
                    }}
                    attempts++;
                    if (attempts >= maxAttempts) {{
                        clearInterval(checkExist);
                        console.log(selector + " did not appear.");
                    }}
                }}, interval);
            }}

            let email = "{email}";
            let button = document.querySelector(".zoom.gallery-view-image[data-id='928107']");
            if (button) {{
                button.click();
                console.log("Clicked the BEACHMONT entry.");
                waitForElement(".collect_email", (emailInput) => {{
                    emailInput.value = email;
                    emailInput.dispatchEvent(new Event("input", {{ bubbles: true }}));
                    emailInput.dispatchEvent(new Event("change", {{ bubbles: true }}));
                    console.log("Email entered successfully.");
                    waitForElement(".submit.do_vote", (voteButton) => {{
                        voteButton.click();
                        console.log("Clicked the 'Vote Now' button.");
                        waitForElement("[name='cf-turnstile-response'], .g-recaptcha-response", (captchaField) => {{
                            console.log("Waiting for CAPTCHA completion...");
                            let observer = new MutationObserver(() => {{
                                if (captchaField.value.trim()) {{
                                    observer.disconnect();
                                    console.log("CAPTCHA completed! Clicking vote button again...");
                                    waitForElement(".submit.do_vote", (finalVoteButton) => {{
                                        finalVoteButton.click();
                                        console.log("Final vote submitted!");
                                        setTimeout(() => {{
                                            console.log("Refreshing page for next email...");
                                            location.reload();
                                        }}, 5000);
                                    }});
                                }}
                            }});
                            observer.observe(captchaField, {{ attributes: true, attributeFilter: ["value"] }});
                        }});
                    }});
                }});
            }} else {{
                console.log("BEACHMONT entry button not found.");
            }}
        }}
        startVoting();
        """
        driver.execute_script(js_script)

        log_message(f"Script executed for {email}. Waiting for CAPTCHA...")
        time.sleep(captcha_wait)

        processed_count += 1
        update_progress()  # Update progress bar with numbers

        time.sleep(reload_wait)

    log_message("All emails processed.")
    running = False
    driver.quit()

def start_voting():
    """Starts or resumes the voting process in a separate thread."""
    global running, voting_thread

    if running:
        return  # Don't start if already running

    voting_thread = threading.Thread(target=process_votes, daemon=True)
    voting_thread.start()

def pause_voting():
    """Toggles the pause state."""
    global paused
    paused = not paused
    pause_button.config(text="Resume" if paused else "Pause")
    log_message("Paused" if paused else "Resumed")

def stop_voting():
    """Stops the voting process."""
    global running, driver
    running = False
    if driver:
        driver.quit()
    log_message("Stopped")

# Create GUI
root = tk.Tk()
root.title("Auto Voting Bot")

frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

# Status label
status_label = tk.Label(frame, text="Click Start to Begin", font=("Arial", 12))
status_label.pack(pady=10)

# Progress number label
progress_label = tk.Label(frame, text=f"Processed {processed_count}/{len(emails)} emails", font=("Arial", 12))
progress_label.pack(pady=5)

# Progress bar
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(frame, length=300, mode="determinate", maximum=len(emails), variable=progress_var)
progress_bar.pack(pady=5)

# Control buttons
btn_frame = tk.Frame(frame)
btn_frame.pack()

start_button = tk.Button(btn_frame, text="Start", command=start_voting, bg="green", fg="white", width=10)
start_button.pack(side="left", padx=5)

pause_button = tk.Button(btn_frame, text="Pause", command=pause_voting, bg="yellow", fg="black", width=10)
pause_button.pack(side="left", padx=5)

stop_button = tk.Button(btn_frame, text="Stop", command=stop_voting, bg="red", fg="white", width=10)
stop_button.pack(side="left", padx=5)

# Run the GUI
root.mainloop()
