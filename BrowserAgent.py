import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent,ChatGoogle
from playwright.sync_api import sync_playwright

load_dotenv()

with sync_playwright() as p:
        chromium_path = p.chromium.executable_path
        print(chromium_path)

HISTORY_FILE = "browser_agent_urls.txt"
MAX_RETRIES = 3  # Number of times to retry the browser agent

async def main():

    # Instantiate the Google Gemini model
    llm = ChatGoogle(model="gemini-2.5-flash")
    task = "Search Google for 'what is browser automation' and tell me the top 3 results"
    chrome_path = "/Users/rahuldev/Library/Caches/ms-playwright/chromium-1187/chrome-mac/Chromium.app/Contents/MacOS/Chromium"

    # Create the Agent in headful mode
    agent = Agent(
        task=task,
        llm=llm,
        browser_path=chrome_path,
        headless=True,            # headless mode
        extensions=[],            # skip extensions to avoid SSL errors
        track_tokens=False,
        profile_options={         # Pass launch options directly
            "headless": True,
            "args": [
                "--disable-gpu",
                "--no-sandbox",
                "--disable-extensions"
            ]
        }
    )



    urls = []

    # Retry logic
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt} running browser agent...")
            history = await agent.run()  # Returns AgentHistoryList
            urls = history.urls()

            # Check if URLs are valid (not all 'about:blank')
            if urls and not all(u == "about:blank" for u in urls):
                print("Browser agent succeeded.")
                break
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            urls = []

    # Fallback to LLM if browser agent fails completely
    if not urls or all(u == "about:blank" for u in urls):
        print("Browser agent failed, generating URLs using the LLM...")
        prompt = (
            "List the top 3 official URLs for understanding 'browser automation'. "
            "Only URLs, separated by commas."
        )
        fallback_result = await llm.agenerate([prompt])
        urls = [u.strip() for u in fallback_result.generations[0][0].text.split(",")]

    # Save URLs to text file
    with open(HISTORY_FILE, "a") as f:
        for url in urls:
            f.write(url + "\n")

    print("Task completed. URLs saved to", HISTORY_FILE)
    print(urls)


if __name__ == "__main__":
    asyncio.run(main())
