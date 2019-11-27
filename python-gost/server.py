import os
import subprocess
from flask import Flask
from flask import request, jsonify, Response
import json
import datetime
import logging

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
        response = post_gost2012_request(sert_lacation, "https://portal.rosreestr.ru:4455/" + query, headers, body)
        return response, 200

@app.route('/<sert_lacation>/cxf/<query>', methods=['GET', 'POST'])
def ros_riestr_gost2012_1(sert_lacation, query):
    if request.method == 'GET':
        response = get_gost2012_request(sert_lacation, "https://portal.rosreestr.ru:4455/cxf/" + query)
        return response, 200
    elif request.method == 'POST':
        body = request.data
        headers = request.headers
        response = post_gost2012_request(sert_lacation, "https://portal.rosreestr.ru:4455/cxf/" + query, headers, body)
        return Response(response, status=200, content_type="text/xml; charset=utf-8") # response, 200



def get_gost2012_request(sert_lacation, url):
    logging.info("send GET request to {}".format(url))
    
    curl_string = '-s {0} -k -v --key {1}/key.pem --cert {1}/cert.pem'.format(url + '?wsdl', sert_lacation)
    filename = 'log_raw/{0}_{1}'.format(datetime.datetime.now(), hash(curl_string)).replace(" ", "_")

    f = open('{0}.request_string.txt'.format(filename), 'w')
    f.write("curl " + curl_string)
    f.close()

    process = subprocess.Popen('curl {0}'.format(curl_string), stdout=subprocess.PIPE, stderr=None, shell=True)
    
    #Launch the shell command:
    output, _ = process.communicate()
    
    logging.info("recive GET response to {}".format(url))
    f = open('{0}.response.txt'.format(filename), 'wb')
    f.write(output)
    f.close()

    if output == None or output.decode("utf-8") == "":
        output = get_soap_errer_message("https://portal.rosreestr.ru:4455/ unuvalable")
        logging.error("https://portal.rosreestr.ru:4455/ unuvalable")
        return output
    
    return output.decode("utf-8")

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

    logging.info("send POST request to {}".format(url))

    soap_action = ""
    for (key, value) in headers:
        if '{}'.format(key).lower() == 'soapaction':
            soap_action = '{0}'.format(value)
    
    if soap_action == "":
        respone = get_soap_errer_message("SOAPAction is empty")
        logging.error("SOAPAction is empty")
        return respone

    filename = 'log_raw/{0}_{1}'.format(datetime.datetime.now(), hash(body)).replace(" ", "_")
    f = open('{0}.body.txt'.format(filename), 'wb')
    f.write(body)
    f.close()

    curl_string = '-s -X POST {0} -H \'Accept-Encoding: gzip, deflate\' -H \'Content-Type: text/plain\' -H \'SOAPAction: {1}\' -d @{2} -k -v --key {3}/key.pem --cert {3}/cert.pem'.format(url, soap_action, filename + '.body.txt', sert_lacation)
    f = open('{0}.request_string.txt'.format(filename), 'w')
    f.write("curl " + curl_string)
    f.close()

    process = subprocess.Popen('curl {}'.format(curl_string), stdout=subprocess.PIPE, stderr=None, shell=True)
    #Launch the shell command:
    output, _ = process.communicate()
    
    logging.info("recive POST response to {}".format(url))
    f = open('{0}.response.txt'.format(filename), 'wb')
    f.write(output)
    f.close()

    if output == None or output.decode("utf-8") == "":
        output = get_soap_errer_message("https://portal.rosreestr.ru:4455/ unuvalable")
        logging.error("https://portal.rosreestr.ru:4455/ unuvalable")
        return output

    return output.decode("utf-8")

def get_soap_errer_message(message):
    errror_str = '''<?xml version = '1.0' encoding = 'UTF-8'?>
<SOAP-ENV:Envelope
   xmlns:SOAP-ENV = "http://schemas.xmlsoap.org/soap/envelope/"
   xmlns:xsi = "http://www.w3.org/1999/XMLSchema-instance"
   xmlns:xsd = "http://www.w3.org/1999/XMLSchema">

   <SOAP-ENV:Body>
      <SOAP-ENV:Fault>
         <faultcode xsi:type = "xsd:string">SOAP-ENV:Client</faultcode>
         <faultstring xsi:type = "xsd:string">
            {0}
         </faultstring>
      </SOAP-ENV:Fault>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''.format(message)
    return errror_str


if __name__ == '__main__':
    if not os.path.isdir('log/'):
        os.mkdir('log')
    if not os.path.isdir('log_raw/'):
        os.mkdir('log_raw')
    
    logging.basicConfig(filename="log/main.log", level=logging.INFO)
    logging.info("server start at 0.0.0.0:80")
    app.run(debug=True, host='0.0.0.0', port=80)