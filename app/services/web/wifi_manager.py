# wifi_manager.py
# Author: Igor Ferreira
# License: MIT
# Version: 2.1.0 (UI refactor: inline CSS from file)
# Description: WiFi Manager for ESP8266 and ESP32 using MicroPython.

import machine
import network
import socket
import re
import time

from app.services.web.web_templates import page, wifi_form, network_row, message_box


class WifiManager:
    def __init__(
        self, ssid="WifiManager", password="wifimanager", reboot=True, debug=True
    ):
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_sta.active(True)
        self.wlan_ap = network.WLAN(network.AP_IF)

        if len(ssid) > 32:
            raise Exception("The SSID cannot be longer than 32 characters.")
        self.ap_ssid = ssid

        if len(password) < 8:
            raise Exception("The password cannot be less than 8 characters long.")
        self.ap_password = password

        # WPA2-PSK
        self.ap_authmode = 3

        # Credentials file (plaintext)
        self.wifi_credentials = "wifi.dat"

        # Prevent auto-connect to last network unless you do it explicitly
        self.wlan_sta.disconnect()

        self.reboot = reboot
        self.debug = debug

        # Pre-compiled regex for routing
        self._route_re = re.compile(b"(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP")

        # Web assets location + inline CSS cache
        self.web_root = "app/services/web"
        self.css_text = ""
        try:
            with open(self.web_root + "/style.css", "r") as f:
                self.css_text = f.read()
        except Exception as e:
            if self.debug:
                print("Could not load style.css:", e)

    # -------------------------
    # WiFi helpers
    # -------------------------
    def connect(self):
        if self.wlan_sta.isconnected():
            return True
        profiles = self.read_credentials()
        for ssid, *_ in self.wlan_sta.scan():
            ssid = ssid.decode("utf-8")
            if ssid in profiles:
                if self.wifi_connect(ssid, profiles[ssid]):
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
        try:
            with open(self.wifi_credentials) as file:
                lines = file.readlines()
        except Exception as error:
            if self.debug:
                print(error)
            lines = []

        profiles = {}
        for line in lines:
            try:
                ssid, password = line.strip().split(";")
                profiles[ssid] = password
            except Exception as error:
                if self.debug:
                    print("Bad credentials line:", line, error)
        return profiles

    def wifi_connect(self, ssid, password):
        print("Trying to connect to:", ssid)
        self.wlan_sta.connect(ssid, password)
        for _ in range(100):
            if self.wlan_sta.isconnected():
                print("\nConnected! Network information:", self.wlan_sta.ifconfig())
                return True
            print(".", end="")
            time.sleep_ms(100)
        print("\nConnection failed!")
        self.wlan_sta.disconnect()
        return False

    # -------------------------
    # HTTP helpers
    # -------------------------
    def send_header(self, status_code=200, content_type="text/html"):
        reasons = {
            200: "OK",
            400: "Bad Request",
            404: "Not Found",
            500: "Internal Server Error",
        }
        reason = reasons.get(status_code, "OK")

        self.client.send("HTTP/1.1 {} {}\r\n".format(status_code, reason))
        self.client.send("Content-Type: {}\r\n".format(content_type))
        self.client.send("Connection: close\r\n\r\n")

    def send_text(self, text, status_code=200, content_type="text/html"):
        self.send_header(status_code, content_type)
        if isinstance(text, str):
            text = text.encode("utf-8")
        self.client.sendall(text)

    def send_response(self, inner_html, status_code=200):
        html = page("WiFi Manager", inner_html, self.css_text)
        self.send_text(html, status_code, "text/html")

    # -------------------------
    # Route handlers
    # -------------------------
    def handle_root(self):
        rows = []
        first = True

        try:
            scanned = self.wlan_sta.scan()
        except Exception as error:
            if self.debug:
                print("scan() failed:", error)
            scanned = []

        for ssid, *_ in scanned:
            try:
                ssid = ssid.decode("utf-8")
            except Exception:
                continue

            safe_id = str(abs(hash(ssid)) % 100000)
            rows.append(network_row(ssid, safe_id, checked=first))
            first = False

        if not rows:
            rows_html = network_row("No networks found (refresh)", "0", checked=True)
        else:
            rows_html = "\n".join(rows)

        content = wifi_form(rows_html)
        self.send_response(content)

    def handle_configure(self):
        match = re.search(b"ssid=([^&]*)&password=(.*)", self.url_decode(self.request))
        if match:
            ssid = match.group(1).decode("utf-8")
            password = match.group(2).decode("utf-8")

            if len(ssid) == 0:
                self.send_response(
                    message_box(
                        "<p>SSID must be provided.</p><p>Go back and try again.</p>",
                        ok=False,
                    ),
                    400,
                )
            elif self.wifi_connect(ssid, password):
                html = "<p>Successfully connected to</p><h1>{}</h1><p>IP address: <b>{}</b></p>".format(
                    ssid, self.wlan_sta.ifconfig()[0]
                )
                self.send_response(message_box(html, ok=True))

                profiles = self.read_credentials()
                profiles[ssid] = password
                self.write_credentials(profiles)
                time.sleep(5)
            else:
                html = "<p>Could not connect to</p><h1>{}</h1><p>Go back and try again.</p>".format(
                    ssid
                )
                self.send_response(message_box(html, ok=False))
                time.sleep(5)
        else:
            self.send_response(
                message_box("<p>Parameters not found!</p>", ok=False), 400
            )
            time.sleep(5)

    def handle_not_found(self):
        self.send_response(message_box("<p>Page not found!</p>", ok=False), 404)

    # -------------------------
    # Web server
    # -------------------------
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
                        if b"\r\n\r\n" in self.request:
                            # Fix for Safari browser
                            self.request += self.client.recv(512)
                            break
                        self.request += self.client.recv(128)
                except Exception as error:
                    if self.debug:
                        print(error)

                if self.request:
                    if self.debug:
                        print(self.url_decode(self.request))

                    m = self._route_re.search(self.request)
                    if not m:
                        self.handle_not_found()
                        continue

                    url = m.group(1).decode("utf-8").rstrip("/")

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
                try:
                    self.client.close()
                except Exception:
                    pass

    # -------------------------
    # URL decoding
    # -------------------------
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
