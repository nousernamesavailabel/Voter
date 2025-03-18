import random
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configuration: Adjust wait times as needed
min_wait = 2  # Default: 5
max_wait = 5  # Default: 15
captcha_wait = 15  # Default: 20
reload_wait = 4  # Default: 7

# Setup log file
log_file = "log.txt"

def log_to_file(email):
    """Logs only timestamp and email address to log.txt."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")  # Format: [YYYY-MM-DD HH:MM:SS]
    with open(log_file, "a") as f:
        f.write(f"{timestamp} {email}\n")

def log_message(message):
    """Logs messages to console with a timestamp."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {message}")

# Load and shuffle emails
with open("emails.txt", "r") as file:
    emails = [line.strip() for line in file.readlines() if line.strip()]
random.shuffle(emails)  # Randomize order for natural behavior

total_emails = len(emails)  # Total emails to process

# Setup Chrome options
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)  # Keeps browser open
options.add_argument("--disable-blink-features=AutomationControlled")  # Helps prevent detection
options.add_argument("--no-sandbox")  # Fixes permission issues
options.add_argument("--disable-dev-shm-usage")  # Prevents crashes on some systems
options.add_argument("--start-maximized")  # Opens browser in full screen

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the voting page
url = "https://app.viralsweep.com/vrlswp/embed/20a210-200524?rndid=200524_340302&framed=1&ref=&hsh=&hash="
log_message(f"Opening {url}")
driver.get(url)

# Process each email
for index, email in enumerate(emails, start=1):
    log_message(f"Processing email {index} of {total_emails} ({email})")  # Progress tracker

    wait_time = random.randint(min_wait, max_wait)  # Randomized delay before voting
    log_message(f"Waiting {wait_time} seconds before selecting BEACHMONT entry...")
    time.sleep(wait_time)  # Simulate human-like behavior

    log_to_file(email)  # Log email to file

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
    log_message(f"Executed script for {email}. Waiting for CAPTCHA input...")

    time.sleep(captcha_wait)  # Allow time for CAPTCHA completion
    log_message(f"Waiting for page refresh before next email ({index + 1} of {total_emails})...")

    time.sleep(reload_wait)  # Wait for page reload

log_message("All emails processed. Closing browser.")
driver.quit()
