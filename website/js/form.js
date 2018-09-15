var client  = mqtt.connect({
			host: '140.116.82.42',
			port: 9001,
			username: 'weblogin',
			password: 'wtf123'
		});
//client.publish('mqtt/data', 'Temperature:28.30 / Humidity:73.08 / Light:50000 / UV:13.88 / Soil:514.12 / Pressure:1001.64');

function makeConnect(){
	
	//client.subscribe('mqtt/data');
    client.subscribe('mqtt/web');

	client.on('message', function (topic, message) {
		var msg = message.toString();
		var topic_name = topic.toString();
		
		if(topic_name == "mqtt/web" && msg.slice(0, 7) != 'request' && msg != "too early"){
            //set_data(msg.slice(0,1), msg);
                draw_table(msg);
        }
	    //var d = new Date(2018,7,10);
        //console.log(Math.floor(d.getTime()/1000).toString(16) + "0000000000000000");
		
        console.log("Topic:" + topic_name + " Message:" + msg);
	});
}

makeConnect();

function draw_table(msg){
    var table = '<table class="table table-striped" style="background: rgba(255,255,255,0.6); font-size:x-large"><thead><tr><th>氣溫</th><th>空氣溼度</th><th>光照</th><th>紫外線</th><th>土壤溼度</th><th>氣壓</th><th>時間</th></thead><tbody>';
    if(msg == "no data"){
        table += '<tr><td colspan="7" align="center">此日期區間沒有資料可供顯示</td></tr>';
    }else{

    msg = msg.slice(1, msg.length-1);
    x = msg.split("], ");
    var i = 0;
    
    for(i = 0; i < x.length; ++i){
        col_in = x[i].indexOf(",");
        table += '<tr><td>' + x[i].slice(1, col_in) + "</td>";
        x[i] = x[i].slice(col_in+2);
        col_in = x[i].indexOf(",");
        table += '<td>' + x[i].slice(0, col_in) + "</td>";
        x[i] = x[i].slice(col_in+2);
        col_in = x[i].indexOf(",");
        table += '<td>' + x[i].slice(0, col_in) + "</td>";
        x[i] = x[i].slice(col_in+2);
        col_in = x[i].indexOf(",");
        table += '<td>' + x[i].slice(0, col_in) + "</td>";
        x[i] = x[i].slice(col_in+2);
        col_in = x[i].indexOf(",");
        table += '<td>' + x[i].slice(0, col_in) + "</td>";
        x[i] = x[i].slice(col_in+2);
        col_in = x[i].indexOf(",");
        table += '<td>' + x[i].slice(0, col_in) + "</td>";
        x[i] = x[i].slice(col_in+2);
        col_in = x[i].indexOf(",");
        table += '<td>' + compute_date(x[i].slice(0, x[i].indexOf("."))) + "</td></tr>";
    }
    table += "</tbody>";
    }
    document.getElementById("table").innerHTML = table;
}

function compute_date(str){
    if(str.length == 3){
        return "0" + str[0] + "/" + str.slice(1, 3);
    }else if(str.length == 4){
        return str.slice(0, 2) + "/" + str.slice(2, 4);
    }else if(str.length == 2 || str.length == 1){
        if(str.length == 2)
            return str.slice(0, 2) + "時";
        else if(str.length == 1)
            return str.slice(0, 1) + "時";
    }else
        console.log("wrong date");
}

range = "month";
function set_range(i){
    range = (i == 0) ? "month" : (i == 1) ? " week" : (i == 2) ? "  day" : "  day";
    document.getElementById("month_btn").style.backgroundColor = "grey";
    document.getElementById("week_btn").style.backgroundColor = "grey";
    document.getElementById("day_btn").style.backgroundColor = "grey";
    if(i == 0)
        document.getElementById("month_btn").style.backgroundColor = "black";
    else if(i == 1)
        document.getElementById("week_btn").style.backgroundColor = "black";
    else if(i == 2)
        document.getElementById("day_btn").style.backgroundColor = "black";
    set_date();
    
}

// send_msg format: request month xxxxxxxxxxxxxxxxxxxxxxxx xxxxxxxxxxxxxxxxxxxxxxxx

function set_date(){
    var date = document.getElementById("datepicker").value;
    console.log(date); //format: 08/10/2018
    
    var year = parseInt(date.substring(6, 10));
    var month = parseInt(date.substring(0, 2));
    var day = parseInt(date.substring(3, 5));

    var d = new Date(year, month-1, day);
    var object_id1 = Math.floor(d.getTime()/1000).toString(16) + "0000000000000000";
    var d1 = d;
    if(range == "month"){
        d = new Date(year, month-1, 1);
        object_id1 = Math.floor(d.getTime()/1000).toString(16) + "0000000000000000";
        d1 = new Date(year, month, -1);
        document.getElementById("range").innerHTML = month.toString() + "月份";
    }else if(range == " week"){
        d1 = new Date(year, month-1, day+7);
        document.getElementById("range").innerHTML = month.toString() + "月" + day.toString() + "日開始的一週";
    }else if (range == "  day"){
        d1 = new Date(year, month-1, day, 23, 59);
        document.getElementById("range").innerHTML = month.toString() + "月" + day.toString() + "日";
    }
    console.log("start:"+(d.getMonth()+1).toString()+"/"+d.getDate().toString());
    console.log("end:"+(d1.getMonth()+1).toString()+"/"+d1.getDate().toString());

    var object_id2 = Math.floor(d1.getTime()/1000).toString(16) + "0000000000000000";
    var send_msg = "request " + range + " " + object_id1 + " " + object_id2;
    if(year >= "2018" && month >= 8)
        client.publish("mqtt/web", send_msg);
    else
        if(year >= "2018" && month >= 7){
            if(day > 24)
                client.publish("mqtt/web", send_msg);
            else
                client.publish("mqtt/web", "too early");
        }else
            client.publish("mqtt/web", "too early");
    
}



/*function set_data(variable, msg){
	index_temp = msg.indexOf("Temperature");
	index_humid = msg.indexOf("Humidity");
	index_light = msg.indexOf("Light");
	index_uv = msg.indexOf("UV");
	index_soil = msg.indexOf("Soil");
	index_press = msg.indexOf("Pressure");
	index_time = msg.indexOf("Time");
    console.log(variable);
    console.log(''.concat("temp", variable));
    document.getElementById(''.concat("time", variable)).innerHTML = msg.slice(index_time + 8, index_time + 22);
    document.getElementById(''.concat("temp", variable)).innerHTML = msg.slice(index_temp + 15, index_temp + 19);
    document.getElementById(''.concat("humid", variable)).innerHTML = msg.slice(index_humid + 12, index_humid + 16);
    document.getElementById(''.concat("light", variable)).innerHTML = msg.slice(index_light + 9, index_light + 16);
    document.getElementById(''.concat("uv", variable)).innerHTML = msg.slice(index_uv + 6, index_uv + 12);
    document.getElementById(''.concat("soil", variable)).innerHTML = msg.slice(index_soil + 8, index_soil + 14);
    document.getElementById(''.concat("press", variable)).innerHTML = msg.slice(index_press + 12, index_press + 19);
}

function createbody(){
    var table = '';
    var rows = 5;
    var cols = 7;
    for(var r = 0; r < rows; r++){
        table += '<tr>';
        for(var c = 0; c < cols; c++){
            switch(c){
                case 0:
                    table += '<td id="time'+ r + '"></td>';
                    break;
                case 1:
                    table += '<td id="temp'+ r + '"></td>';
                    break;
                case 2:
                    table += '<td id="humid'+ r + '"></td>';
                    break;
                case 3:
                    table += '<td id="light'+ r + '"></td>';
                    break;
                case 4:
                    table += '<td id="uv'+ r + '"></td>';
                    break;
                case 5:
                    table += '<td id="soil'+ r + '"></td>';
                    break;
                case 6:
                    table += '<td id="press'+ r + '"></td>';
                    break;
            }
        }
        table += '</tr>';
    }
    document.write(table);
}*/

/*function sleep(time){
    return new Promise((resolve) => setTimeout(resolve, time));
}

sleep(5000).then(() => {
    client.publish('mqtt/web', 'request');
})*/

