from time import sleep
from typing import List

from litespeed import start_with_args
import src.routing.virtual_access_points as Vap
import src.routing.rest as rest
import src.routing.web_pages as WebPages
from src.content import content_gen_startup
import src.file_watching.db_watcher as DbWatcher
from src.util import dict_util
from src.util.db_util import Conwrapper
from src.util.dict_util import DictFormat


# def launch_prep(**kwargs):
#     watch_paths = kwargs.get('watch_paths', None)
#     if watch_paths is not None:
#         print("Adding Missing Files")
#         for path in watch_paths:
#             DbMaintenence.add_all_files(path)
#             DbMaintenence.fix_missing_pages()
#             DbMaintenence.rebuild_missing_file_generated_content(supress_error_ignore=False)
#         print("Finished Adding Initial Files")
#     print("Creating Missing Meta Files")
#     DbMaintenence.gen_missing_meta_files()
#     print("Finished Creating Missing Meta Files")

def rebuild_db(db_path):
    with open("web/data/table_script.v2.txt") as f:
        full_query = f.read()
        separated_queries = full_query.split(';')
        with Conwrapper(db_path) as (conn, curs):
            for query in separated_queries:
                curs.execute(query)
            conn.commit()


if __name__ == '__main__':
    try:
        settings = dict_util.read_dict('settings.ini', DictFormat.ini)
        if settings is None:
            settings = {}
    except FileNotFoundError:
        settings = {}
    try:
        configs = dict_util.read_dict('config.ini', DictFormat.ini)
        if configs is None:
            configs = {}
    except FileNotFoundError:
        configs = {}

    content_gen_startup.initialize_content_gen()
    rebuild_db(configs.get('Launch Args', {}).get('db_path'))

    WebPages.initialize_module(settings=settings, config=configs)
    watcher = DbWatcher.create_database_watchman(config=configs)
    paths = settings.get('Watch', {}).get('paths', None)
    if paths:
        path_list = paths.split('\n')
        for path in path_list:
            print(f"Watching ~ {path}")
            watcher.watch(path, True)

    Vap.RequiredVap.add_to_vap()
    rest.initialize_module(settings=settings, config=configs)
    Vap.VirtualAccessPoints.add_routes()
    # api.add_routes()
    rest.add_routes()
    WebPages.add_routes()

    # launch_prep(watch_paths=path_list)
    watcher.start(True)
    start_with_args()
    watcher.observer.join()
