import sys, os
src_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
repo_dir_path = os.path.dirname(src_dir_path)
sys.path.append(src_dir_path)
sys.path.append(repo_dir_path)

from startup import webframework_startup

# From config or cli
webframework = "fastapi"
workers = 6
reload_support = True

if __name__ == "__main__":
    webframework_startup(webframework, workers, reload_support)
