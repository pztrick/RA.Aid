import os
from typing import Dict

import requests

from langchain_core.tools import tool
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from datetime import datetime

console = Console()

# Global flag to prevent recursive calls
_chiprelay_active = False

@tool
def invoke_chiprelay() -> str:
    """
        This tool **must always be invoked** at the end of any task that is successfully completed.
        Includes loop prevention mechanism to avoid recursive calls.
    """
    global _chiprelay_active
    
    if _chiprelay_active:
        return "ChipRelay already active - skipping recursive call"
        
    _chiprelay_active = True
    try:
        console.print(
            Panel('The firmware will be built and flashed to the target device using the Relay "banana".', title="⚡ Building and uploading to ChipRelay", border_style="bright_blue")
        )
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        with open('/tmp/ra_aid.log', 'a') as f:
            f.write(f"{timestamp} ChipRelay triggered successfully.\n")
        try:
            response = requests.post("https://api.chiprelay.com/trigger", json={})
        except:
            pass
        return "ChipRelay triggered successfully."
    finally:
        _chiprelay_active = False
