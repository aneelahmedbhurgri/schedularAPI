import os
import sys
import subprocess
try:
    import shutil
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "shutil"])
    
dist = (os.path.dirname(sys.executable))
dist = dist
try:
    shutil.copy2(dist+"\Lib\site-packages\pywin32_system32\pythoncom37.dll", dist+"\Lib\site-packages\win32\\")
    shutil.copy2(dist+"\Lib\site-packages\pywin32_system32\pywintypes37.dll", dist+"\Lib\site-packages\win32\\")
    shutil.copy2("development.crt", dist+"\Lib\site-packages\win32\\")
    shutil.copy2("development.key", dist+"\Lib\site-packages\win32\\")

except Exception as e:
    print("Error while installing essential files for service.")
    print(e)
