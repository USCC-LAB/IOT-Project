package com.example.johnny.final_product;

import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import com.google.firebase.messaging.FirebaseMessaging;

import java.io.IOException;
import java.io.OutputStreamWriter;

import uk.co.deanwild.materialshowcaseview.MaterialShowcaseSequence;
import uk.co.deanwild.materialshowcaseview.ShowcaseConfig;

public class Main2Activity extends AppCompatActivity {
    String user_name;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main2);
        Bundle bundle = getIntent().getExtras();
        user_name = bundle.getString("user_name");
        FirebaseMessaging.getInstance().subscribeToTopic(user_name);
        Toast.makeText(Main2Activity.this,"歡迎，使用者  "+user_name,Toast.LENGTH_LONG).show();
        ImageButton data = (ImageButton)findViewById(R.id.imageButton);
        ImageButton water = (ImageButton)findViewById(R.id.imageButton2);
        ImageButton logout = (ImageButton)findViewById(R.id.imageButton9);
        data.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent2 = new Intent();
                intent2.setClass(Main2Activity.this,Main3Activity.class);
                Bundle bundle2 = new Bundle();
                bundle2.putString("user_name",user_name);
                intent2.putExtras(bundle2);
                startActivity(intent2);
            }
        });
        water.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent3 = new Intent();
                intent3.setClass(Main2Activity.this,Main4Activity.class);
                Bundle bundle3 = new Bundle();
                bundle3.putString("user_name",user_name);
                intent3.putExtras(bundle3);
                startActivity(intent3);
            }
        });

        logout.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                AlertDialog.Builder adb=new AlertDialog.Builder(Main2Activity.this);
                adb.setTitle("登出");
                adb.setMessage("確認登出?");
                adb.setNegativeButton("取消", null);
                adb.setPositiveButton("確定", new AlertDialog.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        FirebaseMessaging.getInstance().unsubscribeFromTopic(user_name);
                        writeToFile("null",Main2Activity.this);
                        startActivity(new Intent(Main2Activity.this,HomeActivity.class));
                        finish();
                    }});
                adb.show();
            }
        });

        ShowcaseConfig config = new ShowcaseConfig();
        config.setDelay(300);
        MaterialShowcaseSequence sequence = new MaterialShowcaseSequence(this, "0");
        sequence.setConfig(config);
        sequence.addSequenceItem(data,"按此查看感測器數據", "知道了");
        sequence.addSequenceItem(water,"按此查看澆灌頁面", "知道了");
        sequence.addSequenceItem(logout,"按此登出", "知道了");
        sequence.start();
    }

    private void writeToFile(String data,Context context) {
        try {
            OutputStreamWriter outputStreamWriter = new OutputStreamWriter(context.openFileOutput("username.txt", Context.MODE_PRIVATE));
            outputStreamWriter.write(data);
            outputStreamWriter.close();
        }
        catch (IOException e) {
            Log.e("Exception", "File write failed: " + e.toString());
        }
    }
}
