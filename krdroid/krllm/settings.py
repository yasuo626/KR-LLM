


import pathlib
import sys
import os


# system

sys.path.append("../")




from .core.file_loader import FILE_LOADERS,FileLoader
from .config import SUPPORT_FILE_TYPES,EMBEDDINGS_SIZES

base_loader=FileLoader(FILE_LOADERS,SUPPORT_FILE_TYPES)

from .core.text_spliter import ChineseTextSplitter,CharacterTextSplitter,LineTextSplitter

base_splitter=LineTextSplitter()




# api
from .core.api import AiproxyAPI,OpenaiAPI,LocalModelAPI,TestModelAPI,MultiModelAPI
APIS={
    'openai':OpenaiAPI(api_key="",base_url=""),
    'test':TestModelAPI(api_key="sk-xVFfhXvnpu4k9VUgKiVS8FS2ODytKG8eqWxS4hBOmgK8o6Vv",base_url="https://api.aiproxy.io/v1"),
    'aiproxy':AiproxyAPI(api_key="sk-xVFfhXvnpu4k9VUgKiVS8FS2ODytKG8eqWxS4hBOmgK8o6Vv",base_url="https://api.aiproxy.io/v1"),
    'local':LocalModelAPI(api_key="",base_url=""),
}
base_api=MultiModelAPI(APIS)


# api_key="sk-xVFfhXvnpu4k9VUgKiVS8FS2ODytKG8eqWxS4hBOmgK8o6Vv"
# base_url="https://api.aiproxy.io/v1"

# db
from .core.vdb import MilvusDB,MilvusCollection,get_FileAbstract_fields
base_db=MilvusDB(host="127.0.0.1",port='19530')
for embeddings_size in EMBEDDINGS_SIZES:
    if not base_db.has_collection(f'FileAbstract_{embeddings_size}'):
        base_db.create_collection(f"FileAbstract_{embeddings_size}",get_FileAbstract_fields(embeddings_size),f"FileAbstract_{embeddings_size}")
        kb_collection=base_db.get_collection(f"FileAbstract_{embeddings_size}")
        MilvusCollection(kb_collection,f"FileAbstract",f"{embeddings_size}").update_index('embeddings')


