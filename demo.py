import os
from dotenv import load_dotenv

load_dotenv()

linkedin_username = os.getenv("USERNAME2")
linkedin_password = os.getenv("PASSWORD")

print(linkedin_username, linkedin_password)