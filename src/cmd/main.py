import sys, os
sys.path.append(
    os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))
)
from startup import webframework_startup

webframework = "fastapi" # From config or cli

if __name__ == "__main__":
    webframework_startup(webframework)
