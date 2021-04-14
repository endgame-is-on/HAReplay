import json
import base64
import glob


har_files = glob.glob("har/*")
har_files.sort()

dict_url_response = {}

for har_path in har_files:
        fob = open(har_path, "r")
        data = json.load(fob)
        fob.close()

        entries = data["log"]["entries"]
        for entry in entries:
            url = entry["request"]["url"]
            response = entry["response"]
            dict_url_response[url] = response


def get_response(url):
    return dict_url_response[url]


