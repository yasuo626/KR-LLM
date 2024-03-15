




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
var api_user = api_url+'/wmc/apiuser';

var api_wmc_apiurl= 'http://127.0.0.1:8000/wmc/apiurl';

var absolute_container=document.getElementById('absolute_container')

function show_etc_menu(){
    menu=document.getElementById('etc_menu');
    if(menu.style.display=='block'){
        menu.style.display='none';
    }else{
       menu.style.display='block';
    }

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
            document.getElementById('login_form').style.display='none';
            document.getElementById('absolute_container').style.display='none';
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


function login_required(){
        require_login=document.getElementById('require_login').innerText
        is_login=document.getElementById('is_login').innerText
        username=document.getElementById('get_username').innerText

        if(require_login==1){
            if(is_login==1){
                // document.getElementById('main_container').innerText+=`${username}`;
            }else{
                document.getElementById('fullscreen_shadow').style.display='block';
                document.getElementById('absolute_container').style.display='block';
            }
        }
}
login_required()


function set_url(){
    document.getElementById('login_form').style.display='none';
    document.getElementById('set_url_form').style.display='block';
    absolute_container.style.display='block';
}


function response_set_url_submit(responsedata) {
    // 在这里对响应数据进行处理
    if(responsedata.state=='0'){
        document.getElementById('set_url_response_msg').style.display='inline-block';
        document.getElementById('set_url_response_msg').innerText="set success";
        document.getElementById('set_url_loader').style.display = 'inline-block';
        document.getElementById('set_url_response_msg').innerText="check url...";

        var xhr = new XMLHttpRequest();
        xhr.open('POST', document.getElementById('set_url_form_url').value+"/krdroid/api_check", true);
        xhr.onload = function() {
            if (xhr.status === 200) {
                var jsonResponse = JSON.parse(xhr.responseText);
                document.getElementById('set_url_loader').style.display = 'none';
                document.getElementById('set_url_response_msg').innerText="check success";
                setTimeout(() => {
                    document.getElementById('set_url_form').style.display='none';
                    document.getElementById('absolute_container').style.display='none';
                    location.reload();
                }, 1000);

            } else {
                document.getElementById('set_url_loader').style.display = 'none';
                document.getElementById('set_url_response_msg').innerText="check failed";
            }
        };
        xhr.send(new FormData());


    }else{
        document.getElementById('set_url_response_msg').style.display='inline-block';
        document.getElementById('set_url_response_msg').innerText=`${responsedata.error_info}`;
        document.getElementById('set_url_loader').style.display = 'none';
    }
}

function set_url_submit(){
    var url=document.getElementById('set_url_form_url').value;
    var formdata=new FormData();
    formdata.append('method','set');
    formdata.append('url',url);



    api_request(formdata,api_wmc_apiurl,response_set_url_submit);
}