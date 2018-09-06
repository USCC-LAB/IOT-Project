package com.example.johnny.final_product;

import android.app.Activity;
import android.app.TimePickerDialog;
import android.content.DialogInterface;
import android.graphics.Rect;
import android.support.v4.content.res.ResourcesCompat;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.Layout;
import android.text.method.ScrollingMovementMethod;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.TimePicker;
import android.widget.Toast;
import android.widget.ToggleButton;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

import java.util.ArrayList;
import java.util.List;

import uk.co.deanwild.materialshowcaseview.MaterialShowcaseSequence;
import uk.co.deanwild.materialshowcaseview.ShowcaseConfig;

public class Main4Activity extends AppCompatActivity {
    static  String mqtt_host = "tcp://140.116.82.42:1883";
    String selected_module = "001";
    MqttAndroidClient client;
    List<String> schedule_msg;
    List<String> schedule;
    List<String> module;
    ArrayAdapter<String> schedule_adapter;
    ListView listView;
    final String[] data_type = {"氣溫大於","土壤溼度小於"};//{"Temperature","Humidity","Light","UV","Soil Humidity","Air Pressure"};
    final String[] op ={">","<"};
    int type_i=0,op_i=0;
    ToggleButton toggleButton;
    String recv;
    String[] recv_scheldule;
    String user_name;
    CompoundButton.OnCheckedChangeListener toggle_btn_listener;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main4);
        Bundle bundle = getIntent().getExtras();
        user_name = bundle.getString("user_name");
        final Spinner spinner = (Spinner)findViewById(R.id.spinner3);
        schedule_msg = new ArrayList<>();
        schedule = new ArrayList<>();
        listView = (ListView)findViewById(R.id.schedule_list);
        schedule_adapter = new ArrayAdapter<String>(Main4Activity.this,R.layout.mytextview,schedule);
        listView.setAdapter(schedule_adapter);
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                AlertDialog.Builder adb=new AlertDialog.Builder(Main4Activity.this);
                adb.setTitle("刪除");
                adb.setMessage("確認刪除?");
                final int positionToRemove = position;
                adb.setNegativeButton("取消", null);
                adb.setPositiveButton("確定", new AlertDialog.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        schedule.remove(positionToRemove);
                        schedule_msg.remove(positionToRemove);
                        schedule_adapter.notifyDataSetChanged();
                        schedule_update();
                    }});
                adb.show();
            }
        });
        module = new ArrayList<>();
        module.add("001");
        ArrayAdapter<String> moduleList = new ArrayAdapter<>(Main4Activity.this,
                android.R.layout.simple_spinner_dropdown_item,
                module);
        spinner.setAdapter(moduleList);
        spinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                selected_module = module.get(position);
            }
            @Override
            public void onNothingSelected(AdapterView<?> parent) {
            }
        });
        String clientId = MqttClient.generateClientId();
        client = new MqttAndroidClient(this.getApplicationContext(), mqtt_host, clientId
                ,new MemoryPersistence(),MqttAndroidClient.Ack.AUTO_ACK);
        MqttConnectOptions options = new MqttConnectOptions();
        options.setUserName("applogin");
        options.setPassword("123456".toCharArray());
        try {
            IMqttToken token = client.connect(options);
            token.setActionCallback(new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    Toast.makeText(Main4Activity.this,"連線成功",Toast.LENGTH_SHORT).show();
                    subscribe_topic(user_name+"/#");
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Toast.makeText(Main4Activity.this,"連線失敗",Toast.LENGTH_LONG).show();
                    finish();
                }
            });
        } catch (MqttException e) {
            e.printStackTrace();
        }
        client.setCallback(new MqttCallback() {
            @Override
            public void connectionLost(Throwable cause) {
                Toast.makeText(Main4Activity.this,"連線中斷",Toast.LENGTH_LONG).show();
                finish();
            }

            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {
                recv = new String(message.getPayload());
                if(topic.equals(user_name+"/gateway_"+selected_module+"/control")){
                    if(recv.equals("OFF")){
                        toggleButton.setOnCheckedChangeListener(null);
                        toggleButton.setChecked(false);
                        toggleButton.setBackground(ResourcesCompat.getDrawable(getResources(), R.drawable.off, null));
                        toggleButton.setOnCheckedChangeListener(toggle_btn_listener);
                    }
                    else if(recv.equals("ON")){
                        toggleButton.setOnCheckedChangeListener(null);
                        toggleButton.setChecked(true);
                        toggleButton.setBackground(ResourcesCompat.getDrawable(getResources(), R.drawable.on, null));
                        toggleButton.setOnCheckedChangeListener(toggle_btn_listener);
                    }
                }
                if(topic.equals(user_name+"/gateway_"+selected_module+"/schedule")){
                    schedule_msg.clear();
                    schedule.clear();
                    recv_scheldule = recv.split(" ");

                    for(int i=0;i<recv_scheldule.length;i++){
                        if(recv_scheldule[i].charAt(0)=='1'){
                            schedule.add(recv_scheldule[i].substring(2));
                        }
                        else if(recv_scheldule[i].charAt(0)=='2'){
                            schedule.add("氣溫大於 "+recv_scheldule[i].substring(3)+" ℃ 時澆水");
                        }
                        else if(recv_scheldule[i].charAt(0)=='3'){
                            schedule.add("土壤溼度小於 "+recv_scheldule[i].substring(3)+" % 時澆水");
                        }
                        schedule_msg.add(recv_scheldule[i]+" ");
                    }
                    schedule_adapter.notifyDataSetChanged();
                }
            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {
            }
        });
        toggleButton = (ToggleButton) findViewById(R.id.toggleButton2);
        toggle_btn_listener = new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if(isChecked){
                    toggleButton.setBackground(ResourcesCompat.getDrawable(getResources(), R.drawable.on, null));
                    publish_msg(user_name+"/gateway_"+selected_module+"/control","ON");
                }
                else {
                    toggleButton.setBackground(ResourcesCompat.getDrawable(getResources(), R.drawable.off, null));
                    publish_msg(user_name+"/gateway_"+selected_module+"/control","OFF");
                }
            }
        };
        toggleButton.setOnCheckedChangeListener(toggle_btn_listener);

        ImageButton button_add_timer = (ImageButton)findViewById(R.id.button_add_timer);
        button_add_timer.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                new TimePickerDialog(Main4Activity.this, new TimePickerDialog.OnTimeSetListener(){
                    @Override
                    public void onTimeSet(TimePicker view, int hour, int minute) {
                        if(view.isShown()) {
                            String h = hour + "";
                            String m = minute + "";
                            if(hour<10) h = "0"+h;
                            if(minute<10) m = "0"+m;
                            schedule.add(h + ":" + m);
                            schedule_msg.add("1:"+h+":"+m+" ");
                            schedule_adapter.notifyDataSetChanged();
                            schedule_update();
                        }
                    }
                }, 0, 0, true).show();
            }
        });
        ImageButton button_add = (ImageButton)findViewById(R.id.button_add);
        button_add.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                AlertDialog.Builder builder = new AlertDialog.Builder(Main4Activity.this);
                View mView = getLayoutInflater().inflate(R.layout.layout_dialog,null);
                Spinner spinner_type = (Spinner) mView.findViewById(R.id.spinner_type);
                Spinner spinner_op = (Spinner) mView.findViewById(R.id.spinner_op);
                final EditText editText_val = (EditText) mView.findViewById(R.id.editText_val);
                final ArrayAdapter<String> type_list = new ArrayAdapter<>(Main4Activity.this,
                        android.R.layout.simple_spinner_dropdown_item,
                        data_type);
                final ArrayAdapter<String> op_list = new ArrayAdapter<>(Main4Activity.this,
                        android.R.layout.simple_spinner_dropdown_item,
                        op);
                spinner_type.setAdapter(type_list);
                spinner_op.setAdapter(op_list);
                spinner_op.setAlpha(0.0f);
                spinner_type.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
                    @Override
                    public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                        type_i = position;
                    }
                    @Override
                    public void onNothingSelected(AdapterView<?> parent) {
                    }
                });
                spinner_op.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
                    @Override
                    public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                        op_i = position;
                    }
                    @Override
                    public void onNothingSelected(AdapterView<?> parent) {
                    }
                });
                builder.setView(mView);
                ShowcaseConfig config = new ShowcaseConfig();
                config.setDelay(300);
                builder.setNegativeButton("Cancel",null);
                builder.setPositiveButton("Ok", new AlertDialog.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        if(!editText_val.getText().toString().equals("")){
                            schedule.add(data_type[type_i] + " " + op[type_i] + " " + editText_val.getText().toString());
                            schedule_msg.add((type_i+2)+":"+op[type_i]+editText_val.getText().toString()+" ");
                            schedule_adapter.notifyDataSetChanged();
                            schedule_update();
                        }
                    }});
                builder.show();
            }
        });

        TextView tv = (TextView)findViewById(R.id.textView19);
        tv.setAlpha(0.0f);
        ShowcaseConfig config = new ShowcaseConfig();
        config.setDelay(300);
        MaterialShowcaseSequence sequence = new MaterialShowcaseSequence(this, "2");
        sequence.setConfig(config);
        sequence.addSequenceItem(spinner,"按此選擇欲澆灌之農田", "知道了");
        sequence.addSequenceItem(button_add_timer,"按此新增澆水時間", "知道了");
        sequence.addSequenceItem(button_add,"按此新增澆水規則", "知道了");
        sequence.addSequenceItem(toggleButton,"按此開關水閥", "知道了");
        sequence.addSequenceItem(tv,"透過點擊來刪除澆水時間或規則", "知道了");
        sequence.start();
    }

    public void publish_msg(String topic,String msg){
        try {
            client.publish(topic,
                    msg.getBytes(),0,true);
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }

    public void subscribe_topic(String topic) {
        try {
            client.subscribe(topic, 0);
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }

    void schedule_update(){
        String msg = "";
        for(int i=0;i<schedule_msg.size();i++){
            msg += schedule_msg.get(i);
        }
        publish_msg(user_name+"/gateway_"+selected_module+"/schedule",msg);
    }
}
