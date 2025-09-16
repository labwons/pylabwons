#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# ON GOOGLE COLAB, THIS SECTION MUST BE INITIALIZED. IT TAKES ABOUT 2MINUTES.
# AFTER RUNNING THIS SECTION, RUNTIME(SESSION) MUST BE RESTARTED, IN ORDER TO
# USE labwons/ PACKAGE. SESSION RESTART HOTKEY IS CTRL + M.
import os
if any("COLAB" in e for e in os.environ):
    get_ipython().system('git clone https://github.com/labwons/pylabwons.git')
    if not os.getcwd().endswith('pylabwons'):
        get_ipython().run_line_magic('cd', 'pylabwons')
    get_ipython().system('pip install -e .')


# In[2]:


import os

ACTION = os.environ.get("GITHUB_EVENT_NAME", "LOCALHOST").upper()
HOSTID = os.environ.get("USERDOMAIN", "COLAB") if ACTION == "LOCALHOST" else "GITHUB"


# In[ ]:


from pylabwons.fetch import Tickers
from pylabwons.util import Logging

logger = Logging()
market = Tickers(logger=logger)
market.fetch()


# In[3]:


# WARNING.
# IF YOU RUN THIS SECTION ON COLAB, ALL THE ADDED AND MODIFIED FILES ARE TO BE COMMITTED
# AND PUSHED TO GIT. YOU RUN THIS SECTION IF AND ONLY IF YOU WANT TO UPDATE THROUGH COLAB.
if HOSTID == "COLAB":
    from google.colab import drive
    from json import load
    drive.mount('/content/drive')

    with open(r"/content/drive/MyDrive/secrets.json") as secrets:
        os.environ.update(load(secrets))

    if not os.getcwd().endswith('pylabwons'):
        get_ipython().run_line_magic('cd', 'pylabwons')

    get_ipython().system('git config --global user.name "$GITHUB_USER"')
    get_ipython().system('git config --global user.email "$GUTHUB_EMAIL"')
    get_ipython().system('git remote set-url origin "https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/pylabwons.git"')
    get_ipython().system('git add .')
    get_ipython().system('git commit -m "COMMIT AND PUSH FROM COLAB"')
    get_ipython().system('git push origin main')

