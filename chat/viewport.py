from .bubble import Bubble

import pywebio
from typing import Any

class Viewport:
    def __init__(self, config:dict[str,Any]):
        style = config.get("style",{})
        pywebio.config(
            title = style.get("title", None),
            theme = style.get("theme", "yeti"),
            css_style = style.get("css", None),
            js_code = style.get("js", None),
        )
        
        pywebio.output.put_markdown("")

        logo = style.get("logo", None)
        if logo:
            try:
                with open(logo, "rb") as f:
                    binary = f.read()
                pywebio.output.style(
                    pywebio.output.put_image(binary),
                    "opacity:1;animation-name:none;animation-duration:0s;width:100%;"
                    )
            except:
                print(f"cannot load logo file: {logo}")

        self.user = Bubble(color=style.get("user","#aaeeaa"),position="left")
        self.agent = Bubble(color=style.get("agent","#cccccc"),position="right")

        #
        #html = "<div class='webio-tabs' style>"
        #for url in self._activeHandlers:
        #    name = self._activeHandlers[url].name
        #    checked = name == active.name
        #    html += f"""
        #    <input type="radio" class="toggle" value="{name}" id="menu_{name}" name="menu_{name}" onclick="location.href='{url}';" {"checked" if checked else ""}>
        #    <label for="menu_{name}">{name}</label>
        #    """
        #html += "</div>"

        #pywebio.output.put_html(html)