import os
import requests
import time
import socket
from datetime import datetime

api_url = "http://localhost:8080/api/v2/"

def ensureDefectDojoRunning():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', 8080)) != 0:
            print("Defect dojo not running. Starting it now.")
          # https://github.com/DefectDojo/django-DefectDojo/blob/dev/readme-docs/DOCKER.md)
            os.system("cd django-DefectDojo && ./dc-up-d.sh postgres-redis")
            print("Waiting for a bit so that the initalizer finishes.")
            time.sleep(5)
        else:
            print("Port 8080 open. Expecting it to be defect dojo.")


def ensureProduct(project, api_token):
    product_id = ''
    headers = {
            'Authorization': f'Token {api_token}'
            }
    res = requests.get(f"{api_url}products?name={project}", headers=headers)
    if (res.json()['count'] == 0):
        print(f"No product with name {project}. Creating a new one.")
            # Create product
        data = {
                "name": project,
                "description": f"Automatically created product for {project}",
                "prod_type": 1,
                }
        res = requests.post(f"{api_url}products/",data=data,headers=headers)
        product_id = res.json()['id']
    else:
        product_id = res.json()['results'].pop()['id']
        
    return product_id

def getAdminPass():
    logs = os.popen('docker compose -f ./django-DefectDojo/docker-compose.yml logs initializer  | grep "Admin password:" ').read()
    return logs.split(' ')[5].strip()

def getApiToken(admin_password):
    data = {
            "username": "admin",
            "password": admin_password
            }
    print("HERE")
    print(data)
    res = requests.post(f"{api_url}api-token-auth/", data)
    print(res.status_code)
    return res.json()['token']

def ensureEngagement(engagement, api_token, product_id):
    headers = {
            'Authorization': f'Token {api_token}'
            }
    res = requests.get(f"{api_url}engagements/?name={engagement}", headers=headers)
    engagement_id = ''
    if (res.json()['count'] == 0):
        print(f"No engagement found with name {engagement}. Creating a new one.")
        data = {
                "name": engagement,
                "product": product_id,
                "target_start": datetime.today().strftime('%Y-%m-%d'),
                "target_end": datetime.today().strftime('%Y-%m-%d'),
                 "engagement_type": "CI/CD"

                }
        res = requests.post(f"{api_url}engagements/?name={engagement}", headers=headers, data=data)
        engagement_id = res.json()['id']

    else:
        engagement_id = res.json()['results'].pop()['id']

    return engagement_id

def uploadTestResults(file_path, engagement_id, scan_type, api_token):
    headers = {
            'Authorization': f'Token {api_token}'
            }

    data = {
        'active': True,
        'verified': True,
        'scan_type': scan_type,
        'minimum_severity': 'Low',
        'engagement': engagement_id
    }

    files = {
        'file': open(file_path, 'rb')
    }

    response = requests.post(f"{api_url}import-scan/", headers=headers, data=data, files=files)

    if response.status_code == 201:
        print('Scan results imported successfully')
    else:
        print(f'Failed to import scan results: {response.content}')

def requestsDebug():
    import logging
    import http.client as http_client

    # These two lines enable debugging at httplib level (requests->urllib3->http.client)
    # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # The only thing missing will be the response.body which is not logged.
    http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
