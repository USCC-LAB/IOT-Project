/*var usr = prompt("Please enter username:")
while(usr != "0") {
    usr = prompt("Error, please enter valid username:")
}

var pwd = prompt("Please enter password:")
while(pwd != "0") {
    pwd = prompt("Error, please enter valid password:")
}*/

var client = mqtt.connect({
    host: '140.116.82.42',
    port: 9001,
    username: 'weblogin',
    password: 'wtf123'
});

var checkbox = document.getElementById("myonoffswitch");
var sche_msg;
function switchon() {

    if (checkbox.checked) {
        client.publish('uscclab/gateway_001/control', 'ON', options);
    } else {
        client.publish('uscclab/gateway_001/control', 'OFF', options);
    }
}
//client.publish('uscclab/gateway_001/control', 'ACK');
//client.publish('mqtt/data', 'module_001 / 192.168.137.132 / Temperature:29.4 / Humidity:41.9 / Light:73.31 / UV:102.64 / Soil:909.09 / Air Pressure:99.959 / Time:2018-08-10 15:10:14.047936');

// sensor data format: "module_001 / 192.168.137.132 / Temperature:29.4 / Humidity:41.9 / Light:73.31 / UV:102.64 / Soil:909.09 / Air Pressure:99.959 / Time:2018-08-10 15:10:14.047936"

var options = {retain: true};

function makeConnect() {
    client.subscribe('uscclab/gateway_001/module_001/data');
    client.subscribe('uscclab/gateway_001/control');
    client.subscribe('uscclab/gateway_001/schedule');
    
    client.on('message', function (topic, message) {
        var msg = message.toString();
        var topic_name = topic.toString();

        if (topic_name == "uscclab/gateway_001/module_001/data") {
            msg = slice_data("Temperature", msg);
            msg = slice_data("Humidity", msg);
            msg = slice_data("Light", msg);
            msg = slice_data("UV", msg);
            msg = slice_data("Soil", msg);
            msg = slice_data("Pressure", msg);
        } else if (topic_name == "uscclab/gateway_001/control") {
            if (msg == "OFF") {
                checkbox.checked = false;
            } else if (msg == "ON") {
                checkbox.checked = true;
            }
        } else if (topic_name == "uscclab/gateway_001/schedule") {
            //if (msg.slice(0, 7) == "server_") {
                sche_msg = msg.slice(0, msg.length);
                console.log("sche_msg1:" + sche_msg + "hi");
                if(sche_msg[sche_msg.length-1] == "\n")
                    sche_msg = sche_msg.slice(0, sche_msg.length-1);
                console.log("sche_msg2:" + sche_msg + "hi");
                create_table(sche_msg);
            //}
        }
        console.log("Topic:" + topic.toString() + " Message:" + message);
    });
    
}

makeConnect();
create_table("");
sche_msg = "";
function slice_data(dt_type, msg){
    var index = msg.indexOf(dt_type);
    msg = msg.substring(index);
    slash = msg.indexOf('/');
    var insert_data = "";
    var id = "";
    switch(dt_type){
        case "Temperature": insert_data = msg.substring(12, slash-1); insert_data += "°C"; id = "temp"; break;
        case "Humidity": insert_data = msg.substring(9, slash-1); insert_data += "%"; id = "humid"; break;
        case "Light": insert_data = msg.substring(6, slash-1); insert_data += "mV"; id = "light"; break;
        case "UV": insert_data = msg.substring(3, slash-1); insert_data += "mV"; id = "uv"; break;
        case "Soil": insert_data = msg.substring(5, slash-1); insert_data += ""; id = "soil"; break;
        case "Pressure": insert_data = msg.substring(9, slash-1); insert_data += "hpa"; id = "press"; break;
    }
    document.getElementById(id).innerHTML = insert_data;
    return msg;
}

function create_table(sche_msg) {

    if (sche_msg != "add") {
        var table = '<table class="table table-striped" style="font-size:x-large; layout:fixed"><thead><tr><th width=40%>排程依據</th><th width=50%>內容</th><th width=10%></th></tr></thead><tbody>';
        x = sche_msg.split(" ");
        var i = 0;
        var col1, col2;
        console.log(x.length);
        while (i < x.length-1) {
            type = x[i][0];
            if (type == '1') {
                col1 = "時間";
                col2 = "每天" + x[i].substring(2);
            } else if (type == '2') {
                col1 = "氣溫";
                var compare = (x[i][2] == '<') ? "小於" : "大於";
                col2 = "當" + compare + x[i].substring(3) + "°C時";
            } else if (type == '3') {
                col1 = "土壤溼度";
                var compare = (x[i][2] == '<') ? "小於" : "大於";
                col2 = "當" + compare + x[i].substring(3) + "%時";
            }
            table += '<tr><td width=40%>' + col1 + '</td>';
            table += '<td width=50%>' + col2 + '</td>';
            table += '<td width="10%"><button class="btn icon-btn btn-danger" type="button"';
            table += 'id="btn' + i.toString() + '" onclick="delete_one(' + i.toString() + ')"';
            table += 'style="font-size:18px;"><span class="glyphicon btn-glyphicon glyphicon-trash img-circle text-danger"></span>刪除</button></td></tr>';
            i++;
        }
        table += '<tr id=add-row></tr>';
        table += '</body></table>';
        var node = document.getElementById('tbl-id');
        node.innerHTML = table;
    } else if (sche_msg == "add") {
        var col = '<td width=40%><select title="選擇排程依據" class="form-control" id="wt_type" onchange="selected()" style="width:30%; font-size:18px; height:40px"><option value="">請選擇</option><option value="0">時間</option><option value="1">氣溫</option><option value="2">土壤溼度</option></select></td><td width=50% id="content"></td><td width=10% id="sche_save"></td>';

        document.getElementById('add-row').innerHTML = col;
    }
}

var select = document.getElementById("wt_type");
function selected() {
    var val = document.getElementById("wt_type").value;
    var col = "";
    send_msg = "";
    if (val == "0") {
        col += '<input type="time" id="set-time"/>';
        send_msg += "1:";
    } else if (val == "1") {
        col += '<div class="form-inline"><select class="form-control" id="compare" style="width:13%; font-size:24px;line-height:40px; height:40px; padding-top:0px"><option value="0"><</option><option value="1">></option></select><input type="text" class="form-control" id="set-val" style="width:10%; height:40px; font-size:22px">°C</div>';
        send_msg += "2:";
    } else if (val == "2") {
        col += '<div class="form-inline"><select class="form-control" id="compare" style="width:13%; font-size:24px;line-height:40px; height:40px; padding-top:0px"><option value="0"><</option><option value="1">></option></select><input type="text" class="form-control" id="set-val" style="width:10%; height:40px; font-size:22px">%</div>';
        send_msg += "3:";
    }
    var save_btn = '<button type="button" class="btn btn-success icon-btn" onclick="save_change()" style="font-size:18px;"><span class="glyphicon glyphicon-ok img-circle text-success btn-glyphicon"></span>儲存</button>';
    
    document.getElementById('content').innerHTML = col;
    document.getElementById('sche_save').innerHTML = save_btn;
}

function delete_one(count) {
    var new_msg = "";
    var first = true;
    for (i = 0; i < x.length-1; ++i) {
        if (i != parseInt(count)){
            new_msg += x[i] + " ";
        }
    }
    new_msg = new_msg.substring(0, new_msg.length);
    console.log("after deletion:" + new_msg + "end");
    client.publish('uscclab/gateway_001/schedule', new_msg, options);
}

function save_change() {
    if (send_msg == "2:" || send_msg == "3:") {
        send_msg += (document.getElementById('compare').value == 0) ? "<" : ">";
        send_msg += document.getElementById('set-val').value.toString();
    } else if (send_msg == "1:") {
        send_msg += document.getElementById('set-time').value.toString();
    }
    send_msg += " ";
    if(sche_msg == " ")
        sche_msg = "";
    var temp_sche_msg = sche_msg;
    sche_msg = sche_msg.substring(0, sche_msg.length);
    sche_msg += send_msg;
    if(send_msg.length >3){
        console.log("publish message:" + sche_msg);
        client.publish('uscclab/gateway_001/schedule', sche_msg, options);
    }else{
        sche_msg = temp_sche_msg;
        send_msg = send_msg.substring(0, 2);
    }
}

/*function sethumid() {
	var x = document.getElementById("myRange").value;
	document.getElementById("humidset").innerHTML = x;
}

document.getElementById("time").disabled = true;
document.getElementById("myRange").disabled = true;

var selectmenu = document.getElementById("choose");
selectmenu.onchange = function () { //run some code when "onchange" event fires
	var chosenoption = this.options[this.selectedIndex] //this refers to "selectmenu"
	if(chosenoption.value == "0"){
		document.getElementById("time").disabled = false;
		document.getElementById("myRange").disabled = true;
	}else if(chosenoption.value == "1"){
		document.getElementById("time").disabled = true;
		document.getElementById("myRange").disabled = false;
	}
}

function saveChange(){
	client.publish('mqtt/schedule', 'time');
}*/



