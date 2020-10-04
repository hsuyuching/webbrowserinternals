# webbrowserinternals
## How to run:
Run `python3 connect.py <url>`

## Test with own html file
Run `python3 -m http.server` under the folder that contains test.html. Then visits the localhost:8080, or other port.

## File structure
### connect.py
Connect to URL, handle the request and respone. Support the redirect URL.

### parse.py
Parse the response.body from connect.py and construct html tree

### layout.py
Call from browser.py to fill in the self.display_list[]. Recursively handle the open/close/implicit tag

### browser.py
Collect the self.display_list in layout(), then do the render() and flush(). Handle the keyboard binding, such as "scroll_up", "scroll_down".