import sys, os
src_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir_path = os.path.dirname(src_dir_path)
sys.path.append(src_dir_path)
sys.path.append(project_dir_path)

from startup import file_exporter_startup, webframework_startup

webframework, workers, reload_support = "fastapi", 4, False

if __name__ == "__main__":
    proc_pool, shared_mem = file_exporter_startup()
    webframework_startup(webframework, workers, reload_support)
