import shutil
from typing import List

from src.util import path_util
import os.path
from pdf2image import pdf2image

from src.content.content_gen import AbstractContentGenerator, GeneratedContentType
from depends.LibreOffice.soffice import SOffice


class LibreOfficeContentGenerator(AbstractContentGenerator):

    @staticmethod
    def get_supported_types() -> List[str]:
        # Supports pdf-like files
        return [
            'doc', 'dot', 'wbk', 'docx', 'dotx', 'dotm', 'docb',  # WORD
            'xls', 'xlt', 'xlm', 'xlsx', 'xlsm', 'xltx', 'xltm',  # EXCEL
            'ppt', 'pit', 'pps', 'pptx', 'pptm', 'potx', 'potm', 'ppam', 'ppsx', 'ppsm', 'sldx', 'sldm',  # POWER POINT
            'pub',  # PUBLISHER
            'odt', 'ods', 'odp', 'odg',  # OPEN DOC

            'txt', 'csv',  # TEXT LIKE
        ]

    @staticmethod
    def __get_thumbnail_ext(ext: str) -> str:
        return 'jpeg'

    @staticmethod
    def __get_viewable_ext(ext: str) -> str:
        return 'pdf'

    def generate(self, source_path: str, dest_folder: str, **kwargs):
        ext = path_util.get_formatted_ext(source_path)
        thumbnail_path = os.path.join(dest_folder, self.get_file_name(GeneratedContentType.Thumbnail, ext))
        viewable_path = os.path.join(dest_folder, self.get_file_name(GeneratedContentType.Viewable, ext))
        local_copy_path = os.path.join(dest_folder, self.get_file_name(GeneratedContentType.LocalCopy, ext))

        if all(os.path.exists(path) for path in [thumbnail_path, viewable_path, local_copy_path]) and not kwargs.get(
                'rebuild', False):
            return

        if not os.path.exists(thumbnail_path) or kwargs.get('rebuild', False):
            SOffice.convert_to_format(source_path, thumbnail_path, format='jpeg')
            # with
            # thumbnail = thumbnails[0]
            # thumbnail.thumbnail((256,256))
            # thumbnail.save(thumbnail_path)
            # thumbnail.close()
        if not os.path.exists(viewable_path) or kwargs.get('rebuild', False):
            SOffice.convert_to_format(source_path, viewable_path, format='pdf')

        if not os.path.exists(local_copy_path) or kwargs.get('rebuild', False):
            shutil.copyfile(source_path, local_copy_path)

    def get_file_name(self, content_type: GeneratedContentType, source_ext: str):
        if content_type is GeneratedContentType.Thumbnail:
            content_ext = LibreOfficeContentGenerator.__get_thumbnail_ext(source_ext)
            return f"Thumbnail.{content_ext}"
        if content_type is GeneratedContentType.LocalCopy:
            return f"LocalCopy.{source_ext}"
        if content_type is GeneratedContentType.Viewable:
            content_ext = LibreOfficeContentGenerator.__get_viewable_ext(source_ext)
            return f"Viewable.{content_ext}"
