import board
import digitalio
import analogio
import time
import json
import wifi
import socketpool

WIFI_SSID = "McDonalds"
WIFI_PASSWORD = "12345678"
SERVER = "10.250.112.17"
PORT = 5000
ENDPOINT = "/temperature"

led_builtin = digitalio.DigitalInOut(board.LED)
led_builtin.direction = digitalio.Direction.OUTPUT

led_red = digitalio.DigitalInOut(board.GP15)
led_red.direction = digitalio.Direction.OUTPUT

temp_sensor = analogio.AnalogIn(board.GP26)

print("Connecting to WiFi...")
wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
print(f"Connected! IP: {wifi.radio.ipv4_address}")

pool = socketpool.SocketPool(wifi.radio)

def send_temp(temp):
    try:
        sock = pool.socket()
        sock.settimeout(5)
        sock.connect((SERVER, PORT))
        
        data = json.dumps({"temperature": temp})
        request = (
            f"POST {ENDPOINT} HTTP/1.1\r\n"
            f"Host: {SERVER}:{PORT}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(data)}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
            f"{data}"
        )
        
        sock.send(request.encode())
        time.sleep(0.1)
        
        response = b""
        buffer = bytearray(1024)
        while True:
            try:
                num = sock.recv_into(buffer)
                if num == 0:
                    break
                response += bytes(buffer[:num])
            except:
                break
        
        sock.close()
        
        text = response.decode()
        
        if "{" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

print("Starting...")
led_builtin.value = False
led_red.value = False

while True:
    raw = temp_sensor.value
    voltage = (raw * 3.3) / 65535
    temp = round((voltage - 0.5) * 100, 2)
    print(f"Temp: {temp}C")
    
    result = send_temp(temp)
    if result:
        print(f"Server: {result}")
        led_red.value = result.get("warning", False)
        if led_red.value:
            print("WARNING!")
    
    led_builtin.value = True
    time.sleep(0.1)
    led_builtin.value = False
    time.sleep(5)