import free_proxies_crawl
import better_proxies_crawl
import json

if __name__ == '__main__':
    lst1 = free_proxies_crawl.free_proxy_list_crawl()
    print("done free_proxies_list domain")
    lst2 = free_proxies_crawl.getproxylist_crawl()
    print("done get_proxies_list domain")
    for i in lst2:
        lst1.append(i)
    # print(lst1)
    with open("news_collection/proxies/free_proxies.json", "w") as outfile:
        json.dump(lst1, outfile)

    # similar func for better_proxies_crawl
    lst3 = better_proxies_crawl.hidemy_name_crawl()
    print("done hidemy_name domain")
    # lst4=better_proxies_crawl.free_proxy_cz_crawl()
    # print("done free_proxy_cz domain")
    # for i in lst4:
    #     lst3.append(i)
    print(lst3)
    with open("news_collection/proxies/better_proxies.json", "w") as outfile:
        json.dump(lst3, outfile)
