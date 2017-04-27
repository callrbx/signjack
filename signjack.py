#!/usr/bin/python2

from flask import Flask, render_template, redirect, url_for
app = Flask(__name__)

devices = []

@app.route("/")
def index():
  global devices
  return render_template("index.html", devices=devices)


@app.route("/scan", methods=['POST'])
def devScanButton():
  global devices
  devices = scanDevices()
  return redirect(url_for("index"))

@app.route("/clear", methods=['POST'])
def devClearButton():
  global devices
  devices = []
  return redirect(url_for("index"))


def scanDevices():
  devices = []
  devices.append(("192.168.1.1", "Grant"))
  devices.append(("192.168.1.2", "Ike First Floor"))
  return devices

def main():
  app.run(debug=True)

if __name__ == "__main__":
  main()
