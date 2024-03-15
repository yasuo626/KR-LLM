import pathlib
import os

BASE_DIR=pathlib.Path(r'/work/project/CalcSever')


#  log_utils
LOG_DIR=BASE_DIR/'log'
if not LOG_DIR.exists():
    os.mkdir(LOG_DIR)
LOG_LEVEL=10 # 10:debug,20:info,30:warning,40:error,50:critical



# file
TEST_DOCS_DIR=BASE_DIR/'docs'

SUPPORT_FILE_TYPES=[
    'txt','docx','pdf','html','csv','png','jpg','jpeg','url','md','xlsx'
]



EMBEDDINGS_SIZES=[1536,10]
API={
    'aiproxy':{
        'embedding_model':["text-embedding-ada-002"],
        'embeddings_size':{"text-embedding-ada-002":1536,},
        'llm':["gpt-3.5-turbo","gpt-4","gpt-4-0314","gpt-4-0613"],
    },
    'test':{
        'embedding_model': ["text-embedding-ada-002"],
        'embeddings_size': {"text-embedding-ada-002": 10, },
        'llm': ["gpt-3.5-turbo"],
    }

}

