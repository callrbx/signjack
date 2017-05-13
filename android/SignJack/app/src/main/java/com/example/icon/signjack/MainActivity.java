package com.example.icon.signjack;

import android.os.AsyncTask;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.design.widget.BottomNavigationView;
import android.support.v7.app.AppCompatActivity;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;

import java.lang.reflect.Array;

public class MainActivity extends AppCompatActivity {
    //Variables
    //public String devices[][] = new String[255][2];

    //Instantiate Elements
    Button scan_button;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //Define Elements + Listeners
        scan_button = (Button)findViewById(R.id.scan_button);
        scan_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v){
                new Scanner().scanIP();
            }
        });
    }

    private class Scanner extends AsyncTask<Void, String, Void>{

        String subnet = "192.168.1.";
        int timeout = 5000;
        int current = 1;
        String devicesFound[] = new String[255];

        @Override
        protected void onPreExecute(){
        }

        @Override
        protected void doInBackground(Void... params){
            for(int cur=0; cur<255; cur++){
                String host = String.format("Scanning: %s%d",  subnet, cur);
                Button scan_button = (Button)findViewById(R.id.scan_button);
                scan_button.setText(host);
                try{
                    InetAddress inetAddress = InetAddress.getByName(host);
                    if (inetAddress.isReachable(timeout)) {
                        devicesFound[cur] = host;
                    }
                } catch (UnknownHostException e) {
                    e.printStackTrace();
                } catch (IOException e){
                        e.printStackTrace();
                }
            }
            scan_button.setText("Scan Devices");

    }
}
