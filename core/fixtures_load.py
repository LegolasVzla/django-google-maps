import os
import subprocess
from core.settings import BASE_DIR

def loaddata():
	subprocess.call("python3 manage.py loaddata fixtures/"+'types_user_action.json',shell=True)

loaddata()
