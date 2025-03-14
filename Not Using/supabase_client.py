import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Get .env file
# Please dont commit the .env file I will murder someone
load_dotenv()

# Get env for url + key
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
# Create the connection to supabase
supabase: Client = create_client(url, key)

