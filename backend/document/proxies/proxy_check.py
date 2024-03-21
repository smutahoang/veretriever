from proxy_checker import ProxyChecker
import time
import json 

with open("news_collection/proxies/free_proxies.json", "r") as read_file:
    data = json.load(read_file)
checker = ProxyChecker()
res=[]
time_now=time.perf_counter()
for i in data:   
    ip=i['IP Address']
    port=i['Port']
    print('checking {0}:{1}'.format(ip,port))

    check=checker.check_proxy('{0}:{1}'.format(ip,port))
    if check:
        res.append(check)
    print("time elapsed: ",time.perf_counter()-time_now)
    time_now=time.perf_counter()
with open("news_collection/proxies/checked_proxies.json", "w") as outfile:
        json.dump(res, outfile)

