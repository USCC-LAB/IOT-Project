package com.example.johnny.final_product;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.method.ScrollingMovementMethod;
import android.view.View;
import android.view.Window;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.CompoundButton;
import android.widget.GridLayout;
import android.widget.Spinner;
import android.widget.TextView;
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

public class Main3Activity extends AppCompatActivity {

    static  String mqtt_host = "tcp://140.116.82.42:1883";
    String selected_gateway = "001";
    String selected_module = "001";
    String msg = "";
    String[] data;
    MqttAndroidClient client;
    TextView[] tv;
    String user_name;
    List<String> gateway;
    List<String> module;
    ArrayAdapter<String> module_adp;
    ArrayAdapter<String> gateway_adp;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main3);
        Bundle bundle = getIntent().getExtras();
        user_name = bundle.getString("user_name");
        Spinner spinner_module = (Spinner)findViewById(R.id.spinner);
        Spinner spinner_gateway = (Spinner)findViewById(R.id.spinner2);
        tv = new TextView[7];
        tv[0] = (TextView)findViewById(R.id.textView10);
        tv[1] = (TextView)findViewById(R.id.textView13);
        tv[2] = (TextView)findViewById(R.id.textView11);
        tv[3] = (TextView)findViewById(R.id.textView14);
        tv[4] = (TextView)findViewById(R.id.textView12);
        tv[5] = (TextView)findViewById(R.id.textView15);
        tv[6] = (TextView)findViewById(R.id.textView17);
        ShowcaseConfig config = new ShowcaseConfig();
        config.setDelay(300);
        MaterialShowcaseSequence sequence = new MaterialShowcaseSequence(this, "1");
        sequence.setConfig(config);
        sequence.addSequenceItem(spinner_gateway,"按此選擇欲察看之農田", "知道了");
        sequence.addSequenceItem(spinner_module,"按此選擇欲察看之感測器", "知道了");
        sequence.start();

        gateway = new ArrayList<>();
        gateway.add("001");
        gateway_adp = new ArrayAdapter<>(Main3Activity.this,
                android.R.layout.simple_spinner_dropdown_item,
                gateway);
        spinner_gateway.setAdapter(gateway_adp);
        spinner_gateway.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                selected_gateway = gateway.get(position);
                for(int i=0;i<7;i++){
                    tv[i].setText("");
                }
            }
            @Override
            public void onNothingSelected(AdapterView<?> parent) {
            }
        });

        module = new ArrayList<>();
        module.add("001");
        module_adp = new ArrayAdapter<>(Main3Activity.this,
                android.R.layout.simple_spinner_dropdown_item,
                module);
        spinner_module.setAdapter(module_adp);
        spinner_module.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                selected_module = module.get(position);
                for(int i=0;i<7;i++){
                    tv[i].setText("");
                }
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
                    Toast.makeText(Main3Activity.this,"連線成功",Toast.LENGTH_SHORT).show();
                    //subscribe_topic();
                    subscribe_topic(user_name+"/#");
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    // Something went wrong e.g. connection timeout or firewall problems
                    Toast.makeText(Main3Activity.this,"連線失敗",Toast.LENGTH_LONG).show();
                    finish();
                }
            });
        } catch (MqttException e) {
            e.printStackTrace();
        }
        client.setCallback(new MqttCallback() {
            @Override
            public void connectionLost(Throwable cause) {
                Toast.makeText(Main3Activity.this,"連線中斷",Toast.LENGTH_LONG).show();
                finish();
            }

            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {
                msg = new String(message.getPayload());
                //decode sensor data
                if(topic.equals(user_name+"/gateway_"+selected_gateway+"/module_"+selected_module+"/data")){
                    data = msg.split("/");
                    tv[0].setText(data[3].substring(data[3].indexOf(':')+1)+" ℃");
                    tv[1].setText(data[4].substring(data[4].indexOf(':')+1)+" %");
                    tv[2].setText(data[5].substring(data[5].indexOf(':')+1)+" mV");
                    tv[3].setText(data[6].substring(data[6].indexOf(':')+1)+" mV");
                    tv[4].setText(data[7].substring(data[7].indexOf(':')+1)+" %");
                    tv[5].setText(data[8].substring(data[8].indexOf(':')+1)+" hPa");
                    tv[6].setText(data[9].substring(data[9].indexOf(':')+1));
                }
            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {

            }
        });
    }

    public void subscribe_topic(String topic){
        try {
            client.subscribe(topic,0);
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }
}
