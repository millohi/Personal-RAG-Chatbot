# How to setup
1. Setup .env  
Create a .env file at a safe location outside the project directory. The following variables need to be set:
OPENAI_API_KEY=sk-proj-abc123
ALLOWED_CLIENTS=company1:accesscode1,company2:accesscode2  
2. General configurations  
You need to set the domain-name of your api and the path to the .env in the following files:
   - start_ragbot.sh: Set path to .env (1x) & domain (1x)
   - nginx/cert.conf: Set Domain (1x)
   - nginx/https.conf: Set Domain (4x)
3. Create your database in ragbot/docs/. You can use the empty knowledge-base.md or use any other .md file.
4. Use start_ragbot.sh (after making it executable with chmod +x start_ragbot.sh) to start the ragbot-api automatically (this can take up to 10 minutes).  
If everything works, you can use https://domain.de and should return the info that the ragbot is running. For requests use https://domain.de/chat to call the api. 