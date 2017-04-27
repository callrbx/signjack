#!/usr/bin/python2

#Setup correct imports
import time, sys, re, socket, argparse

try:
  import nmap
except:
  print "install nmap library"
  exit(-1)

try:
  from flask import Flask, render_template, redirect, url_for, request
except:
  print "install flask"
  exit(-1)

#add some sort of sudo check

#The flask object our app runs on top of
app = Flask(__name__)

#Define the vendor id for BrightSign MAC
bsmac = "c0:56:27"  #using Belkin, as i do not have access to sign

#Global devices array; holds added device info
#Device entries stored in tuple: (IP, Location)
#Location is scraped from index of device
devices = []

#Determine our host ip; if not provided, use socket methods
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
host = ".".join(s.getsockname()[0].split(".")[:-1])+".0"
s.close()

#Map our index page
@app.route("/")
def index():
  global devices
  return render_template("index.html", devices=devices)

#Add a device by hand; no scanning required
@app.route("/add", methods=['POST'])
def manual_add():
  global devices
  devices.append((request.form["ip"], request.form["location"]))
  return redirect(url_for("index"))

#Leverages nmap to scan the LAN for BrightSign MACs
@app.route("/scan", methods=['POST'])
def dev_scan_button():
  global devices
  devices += scan_devices()
  return redirect(url_for("index"))

#Remove all devices from the global device list
@app.route("/clear", methods=['POST'])
def dev_clear_button():
  global devices
  devices = []
  return redirect(url_for("index"))

#Nmap LAN for BrightSign MACs
def scan_devices():
  global host
  devices = []
  nm = nmap.PortScanner()
  print host
  print "Scanning for network devices"
  nm.scan(host+'/28', arguments='-O')
  for h in nm.all_hosts():
      if 'mac' in nm[h]['addresses']:
          devices.append((nm[h]['addresses']['ipv4'], nm[h]['vendor'].values()[0]))

  return devices

def main():
  app.run(debug=True)

if __name__ == "__main__":
  main()
