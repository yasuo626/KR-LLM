




function api_request(formData, apiUrl, callback) {

    var xhr = new XMLHttpRequest();
    xhr.open('POST', apiUrl, true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            var jsonResponse = JSON.parse(xhr.responseText);
            callback(jsonResponse)
            // 在这里处理解析后的 JSON 数据
            console.log(jsonResponse);
        } else {
            // 请求失败
            alert('Request failed with status:', xhr.status);
            console.error('Request failed with status:', xhr.status);
        }
    };
    xhr.send(formData);
}

var api_url='http://127.0.0.1:8000'
// 示例数据和 API 地址
var api_user_login = api_url+'/wmc/apiuser';
var api_user_logout = api_url+'/wmc/apiuser';
var api_user_logoff = api_url+'/wmc/apiuser';
var api_user_register = api_url+'/wmc/apiuser';
var api_user = api_url+'/wmc/apiuser';
var api_krdroid_file_upload = api_url+'/krdroid/file_upload';
var api_krdroid_file_delete = api_url+'/krdroid/file_delete';
var api_krdroid_kb_create = api_url+'/krdroid/kb_create';
var api_krdroid_kb_delete = api_url+'/krdroid/kb_delete';
var api_krdroid_kb_add_files = api_url+'/krdroid/kb_add_files';
var api_krdroid_kb_get_files = api_url+'/krdroid/kb_get_files';
var api_krdroid_kb_drop_files = api_url+'/krdroid/kb_drop_files';
var api_krdroid_chat= api_url+'/krdroid/chat';


function show_etc_menu(){
    menu=document.getElementById('etc_menu');
    if(menu.style.display=='block'){
        menu.style.display='none';
    }else{
       menu.style.display='block';
    }

}
function showRegisterForm() {
    document.getElementById('login_form').style.display = 'none';
    document.getElementById('register_form').style.display = 'block';
}
function response_logout(responseData) {
    document.location.reload();
}
function logout(){
    var formdata = new FormData();
    formdata.append('method','logout');
    api_request(formdata,api_user,response_logout);
}

function response_login(responseData) {
    if(responseData.state=='0'){
        document.getElementById('login_response_msg').style.display='inline-block';
        document.getElementById('login_response_msg').innerText="login success";
        document.getElementById('login_loader').style.display = 'none';
        setTimeout(() => {
            document.getElementById('fullscreen_shadow').style.display='none';
            document.getElementById('login_container').style.display='none';
        }, 500);
    }else{
        document.getElementById('login_response_msg').style.display='inline-block';
        document.getElementById('login_response_msg').innerText=`${responseData.error_info}`;
        document.getElementById('login_loader').style.display = 'none';
    }
}
function login() {
    document.getElementById('login_loader').style.display = 'inline-block';
    document.getElementById('login_response_msg').style.display = 'none';

    username=document.getElementById('login_username').value;
    password=document.getElementById('login_password').value;

    var formdata = new FormData();
    formdata.append('method','login');
    formdata.append('username',username);
    formdata.append('password',password);
    api_request(formdata,api_user,response_login);
}
function response_register(responseData) {
    // 在这里对响应数据进行处理
    if(responseData.state=='0'){
        document.getElementById('register_response_msg').style.display='inline-block';
        document.getElementById('register_response_msg').innerText="register success";
        document.getElementById('register_loader').style.display = 'none';
        setTimeout(() => {
            document.getElementById('register_form').style.display = 'none';
            document.getElementById('login_form').style.display = 'block';
        }, 500);
    }else{
        document.getElementById('register_response_msg').style.display='inline-block';
        document.getElementById('register_response_msg').innerText=`${responseData.error_info}`;
        document.getElementById('register_loader').style.display = 'none';
    }
}
function register() {

    document.getElementById('register_loader').style.display = 'inline-block';
    document.getElementById('register_response_msg').style.display = 'none';

    username=document.getElementById('register_username').value;
    email=document.getElementById('register_email').value;
    password=document.getElementById('register_password').value;

    var formdata = new FormData();
    formdata.append('method','register');
    formdata.append('username',username);
    formdata.append('email',email);
    formdata.append('password',password);

    api_request(formdata,api_user,response_register);
}

function login_required(){
        require_login=document.getElementById('require_login').innerText
        is_login=document.getElementById('is_login').innerText
        username=document.getElementById('get_username').innerText

        if(require_login==1){
            if(is_login==1){
                document.getElementById('main_container').innerText+=`${username}`;
            }else{
                document.getElementById('fullscreen_shadow').style.display='block';
                document.getElementById('login_container').style.display='block';
            }
        }
}
login_required()