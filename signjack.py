#!/usr/bin/python2

#Setup correct imports
import time, sys, re, socket, nmap, urllib2
from flask import Flask, render_template, redirect, url_for, request
from bs4 import BeautifulSoup

#add some sort of sudo check

#The flask object our app runs on top of
app = Flask(__name__)
nm = nmap.PortScanner()

#Define the vendor id for BrightSign MAC
bsmac = "90:ac:3f"  #using Belkin, as i do not have access to sign

#Global devices array; holds added device info
#Device entries stored in tuple: (IP, Location)
#Location is scraped from index of device
devices = [("192.168.113.109", "USMA Book Store")]
#devices = []

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
  loc =  get_dev_loc(request.form["ip"])
  if loc is not None:
    devices.append((request.form["ip"], loc))
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


#Control backend for BrightSign utilities; reboot, etc.
@app.route("/control", methods=["POST"])
def control_panel():
  target = request.form["target"]
  command = request.form["command"]

  if command is "Reboot":
    url = "http://{}/action.html?reboot=Reboot".format(target)
    urllib2.urlopen(url)
  else:
    url = "http://{}/storage.html?rp=sd/pool".format(target)
    spider(target, url)
     
  return redirect(url_for("index"))

  
#Nmap LAN for BrightSign MACs
def scan_devices():
  global host, bsmac, nm
  devices = []
  nm.scan(host+'/24', arguments='-O')
  for h in nm.all_hosts():
    if 'mac' in nm[h]['addresses']:
      if bsmac in nm[h]['vendor'].keys()[0].lower():
        ip = nm[h]['addresses']['ipv4']
        devices.append((ip, get_dev_loc(ip)))
  return devices

#Scrape BrightSign webpage to determine device location
def get_dev_loc(ip):
  try:
    page = urllib2.urlopen("http://"+ip, timeout=2)
    content = BeautifulSoup(page, "html.parser")
    loc = content.find_all("td")[3].get_text()
    return loc
  except:
    pass

def scrape_links(url):
    page = urllib2.urlopen(url)
    page = BeautifulSoup(page, "html.parser")
    links = page.find_all("a", href=True) 
    content = [l["href"] for l in links if "pool" in l["href"] and "kill" not in l["href"]]
    return content

def scrap_files(url):
    page = urllib2.urlopen(url)
    page = BeautifulSoup(page, "html.parser")
    links = page.find_all("a", href=True) 
    content = [l["href"] for l in links if "sha" in l["href"] and "kill" not in l["href"]]
    files = [f for f in content if "save" in f]
    return files

#Spider function to find all possible pictures on the BrightSign
def spider(target, url):
  folders = []
  files = []
  links = scrape_links(url)
  for l in links:
    for k in scrape_links("{}/{}".format(url, l[-1])):
       folders.append("http://{}{}".format(target, k))
  for f in folders:
    files += scrap_files(f)
  for i in range(len(files)):
    files[i] = "http://{}{}".format(target, files[i])
  return files
    

if __name__ == "__main__":
  app.run(debug=True)





