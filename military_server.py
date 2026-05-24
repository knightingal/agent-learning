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

    # time = datetime.datetime.now()
    # now = time.strftime("%d-%m-%Y-%H:%M:%S")

    # pic_file = open(now + ".jpg", "wb+")
    # pic_file.write(body)
    # pic_file.close()

    # img = Image.open(now + ".jpg").convert("RGB")
    # img.save(now + "jp.jpg")


    # ocr = PaddleOCR(use_angle_cls=True, lang='ch')

    resp_obj = []

    # result = ocr.ocr(body, cls=True)
    # if result is not None:
    #   for idx in range(len(result)):
    #       res = result[idx]
    #       if res is not None:
    #         for line in res:
    #             print(line)
    #             resp_obj.append({"text":line[1][0], "trust_rate":line[1][1]})

    # resp_body = json.dumps(resp_obj, ensure_ascii=False)
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