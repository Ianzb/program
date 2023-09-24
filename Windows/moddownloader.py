import requests, json

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.36"}
response = requests.get("https://api.modrinth.com/v2", headers=header, stream=True)
print("Modrinth服务器连接成功")


# str转json
def load(data: str):
    return json.loads(data)


# 拼接链接，需要头链接+字典形式参数
def join_url(first: str, end: dict):
    if first[-1] == "?":
        first = first[:-1]
    list = []
    for k, v in end.items():
        if v:
            list.append(k + "=" + str(v))
    string = "&".join(list)
    string = first + "?" + string
    if string[-1] == "?":
        string = string[:-1]
    string = string.replace("'", '"')
    return string


# 搜索文件
def search(data=None, project_type="mod"):
    facets = [["project_type:" + project_type]]
    while None in facets:
        facets.remove(None)
    response = requests.get(join_url("https://api.modrinth.com/v2/search", {"query": data, "facets": facets, "limit": 100}), headers=header, stream=True)
    response = load(response.text)
    return response


# 处理搜索结果
def search_inf(data):
    dict1 = {"当前页面展示数量": str(len(data["hits"])), "总结果数量": str(data["total_hits"])}
    return dict1


# 处理搜索的模组结果
def search_mod_inf(data):
    string = data["hits"]
    list = []
    for i in string:
        dict1 = {"名称": i["title"], "作者": i["author"], "类型：": i["project_type"], "链接": i["slug"], "介绍": i["description"], "标签": i["categories"], "适配版本": i["versions"], "下载次数": str(i["downloads"])}
        list.append(dict1)
    return list


str1 = search("", "mod")
print(search_inf(str1))
print(search_mod_inf(str1)[0])
input()
