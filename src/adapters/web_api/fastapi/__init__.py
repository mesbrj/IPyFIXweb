import sys, os

web_api_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.dirname(os.path.dirname(web_api_dir))

sys.path.append(src_dir)

