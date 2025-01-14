import requests
requests.packages.urllib3.disable_warnings() 
import urllib3
urllib3.disable_warnings()
import pytest

VALIDATOR_IP = "10.0.0.40"
VALIDATOR_PORT = "8091"

SECRET_KEY = "change-me"


# @pytest.fixture
# def disable_ssl_verification():
#     original_verify = requests.Session().verify
#     requests.Session().verify = False
#     yield
#     requests.Session().verify = original_verify


def get(url, headers=None):
    response = requests.get(url, headers=headers, verify=False)
    print(response.status_code)
    print(response.text)
    return response

def post(url, data, headers):
    response = requests.post(url, data=data, headers=headers, verify=False)
    print(response.status_code)
    print(response.text)
    return response


def test_validator_has_ssl():
    ip = VALIDATOR_IP
    port = VALIDATOR_PORT
    url = f"https://{ip}:{port}/ping"  
    res = get(url)
    assert res.status_code == 200
    


def test_can_not_ping_validator_no_auth_api():
    ip = VALIDATOR_IP
    port = VALIDATOR_PORT
    url = f"http://{ip}:{port}/ping"
    print(f"testing url {url}")
    response = requests.get(url, verify=False)
    print(response.status_code)
    #print(response.text)
    detail = response.json()
    print(detail)
    assert response.status_code == 400
    assert detail["detail"] == "Authorization is missing"


def test_can_not_ping_validator_no_auth_api_ssl():
    ip = VALIDATOR_IP
    port = VALIDATOR_PORT
    url = f"https://{ip}:{port}/ping"
    print(f"testing url {url}")
    try:
        response = requests.get(url, verify=False)
        print(response.status_code)
        print(response.text)
        detail = response.json()
        print(detail)
        assert response.status_code == 400
        assert detail["detail"] == "Authorization is missing"

    except requests.exceptions.SSLError as e:       
        print(e)
        print("SSL Error - validator does not have SSL enabled")    
   

def test_can_not_ping_validator_with_wrong_auth_api():
    ip = VALIDATOR_IP
    port = VALIDATOR_PORT
    url = f"http://{ip}:{port}/ping"
    print(f"testing url {url}")
    headers = {"Authorization": "Bearer 123"}
    response = requests.get(url, headers=headers, verify=False)
    print(response.status_code)
    #print(response.text)
    detail = response.json()
    print(detail)
    assert 401 == response.status_code
    assert "Invalid API key request" in detail["detail"]


def test_can_ping_validator_with_auth_api():
    ip = VALIDATOR_IP
    port = VALIDATOR_PORT
    url = f"http://{ip}:{port}/ping"
    print(f"testing url {url}")
    headers = {"Authorization": SECRET_KEY}
    response = requests.get(url, headers=headers, verify=False)
    print(response.status_code)
    #print(response.text)
    detail = response.json()
    print(detail)
    assert response.status_code == 200
    assert detail["detail"] == "pong"


    
if __name__ == "__main__":
    print("tbd")


