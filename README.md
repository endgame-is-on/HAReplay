1. start proxy server
```
python3 start_mitm_proxy.py
```
2. open browser
```
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --proxy-server=127.0.0.1:8080
```
3. open http://www.boa.org/news.html


If you have captured HAR for other web sites, put it into the folder `har/` and restart the proxy server.
