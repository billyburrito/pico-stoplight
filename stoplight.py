import _thread
import network
import socket
from time import sleep
from picozero import LED
import machine
import re

ssid = 'ssid'
password = 'password'

# init led states
state = {}
state['green'] = 'off'
state['yellow'] = 'off'
state['red'] = 'off'
led = {}
led['red'] = LED(5)
led['yellow'] = LED(9)
led['green'] = LED(13)
colors = ['red', 'yellow', 'green', 'all']
cmds=['on', 'off', 'blink', 'pulse']

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage(state):
    #Template HTML
    html = "<!DOCTYPE html><html><table>"

    for col in colors:
        html += "<tr bgcolor=\""+col+"\">\n"
        for each in cmds:
            html += "<td><form action=\"./"+col+"_"+each+"\"><input type=\"submit\" value=\""+col+" "+each+"\" /></form></td>\n"
        html += "</tr>\n"

    html += f"""            
            <tr><td colspan="4">
            <p>Red is {state['red']}</p>
            <p>Yellow is {state['yellow']}</p>
            <p>Green is {state['green']}</p>
            </td></tr>
            </table>
            </body>
            </html>
            """
    return str(html)

def ledControl(color, cmd):
    if color == 'all':
        for keys in led:
            func = getattr(led[keys], cmd)
            func()
            state[keys] = cmd
    else:
        func = getattr(led[color], cmd)
        func()
        state[color] = cmd

def serve(connection):
    #Start a web server
    
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        print(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        
        # lets re the req
        cmd = re.match("^/(.*)_(.*)\?$", request)
        if cmd:
            ledControl(cmd.group(1), cmd.group(2))

        html = webpage(state)
        client.send(html)
        client.close()
        
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
