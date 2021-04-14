from mitmproxy.net.http import Response, Headers
from mitmproxy.options import Options
from mitmproxy.proxy.config import ProxyConfig
from mitmproxy.proxy.server import ProxyServer
from mitmproxy.tools.dump import DumpMaster
import requests
import threading
import asyncio
import base64
import gzip
import brotli
from datetime import datetime
import functions as func



class Interception:
    def __init__(self):
        self.last_response = None

    def request(self, flow):
        try:
                url = flow.request.url
                print(url)
                json_response = func.get_response(url)

                try:
                        text = json_response["content"]["text"]
                        try:
                                if json_response["content"]["encoding"] == "base64":
                                        byt = base64.b64decode(text)
                        except KeyError:
                                byt = str.encode(text)
                                for obj in json_response["headers"]:
                                        if obj["name"].lower() == "content-encoding" and obj["value"] == "gzip":
                                                print("gzip")
                                                byt = gzip.compress(byt)
                                        elif obj["name"].lower() == "content-encoding" and obj["value"] == "br":
                                                print("br")
                                                byt = brotli.compress(byt)
                except KeyError:
                        byt = b''

                list_headers = []
                for obj in json_response["headers"]:
                        if obj["name"].lower() == "content-length":
                                list_headers.append((str.encode(obj["name"]), str.encode(str(len(byt)))))
                        else:
                                list_headers.append((str.encode(obj["name"]), str.encode(obj["value"])))
                headers = Headers(list_headers)

                response = Response(
                    http_version = str.encode(json_response["httpVersion"]),
                    status_code = json_response["status"],
                    reason = str.encode(json_response["statusText"]),
                    headers = headers,
                    content = byt,
                    trailers = None,
                    timestamp_start = 0.,
                    timestamp_end = 1.
                )
                print(response)
        except KeyError:
                print("KeyError")
                headers = Headers([
                        (b'Content-Type', b'text/plain; charset=utf-8'),
                ])
                response = Response(
                    http_version = str.encode("http/2.0"),
                    status_code = 200,
                    reason = str.encode("Success"),
                    headers = headers,
                    content = str.encode("KeyError\n"),
                    trailers = None,
                    timestamp_start = 0.,
                    timestamp_end = 1.
                )
        flow.response = response

    def response(self, flow):
        """
        print(flow.response)
        print(flow.response.http_version)
        print(flow.response.status_code)
        print(flow.response.reason)
        print(flow.response.headers)
        print(flow.response.content)
        print(flow.response.trailers)
        print(flow.response.timestamp_start)
        print(flow.response.timestamp_end)
        """

        self.last_response = flow.response


def loop_in_thread(loop, m):
    asyncio.set_event_loop(loop)
    m.run_loop(loop.run_forever)


intercept = Interception()


options = Options(listen_host='0.0.0.0', listen_port=8080, http2=True)
m = DumpMaster(options, with_termlog=True, with_dumper=True)
m.addons.add(intercept)
config = ProxyConfig(options)
m.server = ProxyServer(config)
loop = asyncio.get_event_loop()
t = threading.Thread(target=loop_in_thread, args=(loop, m))
t.start()


