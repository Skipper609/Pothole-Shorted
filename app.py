from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import model as m
import json
import threading

app = Flask(__name__)
CORS(app)



@app.route('/getAllPotholes', methods=['POST'])
def getAllPotholes():
    try:
        body = request.get_json()
        minLat = body['minLat']
        minLng = body['minLng']
        maxLat = body['maxLat']
        maxLang = body['maxLng']
        points = m.getAllPointsReport(minLng, minLat, maxLang, maxLat)
        return jsonify({"All Points": points})
    except Exception as e:
        return jsonify({"Error":str(e)})
        

@app.route('/potholes', methods=['POST'])
def getPotholes():
    res = []
# try:
    body = request.get_json()
    res = m.getPotholes(body['latitude'], body['longitude'],body['radius'],body['day'])
# except Exception as e:
    # return jsonify(f"error:{e}")
    return jsonify({"potholes":res})

@app.route('/test')
def connectionTest():
    return "<h1> App is up and running</h1>"

if __name__ == "__main__":
    app.run()
