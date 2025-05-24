# 41030 Engineering Capstone
Autumn 2025

# Supervisor
- **Matthias Guertler**

# Team
- **Victor Yang** - 14397842
- **Osasere Eguaibor** - 13623549

# Project Details
The aim of this project is to train LLM to evaluate a set of individual requirements 
as per the INCOSE guidelines, containing a set of characteristics and rules each requirement
shall adhere to (depending on context). 

The model will provide a compliance rating after analyzing the requirements, and and explanation
of why it complies/doesn't comply. With a final step being rephrasing the requirement statement to
adhere to non-complied rules within a particular characteristic.


##Services Overview
### webui
- **Image**: `ghcr.io/open-webui/open-webui:main`
- **Function**: Serves as the web interface for interacting with the Ollama AI models.
- **Customization**: Adjust `OLLAMA_API_BASE_URL` to match the internal network URL of the `ollama` service. If running `ollama` on the docker host, comment out the existing `OLLAMA_API_BASE_URL` and use the provided alternative.

### ollama (Optional if you are running ollama on the docker host)
- **Image**: `ollama/ollama`
- **Function**: Acts as the AI model server, with the capability to utilize NVIDIA GPUs for model inference.
- **GPU Utilization**: Configured to use NVIDIA GPUs to ensure efficient model inference. Verify your system's compatibility.

### tunnel
- **Image**: `cloudflare/cloudflared:latest`
- **Function**: Provides a secure tunnel to the web UI via Cloudflare, enhancing remote access security.
- **Note**: We are using the demo mode by default, so the URL will change each time you restart unless you create an account with cloudflaree

# Tutorials
## Configure Open WebUI to Use Apache Tika 
To use Apache Tika as the context extraction engine in Open WebUI, follow these steps:

Log in to your Open WebUI instance.
Navigate to the Admin Panel settings menu.
Click on Settings.
Click on the Documents tab.
Change the Default content extraction engine dropdown to Tika.
Update the context extraction engine URL to http://tika:9998.
Save the changes.

**How it works**
1. Verify-tika.py parses documents from the "documents" folder for it to be read. 
2. Run the script using the following command: python verify_tika.py
3. The script will output a message indicating whether Apache Tika is working correctly


## Configuration and Deployment

1. **Volumes**: Two volumes, `ollama` and `open-webui`, are defined for data persistence across container restarts.

2. **Environment Variables**: Ensure `OLLAMA_API_BASE_URL` is correctly set. Utilize the `host.docker.internal` address if `ollama` runs on the Docker host.

3. **Deployment**:
    - Run `docker compose up -d` to start the services in detached mode.

4. **Accessing the Web UI**:
    - Directly via `http://localhost:8080` if local access is sufficient.
    - Through the Cloudflare Tunnel URL printed in the docker logs. Run `docker compose logs tunnel` to find the URL for remote access
