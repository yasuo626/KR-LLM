import os
import pathlib

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from django.shortcuts import redirect

from utils import request2json,keys1_in_keys2,file_to_name_type
from .models import File,KnowledgeBase,FileUploadForm,ChatModel
import requests, json
import datetime
from CalcSever.settings import MEDIA_ROOT,MAX_UPLOAD_FILE_SIZE
from krdroid.krllm.config import SUPPORT_FILE_TYPES,API
from .krllm.settings import base_api,base_db,base_loader,base_splitter
from .krllm import file_vdb_upload,file_vdb_delete,kb_vdb_create,kb_vdb_delete,kb_vdb_add_files,kb_vdb_drop_files,kb_vdb_get_files,text2embeddings,search_knowledges,get_msg
from .krllm.core.chat import Chat,Message,get_query_format

def test(request):
    if request.method == 'POST':
        pass
        # file = request.FILES['file']
        # path = os.path.join('/work/project/CalcSever/media/uploads/', file.name)
        # with open(path, 'wb+') as destination:
        #     for chunk in file.chunks():
        #         destination.write(chunk)
        # return render(request, 'apidocs/index.html')  # 渲染上传文件的表单页面
    return render(request, 'test.html')  # 渲染上传文件的表单页面

    # content=""
    # with open('./test.txt',mode='at+') as f:
    #     content=requests.post('http://localhost:8000/krdroid/file_upload',json={'user_name':"test","files":{"t.txt": open('./docs/t.txt', 'rb')}}).json() # request.body is bin
    #     # f.write(str(content.content))
    # return JsonResponse(content)


def file_to_uploads(username,file,file_path, support_file_types, max_file_size):
    file_type = file.name.split('.')[-1]
    if file_type not in support_file_types or file.size > max_file_size:
        return False
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return True

def file_get(request):
    if request.method == "GET":
        return redirect('../apidocs/')

    response={"state":0,"error_info":""}
    if request.method == "POST":
        username = request.POST.get('username')
        files=[]
        for file in File.objects.filter(user_name=username):
            files.append({'name':file.name[len(username)+1:],'type':file.type,'size':file.size,'api':file.api,'embedding_model':file.embedding_model,'create_time':file.ctime})
        response['files']=files
        return JsonResponse(response)
    response["state"]=1
    response["error_info"]=f"request method {request.method}!=POST"
    return JsonResponse(response)

def file_get_detail(request):
    if request.method == "GET":
        return redirect('../apidocs/')

    response={"state":0,"error_info":""}
    if request.method == "POST":
        username = request.POST.get('username')
        filename = request.POST.get('filename')
        name, type = file_to_name_type(filename)
        filename = username + "_" + name + "." + type
        file=File.objects.filter(name=filename)
        if not file.exists():
            response['state']=1
            response['error_info']="file does not exists"
            return JsonResponse(response)
        response['detail']={'name':file[0].name,'type':file[0].type,'size':file[0].size,'api':file[0].api,'embedding_model':file[0].embedding_model,
                            'embeddings_size':file[0].embeddings_size,'count':file[0].count,'create_time':file[0].ctime,'update_time':file[0].utime}
        return JsonResponse(response)
    response["state"]=1
    response["error_info"]=f"request method {request.method}!=POST"
    return JsonResponse(response)

def file_upload(request):
    if request.method == "GET":
        return redirect('../apidocs/')

    response={"state":0,"error_info":""}
    if request.method == "POST":
        username = request.POST.get('username')
        form = FileUploadForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')
        api=request.POST.get('api') #
        embedding_model = request.POST.get('embedding_model')
        if(api not in API.keys()):
            response["state"] = 1
            response["error_info"] = f"api does not exists"
            return JsonResponse(response)
        if(embedding_model not in API[api]["embedding_model"]):
            response["state"] = 1
            response["error_info"] = f"embedding_model does not exists"
            return JsonResponse(response)
        embeddings_size=API[api]["embeddings_size"][embedding_model]


        # upload file
        if not form.is_valid():
            response["state"] = 1
            response["error_info"] = f"form error"
        file_states=[]
        for file in files:
            name,type=file_to_name_type(file.name)
            filename=username+"_"+name+"."+type

            if File.objects.filter(name=filename).exists():
                file_states.append({'name':file.name,'state':0,'error_info':"file already exists"})
                continue
            file_path=os.path.join(MEDIA_ROOT,f'uploads/{filename}')
            if file_to_uploads(username,file,file_path,SUPPORT_FILE_TYPES,MAX_UPLOAD_FILE_SIZE):
                file_obj=File(filename,type,username,file.size,file_path,api,embedding_model,embeddings_size,0)
                file_obj.save()
                file_states.append({'name':file.name,'state':0,'error_info':""})
            else:
                file_states.append({'name':file.name,'state':1,'error_info':"file upload fail,check the file type and the file size"})

        # process file
        upload_path=os.path.join(MEDIA_ROOT,'uploads')


        for file in file_states:
            if file['state']:
                continue
            file_name=file['name']
            name,type=file_to_name_type(file_name)
            file_path=pathlib.Path(os.path.join(upload_path,username+'_'+file_name))

            if not file_vdb_upload(username,name,type,file_path,
                base_api=base_api,api=api,model=embedding_model,db=base_db,loader=base_loader,splitter=base_splitter):
                file['state']=1
                file['error_info']="embedding process fail"
        response['file_states']=file_states
        return JsonResponse(response)
    response["state"]=1
    response["error_info"]=f"request method {request.method}!=POST"
    return JsonResponse(response)

def file_delete(request):
    if request.method == "GET":
        return redirect('../apidocs/')

    response={"state":0,"error_info":""}
    if request.method == "POST":
        username = request.POST.get('username')
        file_names = request.POST.getlist('files')


        file_states = []
        file_embeddings_sizes={}
        for file_name in file_names:
            name,type=file_to_name_type(file_name)
            filename=username+"_"+name+"."+type
            file_obj=File.objects.filter(name=filename)
            if not file_obj.exists():
                file_states.append({'name':file_name,'state':0,'error_info':"file does not exists"})
                continue
            if file_obj[0].count>0:
                file_states.append({'name':file_name,'state':1,'error_info':"file is referenced by other knowledge base"})
                continue
            file_embeddings_sizes[filename]=file_obj[0].embeddings_size
            file_obj.delete()
            file_path=os.path.join(MEDIA_ROOT,f'uploads/{filename}')
            os.remove(file_path)
            file_states.append({'name': file_name, 'state': 0, 'error_info': ""})

        # process file


        for file in file_states:
            file_name=file['name']
            name,type=file_to_name_type(file_name)
            filename=username+"_"+name+"."+type
            if filename not in file_embeddings_sizes.keys():
                continue
            embeddings_size=file_embeddings_sizes[filename]
            if not file_vdb_delete(username,name,type,embeddings_size,base_db):
                file['state']=1
                file['error_info']="embedding delete fail"
        response['file_states']=file_states
        return JsonResponse(response)
    response["state"]=1
    response["error_info"]=f"request method {request.method}!=POST"
    return JsonResponse(response)

def kb_get(request):
    if request.method == "GET":
        return redirect('../apidocs/')

    response={"state":0,"error_info":""}
    if request.method == "POST":
        username = request.POST.get('username')
        kbobjs=KnowledgeBase.objects.filter(user_name=username)
        kb_list = [{'name': obj.name, 'api': obj.api, 'llm': obj.llm,'embedding_model':obj.embedding_model} for obj in kbobjs]
        response["kb_list"] = kb_list
        return JsonResponse(response)
    response["state"]=1
    response["error_info"]=f"request method {request.method}!=POST"
    return JsonResponse(response)

def kb_get_detail(request):
    if request.method == "GET":
        return redirect('../apidocs/')

    response={"state":0,"error_info":""}
    if request.method == "POST":
        kbname = request.POST.get('kbname')
        username = request.POST.get('username')
        kb=KnowledgeBase.objects.filter(name=kbname)
        if not kb.exists():
            response['state']=1
            response['error_info']="kb does not exists"
            return JsonResponse(response)
        response['detail']={'name':kb[0].name,'api':kb[0].api,'llm':kb[0].llm,'embedding_model':kb[0].embedding_model,
                            'reference':kb[0].reference,'create_time':kb[0].ctime,'update_time':kb[0].utime}
        return JsonResponse(response)
    response["state"]=1
    response["error_info"]=f"request method {request.method}!=POST"
    return JsonResponse(response)

def kb_create(request):
    if request.method == "GET":
        return redirect('../apidocs/')

    response={"state":0,"error_info":""}
    if request.method == "POST":
        username = request.POST.get('username')
        kbname = request.POST.get('kbname')
        api=request.POST.get('api') #
        embedding_model = request.POST.get('embedding_model')
        llm= request.POST.get('llm')
        if (api not in API.keys()):
            response["state"] = 1
            response["error_info"] = f"api does not exists"
            return JsonResponse(response)
        if (embedding_model not in API[api]["embedding_model"]):
            response["state"] = 1
            response["error_info"] = f"embedding_model does not exists"
            return JsonResponse(response)
        if (llm not in API[api]["llm"]):
            response["state"] = 1
            response["error_info"] = f"llm does not exists"
            return JsonResponse(response)
        embeddings_size=API[api]["embeddings_size"][embedding_model]

        if KnowledgeBase.objects.filter(name=kbname).exists():
            response["state"] = 1
            response["error_info"] = f"KnowledgeBase {kbname} exists"
            return JsonResponse(response)
        if kb_vdb_create(username,kbname,base_api,api,embedding_model,embeddings_size,base_db):
            kb_obj=KnowledgeBase(kbname,username,api,embedding_model,llm,embeddings_size,0)
            kb_obj.save()
        else:
            response["state"] = 1
            response["error_info"] = f"create vector base error"
        return JsonResponse(response)
    response["state"]=1
    response["error_info"]=f"request method {request.method}!=POST"
    return JsonResponse(response)

def kb_delete(request):
    if request.method == "GET":
        return redirect('../apidocs/')

    response={"state":0,"error_info":""}
    if request.method == "POST":
        username = request.POST.get('username')
        kbname = request.POST.get('kbname')
        kb_obj=KnowledgeBase.objects.filter(name=kbname)
        if not kb_obj.exists():
            response["state"] = 1
            response["error_info"] = f"KnowledgeBase {kbname} does not exists"
            return JsonResponse(response)
        if kb_obj[0].reference>0:
            response["state"] = 1
            response["error_info"] = f"KnowledgeBase {kbname} exists {kb_obj[0].reference} reference files"
            return JsonResponse(response)
        if kb_vdb_delete(username,kbname,base_db):
            kb_obj.delete()
        else:
            response["state"] = 1
            response["error_info"] = f"delete vector base error"
        return JsonResponse(response)
    response["state"]=1
    response["error_info"]=f"request method {request.method}!=POST"
    return JsonResponse(response)

def kb_get_valid_files(request):
    if request.method == "GET":
        return redirect('../apidocs/')

    response={"state":0,"error_info":""}
    if request.method == "POST":
        username = request.POST.get('username')
        kbname = request.POST.get('kbname')
        kb_obj=KnowledgeBase.objects.filter(name=kbname)
        if not kb_obj.exists():
            response["state"] = 1
            response["error_info"] = f"KnowledgeBase {kbname} does not exists"
            return JsonResponse(response)
        kb_vdb_files=kb_vdb_get_files(username,kbname,base_db)
        kb_files=[]
        for file_name in kb_vdb_files:
            name,type=file_to_name_type(file_name)
            kb_files.append(f"{name}.{type}")

        kb_username=kb_obj[0].user_name
        kb_api=kb_obj[0].api
        kb_embedding_model=kb_obj[0].embedding_model
        kb_embeddings_size=kb_obj[0].embeddings_size

        user_files=[]
        file_objs=File.objects.filter(user_name=kb_username,api=kb_api,embedding_model=kb_embedding_model,embeddings_size=kb_embeddings_size)
        for obj in file_objs:
            user_files.append(obj.name[len(username)+1:])
        valid_files=[file for file in user_files if file not in kb_files]

        response['files'] = valid_files
        return JsonResponse(response)
    response["state"] = 1
    response["error_info"] = f"request method {request.method}!=POST"
    return JsonResponse(response)

def kb_get_files(request):
    if request.method == "GET":
        return redirect('../apidocs/')

    response={"state":0,"error_info":""}
    if request.method == "POST":
        username = request.POST.get('username')
        kbname = request.POST.get('kbname')
        kb_obj=KnowledgeBase.objects.filter(name=kbname)
        if not kb_obj.exists():
            response["state"] = 1
            response["error_info"] = f"KnowledgeBase {kbname} does not exists"
            return JsonResponse(response)
        kb_vdb_files=kb_vdb_get_files(username,kbname,base_db)

        kb_files=[]
        for file_name in kb_vdb_files:
            name,type=file_to_name_type(file_name)
            kb_files.append(f"{name}.{type}")

        response['files'] = kb_files
        return JsonResponse(response)
    response["state"] = 1
    response["error_info"] = f"request method {request.method}!=POST"
    return JsonResponse(response)

def kb_add_files(request):
    if request.method == "GET":
        return redirect('../apidocs/')

    response={"state":0,"error_info":""}
    if request.method == "POST":
        username = request.POST.get('username')
        kbname = request.POST.get('kbname')
        file_names = request.POST.getlist('files')
        kb_obj=KnowledgeBase.objects.filter(name=kbname)
        if not kb_obj.exists():
            response["state"] = 1
            response["error_info"] = f"KnowledgeBase {kbname} does not exists"
            return JsonResponse(response)
        kb_files=kb_vdb_get_files(username,kbname,base_db)
        api=kb_obj[0].api
        kb_embedding_model=kb_obj[0].embedding_model

        file_states=[]
        # fliter valid files
        for file_name in file_names:
            name,type=file_to_name_type(file_name)
            filename=username+"_"+name+"."+type
            file=File.objects.filter(name=filename)
            if not file.exists():
                file_states.append({'name':file_name,'state':1,'error_info':"file does not exists"})
                continue
            if file[0].api!=api:
                file_states.append({'name':file_name,'state':1,'error_info':"api does not match"})
                continue
            if file[0].embedding_model!=kb_embedding_model:
                file_states.append({'name':file_name,'state':1,'error_info':"embedding_model does not match"})
                continue
            if file_name in kb_files:
                file_states.append({'name':file_name,'state':1,'error_info':"file already in knowledge base"})
                continue
            file_states.append({'name':file_name,'state':0,'error_info':""})

        # get valid files:
        fliter_file_names=[]
        for file in file_states:
            if file['state']:
                continue
            fliter_file_names.append(file['name'])
        # add files to vdb
        embeddings_size=kb_obj[0].embeddings_size
        if kb_vdb_add_files(username,kbname,fliter_file_names,embeddings_size,base_db):
            for file in file_states:
                if not file['state']:
                    name, type = file_to_name_type(file['name'])
                    filename = username + "_" + name + "." + type
                    file_obj=File.objects.get(name=filename)
                    kb_obj=KnowledgeBase.objects.get(name=kbname)
                    file_obj.count+=1
                    kb_obj.reference+= 1
                    file_obj.save()
                    kb_obj.save()
        else:
            for file in file_states:
                if not file['state']:
                    file['state']=1
                    file['error_info']="kb add file embeddings fail"
        response['file_states']=file_states
        return JsonResponse(response)
    response["state"]=1
    response["error_info"]=f"request method {request.method}!=POST"
    return JsonResponse(response)

def kb_drop_files(request):
    if request.method == "GET":
        return redirect('../apidocs/')

    response={"state":0,"error_info":""}
    if request.method == "POST":
        username = request.POST.get('username')
        kbname = request.POST.get('kbname')
        file_names = request.POST.getlist('files')
        kb_obj=KnowledgeBase.objects.filter(name=kbname)
        if not kb_obj.exists():
            response["state"] = 1
            response["error_info"] = f"KnowledgeBase {kbname} does not exists"
            return JsonResponse(response)
        kb_files=kb_vdb_get_files(username,kbname,base_db)

        file_states=[]
        # fliter valid files
        for file_name in file_names:
            name,type=file_to_name_type(file_name)
            filename=username+"_"+name+"."+type
            file=File.objects.filter(name=filename)
            if not file.exists():
                file_states.append({'name':file_name,'state':1,'error_info':"file does not exists"})
                continue
            if not file_name in kb_files:
                file_states.append({'name':file_name,'state':1,'error_info':"file does not in knowledge base"})
                continue
            file_states.append({'name':file_name,'state':0,'error_info':""})

        # get valid files:
        fliter_file_names=[]
        for file in file_states:
            if file['state']:
                continue
            fliter_file_names.append(file['name'])
        # drop files from vdb
        if kb_vdb_drop_files(username,kbname,fliter_file_names,base_db):
            for file in file_states:
                if not file['state']:
                    name, type = file_to_name_type(file['name'])
                    filename = username + "_" + name + "." + type
                    file_obj=File.objects.get(name=filename)
                    kb_obj=KnowledgeBase.objects.get(name=kbname)
                    file_obj.count-=1
                    kb_obj.reference-= 1
                    file_obj.save()
                    kb_obj.save()
        else:
            for file in file_states:
                if not file['state']:
                    file['state']=1
                    file['error_info']="kb drop file embeddings fail"
        response['file_states']=file_states
        return JsonResponse(response)
    response["state"]=1
    response["error_info"]=f"request method {request.method}!=POST"
    return JsonResponse(response)

def api_check(request):
    if request.method == "GET":
        return redirect('../apidocs/')

    response={"state":0,"error_info":""}
    if request.method == "POST":
        return JsonResponse(response)
    response["state"]=1
    response["error_info"]=f"request method {request.method}!=POST"
    return JsonResponse(response)


import pickle
# new_chat,delete_chat,save_chat,load_chat,send_msg
def chat(request):
    if request.method == "GET":
        return redirect('../apidocs/')
    response={"state":0,"error_info":""}
    if request.method == "POST":
        method= request.POST.get('method')
        if method == "get":
            username = request.POST.get('username')
            chatobjs=ChatModel.objects.filter(user_name=username)
            chat_list=[obj.name.split('.')[-1]  for obj in chatobjs]
            response["chat_list"] = chat_list
            return JsonResponse(response)
        elif method=="create":
            username = request.POST.get('username')
            chatname = request.POST.get('chatname')
            kbname = request.POST.get('kbname')
            max_context = request.POST.get('max_context')

            max_context=min(int(max_context),5)
            system_template = request.POST.get('system_template')
            question_template = request.POST.get('question_template')
            chat_name=username+"."+chatname

            if ChatModel.objects.filter(name=chat_name).exists():
                response["state"] = 1
                response["error_info"] = f"Chat {chatname} exists"
                return JsonResponse(response)
            if not KnowledgeBase.objects.filter(name=kbname).exists():
                response["state"] = 1
                response["error_info"] = f"KnowledgeBase {kbname} not exists"
                return JsonResponse(response)
            chat_obj=ChatModel(chat_name,username,kbname,pickle.dumps([]),max_context,system_template,question_template)
            chat_obj.save()
            return JsonResponse(response)
        elif method=="delete":
            username = request.POST.get('username')
            chatname = request.POST.get('chatname')
            chat_name=username+"."+chatname
            chatobj=ChatModel.objects.filter(name=chat_name)
            if not chatobj.exists():
                response["state"] = 1
                response["error_info"] = f"Chat {chatname} not exists"
                return JsonResponse(response)
            if chatobj[0].user_name!=username:
                response["state"] = 1
                response["error_info"] = f"no permission to delete"
                return JsonResponse(response)
            chatobj[0].delete()
            return JsonResponse(response)
        elif method=="chat":
            username = request.POST.get('username')
            chatname = request.POST.get('chatname')
            chat_name = username+"."+chatname
            message = request.POST.get('message')
            msgtype = request.POST.get('msgtype')
            # if msgtype not in ['text','img','video','audio']:
            if msgtype not in ['text']:
                response["state"] = 1
                response["error_info"] = f"unsupport msg type {msgtype}"
            chatobj = ChatModel.objects.filter(name=chat_name)
            if not chatobj.exists():
                response["state"] = 1
                response["error_info"] = f"Chat {chatname} not exists"
                return JsonResponse(response)
            if chatobj[0].user_name != username:
                response["state"] = 1
                response["error_info"] = f"no permission to access"
                return JsonResponse(response)
            kbobj=KnowledgeBase.objects.filter(name=chatobj[0].kb_name)[0]


            embeddings=text2embeddings(message,base_api,kbobj.api,kbobj.embedding_model)

            krdroid_chat=Chat(chatobj[0].max_context,chatobj[0].system_template,chatobj[0].question_template)
            history=ChatModel.bin2obj(chatobj[0].history)
            krdroid_chat.load(history)
            msg=Message('user',msgtype,message)
            krdroid_chat.update(msg)
            ChatModel.update(chatobj[0],msg)

            kns=search_knowledges(username,kbobj.name,embeddings,base_db)

            context=krdroid_chat.msg2_api_dict(krdroid_chat.get_context_message())[:-1]
            question=get_query_format(message,kns,krdroid_chat.question_template)

            refs=[]
            for k in kns:
                if k['file'] not in refs:
                    refs.append(k['file'])
            # with open('tmp.txt',mode='at+') as f:
            #     f.write(str(kns))
            context.append({'role':'user','content':question})
            reply=get_msg(context,base_api,kbobj.api,kbobj.llm)
            ChatModel.update(chatobj[0],Message('assistant','text',reply))
            response["reply"] = reply
            response["refs"] = refs
            response["kns"] = kns

            return JsonResponse(response)
        elif method=="load":
            username = request.POST.get('username')
            chatname = request.POST.get('chatname')
            chat_name=username+"."+chatname
            chatobj=ChatModel.objects.filter(name=chat_name)
            if not chatobj.exists():
                response["state"] = 1
                response["error_info"] = f"Chat {chatname} not exists"
                return JsonResponse(response)
            if chatobj[0].user_name != username:
                response["state"] = 1
                response["error_info"] = f"no permission to access"
                return JsonResponse(response)
            history=[msg.to_dict() for msg in ChatModel.bin2obj(chatobj[0].history)]
            response["history"] = history
            return JsonResponse(response)
        else:
            response["state"] = 1
            response["error_info"] = f"method not supported"
            return JsonResponse(response)

    response["state"] = 1
    response["error_info"] = f"request method {request.method}!=POST"
    return JsonResponse(response)
