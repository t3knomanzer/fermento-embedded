# Author: Igor Ferreira
# License: MIT
# Version: 2.1.0
# Description: WiFi Manager for ESP8266 and ESP32 using MicroPython.

import machine
import network
import socket
import re
import time


class WifiManager:

    def __init__(
        self, ssid="WifiManager", password="wifimanager", reboot=True, debug=False
    ):
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_sta.active(True)
        self.wlan_ap = network.WLAN(network.AP_IF)

        # Avoids simple mistakes with wifi ssid and password lengths, but doesn't check for forbidden or unsupported characters.
        if len(ssid) > 32:
            raise Exception("The SSID cannot be longer than 32 characters.")
        else:
            self.ap_ssid = ssid
        if len(password) < 8:
            raise Exception("The password cannot be less than 8 characters long.")
        else:
            self.ap_password = password

        # Set the access point authentication mode to WPA2-PSK.
        self.ap_authmode = 3

        # The file were the credentials will be stored.
        # There is no encryption, it's just a plain text archive. Be aware of this security problem!
        self.wifi_credentials = "wifi.dat"

        # Prevents the device from automatically trying to connect to the last saved network without first going through the steps defined in the code.
        self.wlan_sta.disconnect()

        # Change to True if you want the device to reboot after configuration.
        # Useful if you're having problems with web server applications after WiFi configuration.
        self.reboot = reboot

        self.debug = debug

    def connect(self):
        if self.wlan_sta.isconnected():
            return
        profiles = self.read_credentials()
        for ssid, *_ in self.wlan_sta.scan():
            ssid = ssid.decode("utf-8")
            if ssid in profiles:
                password = profiles[ssid]
                if self.wifi_connect(ssid, password):
                    return True
        return False

    def disconnect(self):
        if self.wlan_sta.isconnected():
            self.wlan_sta.disconnect()

    def is_connected(self):
        return self.wlan_sta.isconnected()

    def get_address(self):
        return self.wlan_sta.ifconfig()

    def write_credentials(self, profiles):
        lines = []
        for ssid, password in profiles.items():
            lines.append("{0};{1}\n".format(ssid, password))
        with open(self.wifi_credentials, "w") as file:
            file.write("".join(lines))

    def read_credentials(self):
        lines = []
        try:
            with open(self.wifi_credentials) as file:
                lines = file.readlines()
        except Exception as error:
            if self.debug:
                print(error)
            pass
        profiles = {}
        for line in lines:
            ssid, password = line.strip().split(";")
            profiles[ssid] = password
        return profiles

    def wifi_connect(self, ssid, password):
        print("Trying to connect to:", ssid)
        self.wlan_sta.connect(ssid, password)
        for _ in range(100):
            if self.wlan_sta.isconnected():
                print("\nConnected! Network information:", self.wlan_sta.ifconfig())
                return True
            else:
                print(".", end="")
                time.sleep_ms(100)
        print("\nConnection failed!")
        self.wlan_sta.disconnect()
        return False

    def web_server(self):
        self.wlan_ap.active(True)
        self.wlan_ap.config(
            essid=self.ap_ssid, password=self.ap_password, authmode=self.ap_authmode
        )
        server_socket = socket.socket()
        server_socket.close()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", 80))
        server_socket.listen(1)
        print(
            "Connect to",
            self.ap_ssid,
            "with the password",
            self.ap_password,
            "and access the captive portal at",
            self.wlan_ap.ifconfig()[0],
        )
        while True:
            if self.wlan_sta.isconnected():
                self.wlan_ap.active(False)
                if self.reboot:
                    print("Resetting device...")
                    machine.reset()
            self.client, addr = server_socket.accept()
            try:
                self.client.settimeout(5.0)
                self.request = b""
                try:
                    while True:
                        if "\r\n\r\n" in self.request:
                            # Fix for Safari browser
                            self.request += self.client.recv(512)
                            break
                        self.request += self.client.recv(128)
                except Exception as error:
                    # It's normal to receive timeout errors in this stage, we can safely ignore them.
                    if self.debug:
                        print(error)
                    pass
                if self.request:
                    if self.debug:
                        print(self.url_decode(self.request))
                    url = (
                        re.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", self.request)
                        .group(1)
                        .decode("utf-8")
                        .rstrip("/")
                    )
                    if url == "":
                        self.handle_root()
                    elif url == "configure":
                        self.handle_configure()
                    else:
                        self.handle_not_found()
            except Exception as error:
                if self.debug:
                    print(error)
                return
            finally:
                self.client.close()

    def send_header(self, status_code=200):
        self.client.send("""HTTP/1.1 {0} OK\r\n""".format(status_code))
        self.client.send("""Content-Type: text/html\r\n""")
        self.client.send("""Connection: close\r\n""")

    def send_response(self, payload, status_code=200):
        self.send_header(status_code)
        # Serve WiFi setup page (dark theme, Bootstrap)
        self.client.sendall(
            """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>WiFi Setup</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <!-- Bootstrap 5 -->
            <link
            href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
            rel="stylesheet">

            <style>
                body {
                    min-height: 100vh;
                    background: #0e1117;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-family: system-ui, -apple-system, BlinkMacSystemFont,
                                "Segoe UI", Roboto, sans-serif;
                    color: #e6e6e6;
                }

                .card {
                    max-width: 420px;
                    width: 100%;
                    background: #161b22;
                    border-radius: 16px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.6);
                    border: 1px solid #222;
                }

                .logo {
                    width: 72px;
                    height: 72px;
                    background: #21262d;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 600;
                    color: #9da7b1;
                    margin: 0 auto 1rem;
                    font-size: 14px;
                    letter-spacing: 0.05em;
                }

                h4 {
                    color: #c9d1d9;
                    font-weight: 500;
                    letter-spacing: 0.02em;
                }

                .form-check-label {
                    color: #e6e6e6;
                }

                .form-check-input {
                    background-color: #0e1117;
                    border: 1px solid #30363d;
                }

                .form-check-input:checked {
                    background-color: #2ea043;
                    border-color: #2ea043;
                }

                .form-check-input:focus {
                    box-shadow: 0 0 0 0.15rem rgba(46, 160, 67, 0.4);
                    border-color: #2ea043;
                }

                .form-control {
                    background-color: #0e1117;
                    color: #e6e6e6;
                    border: 1px solid #30363d;
                }

                .form-control::placeholder {
                    color: #8b949e;
                }

                .form-control:focus {
                    background-color: #0e1117;
                    color: #fff;
                    border-color: #58a6ff;
                    box-shadow: none;
                }

                .btn-primary {
                    background-color: #238636;
                    border-color: #238636;
                }

                .btn-primary:hover {
                    background-color: #2ea043;
                    border-color: #2ea043;
                }
            </style>
        </head>

        <body>
        <div class="card p-4">
            <div class="logo">LOGO</div>

            <h4 class="text-center mb-3">Connect to Wi-Fi</h4>

            <form action="/configure" method="post" accept-charset="utf-8">
                <div class="mb-3">
        """
        )

        # SSID list (Bootstrap radios)
        for ssid, *_ in self.wlan_sta.scan():
            ssid = ssid.decode("utf-8")

            # NOTE: If SSIDs can contain quotes or weird chars, consider sanitizing.
            self.client.sendall(
                f"""
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="ssid" value="{ssid}" id="{ssid}" required>
                        <label class="form-check-label" for="{ssid}">
                            {ssid}
                        </label>
                    </div>
            """
            )

        # Password + submit + close HTML
        self.client.sendall(
            """
                </div>

                <div class="mb-3">
                    <input
                        type="password"
                        class="form-control"
                        id="password"
                        name="password"
                        placeholder="Wi-Fi password"
                        required>
                </div>

                <button type="submit" class="btn btn-primary w-100">
                    Connect
                </button>
            </form>
        </div>
        </body>
        </html>
        """
        )

        self.client.close()

    def handle_configure(self):
        match = re.search("ssid=([^&]*)&password=(.*)", self.url_decode(self.request))
        if match:
            ssid = match.group(1).decode("utf-8")
            password = match.group(2).decode("utf-8")
            if len(ssid) == 0:
                self.send_response(
                    """
                    <p>SSID must be providaded!</p>
                    <p>Go back and try again!</p>
                """,
                    400,
                )
            elif self.wifi_connect(ssid, password):
                self.send_response(
                    """
                    <p>Successfully connected to</p>
                    <h1>{0}</h1>
                    <p>IP address: {1}</p>
                """.format(
                        ssid, self.wlan_sta.ifconfig()[0]
                    )
                )
                profiles = self.read_credentials()
                profiles[ssid] = password
                self.write_credentials(profiles)
                time.sleep(5)
            else:
                self.send_response(
                    """
                    <p>Could not connect to</p>
                    <h1>{0}</h1>
                    <p>Go back and try again!</p>
                """.format(
                        ssid
                    )
                )
                time.sleep(5)
        else:
            self.send_response(
                """
                <p>Parameters not found!</p>
            """,
                400,
            )
            time.sleep(5)

    def handle_not_found(self):
        self.send_response(
            """
            <p>Page not found!</p>
        """,
            404,
        )

    def url_decode(self, url_string):

        # Source: https://forum.micropython.org/viewtopic.php?t=3076
        # unquote('abc%20def') -> b'abc def'
        # Note: strings are encoded as UTF-8. This is only an issue if it contains
        # unescaped non-ASCII characters, which URIs should not.

        if not url_string:
            return b""

        if isinstance(url_string, str):
            url_string = url_string.encode("utf-8")

        bits = url_string.split(b"%")

        if len(bits) == 1:
            return url_string

        res = [bits[0]]
        appnd = res.append
        hextobyte_cache = {}

        for item in bits[1:]:
            try:
                code = item[:2]
                char = hextobyte_cache.get(code)
                if char is None:
                    char = hextobyte_cache[code] = bytes([int(code, 16)])
                appnd(char)
                appnd(item[2:])
            except Exception as error:
                if self.debug:
                    print(error)
                appnd(b"%")
                appnd(item)

        return b"".join(res)
