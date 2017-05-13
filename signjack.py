#!/usr/bin/python2

#Setup correct imports
import time, sys, re, socket, urllib2, requests, os
from flask import Flask, render_template, redirect, url_for, request
from bs4 import BeautifulSoup
from subprocess import Popen, PIPE

#The flask object our app runs on top of
app = Flask(__name__)

#Define the vendor id for BrightSign MAC
bsmac = "90:ac:3f"

#Global devices array; holds added device info
#Device entries stored in tuple: (IP, Location)
#Location is scraped from index of device
devices = []


#File paths on the device
files = []
cur = 0


#Map our index page
@app.route("/")
def index():
  global devices, files, index
  return render_template("index.html", devices=devices, files=files, cur=cur)


#Add a device by hand; no scanning required
@app.route("/add", methods=['POST'])
def manual_add():
  global devices, files
  loc =  get_dev_loc(request.form["ip"])
  if loc is not None:
    devices.append((request.form["ip"], loc))
  return redirect(url_for("index"))


#Navigate images
@app.route("/skip", methods=['POST'])
def skip_file():
  global cur, files
  sel = request.form["move"]
  if "next" in sel:
    cur = cur+1 if cur+1 < len(files) else 0
  elif "replace" in sel:
    refile = request.files['file']
    refile.save(refile.filename)
    replace(files[cur], refile.filename)
  else:
    cur = cur-1 if cur-1 > 0 else 0
  return redirect(url_for("index"))


#Leverages nmap to scan the LAN for BrightSign MACs
@app.route("/scan", methods=['POST'])
def dev_scan_button():
  global bsmac, devices
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(("8.8.8.8", 80))
  host = ".".join(s.getsockname()[0].split(".")[:-1])
  s.close()
  devices = []
  FNULL = open(os.devnull)
  for n in range(0, 255):
    tgt = "{}.{}".format(host,n)
    Popen(["ping", "-c", "1", tgt], stdout=FNULL, stderr=FNULL)
    s = Popen(["arp", "-n", tgt], stdout=PIPE).communicate()[0]
    try:
      mac = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", s).groups()[0]
      if bsmac in mac:
        devices.append((tgt, get_dev_loc(tgt)))
    except:
      pass
  return redirect(url_for("index"))


#Remove all devices from the global device list
@app.route("/clear", methods=['POST'])
def dev_clear_button():
  global devices, files, cur
  cur = 0
  files = []
  devices = []
  return redirect(url_for("index"))


#Control backend for BrightSign utilities; reboot, etc.
@app.route("/control", methods=["POST"])
def control_panel():
  target = request.form["target"]
  command = request.form["command"]

  if "Reboot" in command:
    url = "http://{}/action.html?reboot=Reboot".format(target)
    urllib2.urlopen(url)
  else:
    url = "http://{}/storage.html?rp=sd/pool".format(target)
    spider(target, url)

  return redirect(url_for("index"))


#Scrape BrightSign webpage to determine device location
def get_dev_loc(ip):
  page = urllib2.urlopen("http://"+ip, timeout=2)
  content = BeautifulSoup(page, "html.parser")
  loc = content.find_all("td")[3].get_text()
  return loc


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
  global files
  files = []
  folders = []
  links = scrape_links(url)
  for l in links:
    for k in scrape_links("{}/{}".format(url, l[-1])):
       folders.append("http://{}{}".format(target, k))
  for f in folders:
    files += scrap_files(f)
  for i in range(len(files)):
    files[i] = "http://{}{}".format(target, files[i])


#The function that creates a backup and uploads a new one
def replace(furl, refile):
  tfurl = furl.replace("save", "tools")
  parts = furl.split("/")
  backurl = "http://{0}/rename?origfile=sd%2Fpool%2F{2}%2F{3}%2F{1}&custom=&filename={1}.backup&rename=Rename".format(parts[2], parts[-1], parts[-3], parts[-2])
  urllib2.urlopen(backurl)
  os.rename(refile, parts[-1])
  upurl = "http://{0}/upload.html?rp=sd/pool/{1}/{2}".format(parts[2], parts[-3], parts[-2])
  with open(parts[-1], 'rb') as f: r = requests.post(upurl, files={'report.xls': f})
  os.remove(parts[-1])


if __name__ == "__main__":
  app.config["UPLOAD_FOLDER"] = "."
  #app.run(debug=True, host="0.0.0.0", port=80)
  app.run(debug=True)


