from litespeed import route

from src.Routing.Pages import errors
from src.Routing.Pages.file_page_group import FilePageGroup


def initialize_module(**kwargs):
    FilePageGroup.initialize(**kwargs)
    errors.initialize_module(**kwargs)


# hardcoded for now
def add_routes():
    errors.add_routes()
    FilePageGroup.add_routes()
    # Index page, can be replaced by a proper index
    route('/',f= FilePageGroup.as_route_func(FilePageGroup.index), methods=['GET'])
