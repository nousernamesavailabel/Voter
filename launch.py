from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

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
print(f"Opening {url}")
driver.get(url)

# Wait to see if the page loads
time.sleep(10)

# Check if the page loaded correctly
if "Viralsweep" in driver.title:  # Adjust this check based on the actual title
    print("Page loaded successfully.")
else:
    print("Page did not load. Trying again...")
    driver.refresh()
    time.sleep(10)

print("Ready to execute JavaScript.")
