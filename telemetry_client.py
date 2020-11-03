import sys
import re
import traceback
import paramiko
from websocket import create_connection
from time import sleep

HOSTNAME = "192.168.0.117"
USERNAME = "deepracer"
PASSWORD = "deepracer"
SERVER_URL = "ws://localhost:8000/ws/0"

p = re.compile('msg: "Setting throttle to (\d+\.\d+)"')

def websocket_connect():
    while True:
        try:
            websocket = create_connection(SERVER_URL, timeout=0.1)
            print("Websocket connected")
            return websocket
        except Exception as e:
            print("Failed to open websocket: %s" % e)
        sleep(1)


ws = websocket_connect()

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, 22, USERNAME, PASSWORD)

    print("connected")

    stdin, stdout, stderr = client.exec_command("source /opt/ros/kinetic/setup.bash; rostopic echo /rosout_agg")
    stdin.close()
    for line in iter(lambda: stdout.readline(2048), ""):
        # print(line, end="")
        if "Setting throttle to" in line:
            match = p.match(line)
            throttle_raw = float(match.group(1))
            throttle = round(throttle_raw * 100)
            print(throttle)
            try:
                ws.send(str(throttle))
            except Exception as e:
                print("Failed to send to websocket: %s" % e)
                ws = websocket_connect()
                ws.send(str(throttle))


except Exception as e:
    print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
    traceback.print_exc()
    try:
        client.close()
    except:
        pass
    sys.exit(1)
