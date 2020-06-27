from typing import Dict, Optional, Tuple, Union, Callable, List

from PIL import Image
from litespeed import serve, route, register_error_page
from pystache import Renderer

import src.PathUtil as PathUtil
import src.DbMediator as DbUtil

# define renderer
from src.REST import DbRest

renderer = None


def escape_js_string(input: str) -> str:
    input = input.replace('/', '//')
    input = input.replace("'", '/')
    input = input.replace('"', '/"')
    return input


# hardcoded for now
def init():
    global renderer
    renderer = Renderer(search_dirs=PathUtil.html_path("templates"))


@route("/debug(.*)")
def debug(request, path):
    return None
    return serve(PathUtil.html_path("bootstrap_template.html"))


@route("/")
def index(request):
    return show_image_list_index(request)


@route("show/image/index")
def show_image_list_index(request):
    return show_image_list(request, 0)


@route(f"show/image/index/(\d*)")
def show_image_list(request, page: int):
    desired_file = PathUtil.html_image_path("index.html")
    req_imgs = DbUtil.get_imgs(50, page)
    req_tags = DbUtil.get_imgs_tags_from_imgs(req_imgs)

    img_context = parse_rest_image(req_imgs)
    tag_context = parse_rest_tags(req_tags, support_search=True)
    context = {
        'TITLE': "Title",
        'IMG_LIST': img_context,
        'TAG_LIST': tag_context,
    }
    return serve_formatted(desired_file, context)


@route("show/image/search/([\w%'\s]*)", no_end_slash=True)
def show_image_list_search(request, search: str):
    return show_image_list_paged_search(request, 0, search)


@route(f"show/image/search/(\d*)/([\w%'\s]*)", no_end_slash=True)
def show_image_list_paged_search(request, page: int, search: str):
    desired_file = PathUtil.html_image_path("index.html")
    req_imgs = DbUtil.search_imgs(search, 50, page)
    img_id_list = []

    req_tags = DbUtil.get_imgs_tags_from_imgs(req_imgs)

    img_context = parse_rest_image(req_imgs)
    tag_context = parse_rest_tags(req_tags, support_search=True)
    context = {
        'TITLE': "Title",
        'IMG_LIST': img_context,
        'TAG_LIST': tag_context,
        'SEARCH': search,
    }
    return serve_formatted(desired_file, context)


@route(f"show/image/(\d*)")
def show_image(request, img_id):
    desired_file = PathUtil.html_image_path("page.html")
    img_data = DbUtil.get_img(img_id)
    if not img_data:
        return serve_error(404)
    tag_data = DbUtil.get_img_tags(img_id)
    img_context = parse_rest_image(img_data)
    context = {
        'TITLE': "Title",
        'TAG_LIST': parse_rest_tags(tag_data, support_search=True)
    }
    context.update(img_context)
    return serve_formatted(desired_file, context)


@route("show/image/(\d*)/edit")
def show_image_edit(request, img_id):
    desired_file = PathUtil.html_image_path("edit.html")
    img_data = DbUtil.get_img(img_id)
    if not img_data:
        return serve_error(404)
    tag_data = DbUtil.get_img_tags(img_id)

    img_ext, img_w, img_h = img_data
    context = {
        'TITLE': "Title",
        'TAG_LIST': parse_rest_tags(tag_data)
    }
    context.update(parse_rest_image(img_data))
    return serve_formatted(desired_file, context)


@route("show/tag/index")
def show_tag_list_index(request):
    return show_tag_list(request, 0)


def parse_rest_image(imgs: Union[DbRest.RestImage, List[DbRest.RestImage]]) -> Union[
    Dict[str, object], List[Dict[str, object]]]:
    def parse(input_img: DbRest.RestImage):
        return {
            'PAGE_PATH': f"/show/image/{input_img.id}",
            'IMG_ALT': '???',
            'IMG_HEIGHT': input_img.height,
            'IMG_WIDTH': input_img.width,
            'IMG_ID': input_img.id,
            'IMG_EXT': input_img.extension
        }

    if not isinstance(imgs, List):
        return parse(imgs)

    output_rows = []
    for img in imgs:
        output_rows.append(parse(img))
    return output_rows


def parse_rest_tags(tags: Union[DbRest.RestTag, List[DbRest.RestTag]], support_search: bool = False) -> Union[
    Dict[str, object], List[Dict[str, object]]]:
    def parse(input_tag: DbRest.RestTag):
        result = {
            'PAGE_PATH': f"/show/tag/{input_tag.id}",
            'TAG_ID': input_tag.id,
            'TAG_NAME': input_tag.name,
            'TAG_COUNT': input_tag.count,
        }
        if support_search:
            result['TAG_SEARCH_SUPPORT'] = {
                'SEARCH_ID': 'tagsearchbox',
                'ESC_TAG_NAME': escape_js_string(input_tag.name.replace(' ', '_'))
            }
        return result

    if not isinstance(tags, List):
        return parse(tags)

    output_rows = []
    for tag in tags:
        output_rows.append(parse(tag))
    return output_rows


@route("show/tag/index/(\d*)")
def show_tag_list(request, page: int):
    desired_file = PathUtil.html_tag_path("index.html")
    rows = DbUtil.get_tags(50, page)

    fixed_rows = parse_rest_tags(rows)
    context = {'TITLE': "Tags",
               'TAG_LIST': fixed_rows}
    return serve_formatted(desired_file, context)


@route("show/tag/(\d*)/")
def show_tag(request, tag_id):
    desired_file = PathUtil.html_tag_path("page.html")
    result = DbUtil.get_tag(tag_id)
    if not result:
        return serve_error(404)
    (tag_name,) = result

    context = {
        'PAGE_PATH': f"/show/tag/{tag_id}",
        'TAG_ID': tag_id,
        'TAG_NAME': tag_name,
    }
    return serve_formatted(desired_file, context)


@route("show/tag/(\d*)/edit")
def show_tag_edit(request, img_id):
    serve_error(404)


@route("upload/image")
def uploading_image(request):
    desired_file = PathUtil.html_path("upload.html")
    return serve(desired_file)


@route("action/upload_image", methods=['POST'])
def uploading_image(request):
    desired_file = PathUtil.html_path("redirect.html")
    req = request['FILES']
    last_id = None
    for temp in req:
        filename, filestream = req[temp]
        img = Image.open(filestream)
        img_id = DbUtil.add_img(filename, img, PathUtil.image_path("posts"))
        img.close()
        last_id = img_id
    if last_id is not None:
        return serve_formatted(desired_file, {"REDIRECT_URL": f"/show/image/{last_id}"}, )


@route("action/update_tags/(\d*)", methods=['POST'])
def updating_tags(request, img_id: int):
    desired_file = PathUtil.html_path("redirect.html")
    req = request['POST']
    tag_box = req['tags']
    lines = tag_box.splitlines()
    for i in range(0, len(lines)):
        lines[i] = lines[i].strip()
    DbUtil.add_missing_tags(lines)
    DbUtil.set_img_tags(img_id, lines)
    return serve_formatted(desired_file, {"REDIRECT_URL": f"/show/image/{img_id}"}, )


@route("action/image/search", methods=['POST'])
def action_image_search(request):
    desired_file = PathUtil.html_path("redirect.html")
    req = request['POST']
    search = req['search']
    return serve_formatted(desired_file, {"REDIRECT_URL": f"/show/image/search/{search}"}, )


def serve_formatted(file: str, context: Dict[str, object] = None, cache_age: int = 0,
                    headers: Optional[Dict[str, str]] = None,
                    status_override: int = None) -> Tuple[bytes, int, Dict[str, str]]:
    if context is None:
        context = {}

    content, status, header = serve(file, cache_age, headers, status_override)
    fixed_content = renderer.render(content, context)
    return fixed_content, status, header


def serve_error(error_path, context=None) -> Tuple[bytes, int, Dict[str, str]]:
    return serve_formatted(PathUtil.html_path(f"error/{error_path}.html", context))


@register_error_page(404)
def error_404(request, *args, **kwargs):
    return serve(PathUtil.html_path(f"error/{404}.html"))


# has to be loaded LAST
# Will capture EVERYTHING meant for declerations after it
@route("(.*)")
def catchall(request, catch):
    return serve_error(404)
