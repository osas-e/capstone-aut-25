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



## Configure Open WebUI to Use Apache Tika
To use Apache Tika as the context extraction engine in Open WebUI, follow these steps:

Log in to your Open WebUI instance.
Navigate to the Admin Panel settings menu.
Click on Settings.
Click on the Documents tab.
Change the Default content extraction engine dropdown to Tika.
Update the context extraction engine URL to http://tika:9998.
Save the changes.
