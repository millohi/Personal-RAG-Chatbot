# How to setup
1. Setup .env  
Create a .env file at a safe location outside the project directory. The following variables need to be set:
OPENAI_API_KEY=sk-proj-abc123
ALLOWED_CLIENTS=company1:accesscode1,company2:accesscode2  
2. General configurations  
You need to set the domain-name of your api and the path to the .env in the following files:
   - start_ragbot.sh: Set path to .env (1x) & domain (2x)
   - nginx/cert.conf: Set Domain (1x)
   - nginx/https.conf: Set Domain (4x)
   - api/main.py: Set domain of frontend
3. Create your knowledge-base in ragbot/docs/ - As default every company from the .env file has its own knowledge-base. Use one directory for each company (e.g. if you have a company1 then create ragbot/docs/company1/knowledge.md). If you just want to use a single knowledge-base for all companies, then online use the root directory ragbot/docs/ for your md files.
4. Use start_ragbot.sh (after making it executable with chmod +x start_ragbot.sh) to start the ragbot-api automatically (this can take up to 10 minutes).  
If everything works, you can use https://[your-domain].de and should return the info that the ragbot is running. For requests use https://[your-domain].de/chat to call the api. 