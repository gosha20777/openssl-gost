import os
import subprocess
from flask import Flask
from flask import request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'status': "server is running"}), 200

@app.route('/<sert_lacation>/<query>', methods=['GET', 'POST'])
def ros_riestr_gost2012(sert_lacation, query):
    if request.method == 'GET':
        response = get_gost2012_request(sert_lacation, "https://portal.rosreestr.ru:4455/" + query)
        return response, 200
    elif request.method == 'POST':
        body = request.data
        headers = request.headers
        return post_gost2012_request(sert_lacation, "https://portal.rosreestr.ru:4455/" + query, headers, body), 200

@app.route('/<sert_lacation>/cxf/<query>', methods=['GET', 'POST'])
def ros_riestr_gost2012_1(sert_lacation, query):
    if request.method == 'GET':
        return get_gost2012_request(sert_lacation, "https://portal.rosreestr.ru:4455/cxf/" + query)
    elif request.method == 'POST':
        body = request.data
        headers = request.headers
        return post_gost2012_request(sert_lacation, "https://portal.rosreestr.ru:4455/cxf/" + query, headers, body), 200



def get_gost2012_request(sert_lacation, url):
    print("[INFO] sent request to {}".format(url))
    process = subprocess.Popen('curl -s {0} -k -v --key {1}/key.pem --cert {1}/cert.pem'.format(url, sert_lacation), stdout=subprocess.PIPE, stderr=None, shell=True)
    #Launch the shell command:
    output, _ = process.communicate()
    if "curl:" in output.decode("utf-8"):
        respone = {"error": output.decode("utf-8").replase("curl:", "")}
        print("[ERROR] get curl error: {}".format(respone))
        output = json.dumps(respone)
    
    print("[INFO] recive request from {}".format(url))
    return output

def post_gost2012_request(sert_lacation, url, headers, body):

    """
    curl -X POST   https://portal.rosreestr.ru:4455/cxf/External -H 'Accept-Encoding: gzip, deflate'   -H 'Content-Type: text/plain'   -H 'SOAPAction: "urn:ws.request.pgu.sids.fccland.ru/getEvents"'   -d '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:ws.request.pgu.sids.fccland.ru">
   <soapenv:Header/>
   <soapenv:Body>
      <urn:getEvents>
         <lastEventID>1820769a-7c4d-47d1-9b45-aa179361473c/STATUS/000/1573618247447</lastEventID>
      </urn:getEvents>
   </soapenv:Body>
</soapenv:Envelope>' -k -v --key key.pem --cert cert.pem
    """

    print("[INFO] sent request to {}".format(url))
    soap_action = ""
    for (key, value) in headers:
        if '{}'.format(key).lower() == 'soapaction':
            soap_action = '{0}'.format(value)
    
    if soap_action == "":
        respone = {"error": "SOAPAction is empty"}
        print("[ERROR] get curl error: {}".format(respone))
        return json.dumps(respone)

    curl_string = '-s -X POST {0} -H \'Accept-Encoding: gzip, deflate\' -H \'Content-Type: text/plain\' -H \'SOAPAction: {1}\' -d \'{2}\' -k -v --key {3}/key.pem --cert {3}/cert.pem'.format(url, soap_action, body.decode("utf-8"), sert_lacation)
    process = subprocess.Popen('curl {}'.format(curl_string), stdout=subprocess.PIPE, stderr=None, shell=True)
    #Launch the shell command:
    output, _ = process.communicate()

    if "curl:" in output.decode("utf-8"):
        respone = {"error": output.decode("utf-8").replase("curl:", "")}
        print("[ERROR] get curl error: {}".format(respone))
        output = json.dumps(respone)
    
    print("[INFO] recive request from {}".format(url))
    return output


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)