import os
import socket
import requests
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
        #bt.logging.error(f"Port {port} on IP {ip} is not connected.")
        return False
    except socket.timeout:        
        #bt.logging.error(f"No response from Port {port} on IP {ip}.")
        return False
    except Exception as e:        
        #bt.logging.error(f"An error occurred: {e}")
        return False

    finally:
        # Close the socket regardless of whether an exception was raised
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
    assert response.status_code == 400



# def test_ok_auth_validator():    
#     url = f"http://{TEST_VALIDATOR_IP}:{VALIDATOR_PORT}/ping"
#     response = requests.get(url)
#     print(response.text)
#     assert response.status_code == 400