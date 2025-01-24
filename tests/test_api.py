import os
import socket
import time
import requests
from bitrecs.utils.version import LocalMetadata
from bitrecs.validator.forward import get_bitrecs_dummy_request
from dotenv import load_dotenv
load_dotenv()


TEST_VALIDATOR_IP = os.getenv("TEST_VALIDATOR_IP")
if not TEST_VALIDATOR_IP:
    TEST_VALIDATOR_IP = "127.0.0.1"
VALIDATOR_PORT = 8091
VALIDATOR_IS_SSL = False
print(f"Running tests on validator IP: {TEST_VALIDATOR_IP} with port: {VALIDATOR_PORT}")

BITRECS_API_KEY = os.getenv("BITRECS_API_KEY")
if BITRECS_API_KEY is None:
    raise ValueError("BITRECS_API_KEY")


def socket_ip(ip, port, timeout=10) -> bool:
    try:        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
        sock.settimeout(timeout)        
        sock.connect((ip, port))
        return True
    except ConnectionRefusedError:
        print(f"Connection refused to {ip}:{port}")
        return False
    except socket.timeout:
        print(f"Connection timeout to {ip}:{port}")
        return False
    except Exception as e:
        print(f"Error connecting to {ip}:{port} - {e}")
        return False

    finally:        
        if 'sock' in locals():
            sock.close()
   


def test_can_reach_validator():    
    success = socket_ip(TEST_VALIDATOR_IP, VALIDATOR_PORT)    
    assert success == True


def test_no_auth_error_validator():
    url = f"http://{TEST_VALIDATOR_IP}:{VALIDATOR_PORT}/ping"
    response = requests.get(url)
    print(response.text)
    assert response.status_code == 400


def test_wrong_auth_error_validator():    
    url = f"http://{TEST_VALIDATOR_IP}:{VALIDATOR_PORT}/ping"
    headers = {
        "Authorization": "Bearer wrong"
    }            
    response = requests.get(url, headers=headers)
    print(response.text)
    assert response.status_code == 401


def test_good_auth_validator():    
    url = f"http://{TEST_VALIDATOR_IP}:{VALIDATOR_PORT}/ping"
    headers = {
        "Authorization": f"Bearer {BITRECS_API_KEY}"
    }
    response = requests.get(url, headers=headers)
    print(response.text)
    assert response.status_code == 200


def test_good_server_time_validator():    
    url = f"http://{TEST_VALIDATOR_IP}:{VALIDATOR_PORT}/ping"
    headers = {
        "Authorization": f"Bearer {BITRECS_API_KEY}"
    }
    response = requests.get(url, headers=headers)
    print(response.text)
    assert response.status_code == 200
    st = response.json()["st"]
    assert st > 0
    current_time = int(time.time())
    over_5_minutes = current_time - st > 300
    assert over_5_minutes == False


def test_version_ok_validator():    
    url = f"http://{TEST_VALIDATOR_IP}:{VALIDATOR_PORT}/version"
    headers = {
        "Authorization": f"Bearer {BITRECS_API_KEY}"
    }
    response = requests.get(url, headers=headers)
    print(response.text)    
    assert response.status_code == 200
    meta_json = response.json()["meta_data"]
    md = LocalMetadata(**meta_json)
    #print(md)
    assert md.head != "head error"


def test_rec_no_sig_is_rejected_ok():
    url = f"http://{TEST_VALIDATOR_IP}:{VALIDATOR_PORT}/rec"
    headers = {
        "Authorization": f"Bearer {BITRECS_API_KEY}",
        "x-timestamp": str(int(time.time()))
    }
    br = get_bitrecs_dummy_request(5)
    data = br.model_dump()
    response = requests.post(url, headers=headers, json=data)
    print(response.text)
    assert response.status_code == 422 #missing headers



def test_rec_wrong_sig_rejected_ok():
    url = f"http://{TEST_VALIDATOR_IP}:{VALIDATOR_PORT}/rec"
    headers = {
        "Authorization": f"Bearer {BITRECS_API_KEY}",
        "x-signature": "wrong",
        "x-timestamp": str(int(time.time()))
    }
    br = get_bitrecs_dummy_request(5)
    data = br.model_dump()
    response = requests.post(url, headers=headers, json=data)
    print(response.text)
    assert response.status_code == 401


