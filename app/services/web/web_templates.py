# web_templates.py
def page(title, inner_html, css_text=""):
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{}</title>
  <link rel="icon" href="data:,">
  <style>{}</style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <header>
        <h1>{}</h1>
        <p>Select a network and enter the password to connect.</p>
      </header>
      {}
      <footer>Fermento • Captive Portal</footer>
    </div>
  </div>
</body>
</html>""".format(
        title, css_text, title, inner_html
    )


def wifi_form(network_rows_html):
    return """<form action="/configure" method="post" accept-charset="utf-8">
  <div class="list">
    {}
  </div>
  <p style="margin:10px 0 6px 0">Password</p>
  <input class="field" type="password" id="password" name="password" placeholder="Enter WiFi password">
  <button class="btn" type="submit">Connect</button>
</form>""".format(
        network_rows_html
    )


def network_row(ssid, safe_id, checked=False):
    return """<div class="net">
  <input type="radio" name="ssid" value="{ssid}" id="ssid_{id}" {checked}>
  <label for="ssid_{id}">{ssid}</label>
</div>""".format(
        ssid=ssid,
        id=safe_id,
        checked="checked" if checked else "",
    )


def message_box(html, ok=True):
    cls = "msg ok" if ok else "msg err"
    return '<div class="{}">{}</div>'.format(cls, html)
