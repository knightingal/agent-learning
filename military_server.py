import datetime
import json
import base64
# from PIL import Image
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from pic_read import init_llm, military_read

# from paddleocr import PaddleOCR, draw_ocr

def print_hello():
  print("Hello")


class MilitaryHTTPRequestHandler(SimpleHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.send_header("content-length", str(len("MilitaryHTTPRequestHandler")))
    self.end_headers()

    self.wfile.write(bytes("MilitaryHTTPRequestHandler", "UTF-8"))

  def do_POST(self):
    content_length = int(self.headers.get("content-length"))
    body = self.rfile.read(content_length)

    image_base64 = base64.b64encode(body).decode("utf-8")
    response_json = military_read(image_base64=image_base64)

    print(response_json)
    resp_bytes = bytes(response_json, "UTF-8")

    self.send_response(200)
    self.send_header("content-length", str(len(resp_bytes)))
    self.end_headers()
    self.wfile.write(resp_bytes)


def run(server_class=HTTPServer, handler_class=MilitaryHTTPRequestHandler):
  server_address=('', 8000)
  httpd = server_class(server_address, handler_class)
  httpd.serve_forever()


if __name__ == "__main__":
  init_llm()
  print_hello()
  run()