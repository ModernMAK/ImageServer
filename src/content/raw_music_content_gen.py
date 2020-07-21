import shutil
from typing import List

from src.util import path_util
import os.path

from src.content.content_gen import StaticContentGenerator, GeneratedContentType


class MusicContentGenerator(StaticContentGenerator):
    @staticmethod
    def get_supported_types() -> List[str]:
        return ['mp3', 'wav', 'ogg']

    def generate(self, source_path: str, dest_folder: str, **kwargs):
        ext = path_util.get_formatted_ext(source_path)
        local_copy_path = os.path.join(dest_folder, self.get_file_name(GeneratedContentType.LocalCopy, ext))

        if not os.path.exists(local_copy_path) or kwargs.get('rebuild', False):
            shutil.copyfile(source_path, local_copy_path)

    def get_file_name(self, content_type: GeneratedContentType, source_ext: str):
        if content_type is GeneratedContentType.Thumbnail:
            return None
        return f"LocalCopy.{source_ext}"
