let url = "http://203.64.95.118:30001/api_v1";
let public_key = "";
auth();

function register(){
    let name = document.getElementById("name").value;
    let cpu = document.getElementById("cpu").value;
    let memory = document.getElementById("memory").value;
    let node_name = document.getElementById("node_name").value;
    let disk_size = document.getElementById("disk_size").value;

    send_data = {
        name:name,                           //算是uid，依賴這一個key來開pod(實際上uid應該要是一連串的亂碼，但來不及做完)
        cpu:parseInt(cpu),
        memory:parseFloat(memory),          //單位是M
        node_name:node_name,
        disk_size:parseInt(disk_size),      //單位是G
    };

    $.ajax({
        type: "POST",                                   //傳輸協定 正常都是POST或GET
        url: `${url}/machine/CREATE`,                   //設定api server url
        data: JSON.stringify(send_data),                //要傳給api server的資料，若沒有可以不用這行
        contentType: "application/json; charset=utf-8", //傳輸資料的型態，通常會建議傳json + utf8
        dataType: "json",                               //api server回傳資料的型態，不打這行的話會自動判斷，留空的話我不保證也會自動判斷，建議自己打或直接刪掉這行
        success: function (data) {                      //傳輸成功時要做的事，也有傳輸失敗、傳輸中間等等可以設定
            console.log("register: success");
            console.log(data);
            if (data["status"] == "success"){
                alert("申請成功");
            }else{
                alert("申請失敗");
            }
        }
    });
}


function apply(type_name){
    let machine_name = document.getElementById("machine_name").value;

    let send_data = {
        name:machine_name,
        token:""
    };

    $.ajax({
        type: "POST",                                   //傳輸協定 正常都是POST或GET
        url: `${url}/pod/${type_name}`,                 //設定api server url
        data: JSON.stringify(send_data),                //要傳給api server的資料，若沒有可以不用這行
        contentType: "application/json; charset=utf-8", //傳輸資料的型態，通常會建議傳json + utf8
        dataType: "json",                               //api server回傳資料的型態，不打這行的話會自動判斷，留空的話我不保證也會自動判斷，建議自己打或直接刪掉這行
        success: function (data) {                      //傳輸成功時要做的事，也有傳輸失敗、傳輸中間等等可以設定
            console.log("apply: success");
            console.log(data);
            if (data["status"] == "success"){
                if (type_name == "CREATE"){
                    alert("開啟成功");
                }else if (type_name == "DELETE"){
                    alert("關閉成功");
                }else{
                    alert("重啟成功");
                }
            }else{
                alert("開啟失敗");
            }
        }
    });
}


function get_machine_all_list(){
    let send_data = {
        name:"all"
    };

    $.ajax({
        type: "POST",                                   //傳輸協定 正常都是POST或GET
        url: `${url}/machine/GET`,                      //設定api server url
        data: JSON.stringify(send_data),                //要傳給api server的資料，若沒有可以不用這行
        contentType: "application/json; charset=utf-8", //傳輸資料的型態，通常會建議傳json + utf8
        dataType: "json",                               //api server回傳資料的型態，不打這行的話會自動判斷，留空的話我不保證也會自動判斷，建議自己打或直接刪掉這行
        success: function (data) {                      //傳輸成功時要做的事，也有傳輸失敗、傳輸中間等等可以設定
            console.log("get_machine_list: success");
            console.log(data);
            let select = document.getElementById("machine_name");
            for (let i in data["data"]["name_list"]){
                let opt = document.createElement('option');
                opt.value = data["data"]["name_list"][i];
                opt.innerHTML = data["data"]["name_list"][i];
                select.appendChild(opt);
            }
        }
    });
}


function get_machine_status(){
    let machine_name = document.getElementById("machine_name").value;
    let send_data = {
        name:machine_name
    };

    $.ajax({
        type: "POST",                                           //傳輸協定 正常都是POST或GET
        url: `${url}/machine/GET`,                              //設定api server url
        data: JSON.stringify(send_data),                        //要傳給api server的資料，若沒有可以不用這行
        contentType: "application/json; charset=utf-8",         //傳輸資料的型態，通常會建議傳json + utf8
        dataType: "json",                                       //api server回傳資料的型態，不打這行的話會自動判斷，留空的話我不保證也會自動判斷，建議自己打或直接刪掉這行
        success: function (data) {                              //傳輸成功時要做的事，也有傳輸失敗、傳輸中間等等可以設定
            console.log("get_all_machine_status: success");
            console.log(data);
            if (data["status"] == "success"){
                data = data["data"];
                alert(`status:${data['ready']}\nip:${data['ip']}\nports:${data['ports']}\ncpu:${data['cpu']}\nmemory:${data['memory']}\ngpu:${data['gpu']}\n`);
            }else{
                alert("error");
            }
        }
    });
}


function get_machine_link_string(){
    let machine_name = document.getElementById("machine_name").value;
    let send_data = {
        name:machine_name
    };

    $.ajax({
        type: "POST",                                           //傳輸協定 正常都是POST或GET
        url: `${url}/machine/GET`,                              //設定api server url
        data: JSON.stringify(send_data),                        //要傳給api server的資料，若沒有可以不用這行
        contentType: "application/json; charset=utf-8",         //傳輸資料的型態，通常會建議傳json + utf8
        dataType: "json",                                       //api server回傳資料的型態，不打這行的話會自動判斷，留空的話我不保證也會自動判斷，建議自己打或直接刪掉這行
        success: function (data) {                              //傳輸成功時要做的事，也有傳輸失敗、傳輸中間等等可以設定
            console.log("get_all_machine_status: success");
            console.log(data);
            if (data["status"] == "success"){
                data = data["data"];
                alert(`ssh -J root@203.64.95.118:30003 root@${data['ip']}`);
            }else{
                alert("error");
            }
        }
    });
}


function parse_time(time_string){
    result = replace_all(time_string, "T", "/");
    result = replace_all(result, ":", "/");
    result = replace_all(result, "-", "/");

    return result;
}


function login(){
    let uid = document.getElementById("uid").value;
    let password = document.getElementById("password").value;

    $.ajax({
        type: "POST",                                           //傳輸協定 正常都是POST或GET
        url: `${url}/account/LOGIN`,                            //設定api server url
        data: JSON.stringify({"uid":uid, "passwd":password}),     //要傳給api server的資料，若沒有可以不用這行
        contentType: "application/json; charset=utf-8",         //傳輸資料的型態，通常會建議傳json + utf8
        dataType: "json",                                       //api server回傳資料的型態，不打這行的話會自動判斷，留空的話我不保證也會自動判斷，建議自己打或直接刪掉這行
        success: function (data) {                              //傳輸成功時要做的事，也有傳輸失敗、傳輸中間等等可以設定
            console.log("login: success");
            console.log(data);
            if (data["result"] != "success"){
                alert("帳號或密碼輸入錯誤");
            }else{
                sessionStorage["uid"] = data["uid"];
                sessionStorage["token"] = data["token"];
                if (data["permission"] == "user"){
                    window.location.href = "user.html";
                }else if (data["permission"] == "admin"){
                    window.location.href = "management.html";
                }
                    
            }
        }
    });
}


//count, 用來計算source_str裡有多少個target_str
function string_count(source_str, target_str) {
    return source_str.split(target_str).length - 1
}

//replace_all, 取代javascript裡對應的replaceAll, 主因是不知為啥replaceAll很常自己消失, 所以自己刻一個replaceAll功能的function
function replace_all(source_str, target_str, replace_str) {
    let count = string_count(source_str, target_str);
    for (let i = 0; i < count; i++) {
        source_str = source_str.replace(target_str, replace_str);
    }
    return source_str
}


function auth(){
    let page = window.location.pathname.split("/").pop();
    if (page != "login.html" && page != "signin.html"){
        if (sessionStorage.key("uid") != null){
            console.log("驗證成功");
        }else{
            window.location.href = "login.html";
        }
    }
}


function show_time(o){
    let now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    let show_time = now.toISOString().slice(0, -1).split(".")[0];
    show_time = replace_all(show_time, "T", "  ");
    o.innerText = show_time;
}


async function page_reload(m, s){
    await sleep((60 * m + s) * 1000);
    window.location.reload();
}


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


window.addEventListener('load', () => {
    let now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    let start = document.getElementById('start_time');
    let end = document.getElementById('end_time');
    if (start != null){
        start.min = now.toISOString().slice(0, -1).split(".")[0];
        start.value = now.toISOString().slice(0, -1).split(".")[0];
    }
    if (end != null){
        end.min = now.toISOString().slice(0, -1).split(".")[0];
        end.value = now.toISOString().slice(0, -1).split(".")[0];
    }
});