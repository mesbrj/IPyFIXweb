import sys, os
src_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir_path = os.path.dirname(src_dir_path)
sys.path.append(src_dir_path)
sys.path.append(project_dir_path)

if __name__ == "__main__":
    from startup import init_app, webapp_startup
    init_app()
    webapp_startup(workers=3)
