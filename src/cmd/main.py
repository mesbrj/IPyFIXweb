import sys, os, logging

src_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir_path = os.path.dirname(src_dir_path)
sys.path.append(src_dir_path)
sys.path.append(project_dir_path)

from startup import file_exporter_startup, webframework_startup

webframework, workers, reload_support = "fastapi", 4, False

if __name__ == "__main__":

    proc_pool, shared_mem = file_exporter_startup()
    logging.info(
        f"file export proc_pool_exec at: {proc_pool.get_instance(only_id=True)} "
        f"file export shared_mem at: {shared_mem.get_instance(only_id=True)}"
    )

    webframework_startup(webframework, workers, reload_support)
