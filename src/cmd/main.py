import sys, os
src_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir_path = os.path.dirname(src_dir_path)
sys.path.append(src_dir_path)
sys.path.append(project_dir_path)

from startup import webframework_startup

# From config or app cli arguments
webframework = "fastapi"
workers = 4
reload_support = False

if __name__ == "__main__":
    webframework_startup(webframework, workers, reload_support)
