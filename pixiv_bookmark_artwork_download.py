import requests
import json
import os

def get_filtered_ids(user_id, cookie, user_agent, proxy, start_page, end_page):
    headers = {
        'User-Agent': user_agent,
        'Cookie': cookie
    }
    
    proxies = {
        'http': proxy,
        'https': proxy
    }
    
    filtered_ids = []
    # bookmark offset
    offset = 48 * (start_page - 1)
    
    for _ in range(end_page - start_page + 1):
        url = f"https://www.pixiv.net/ajax/user/{user_id}/illusts/bookmarks?offset={offset}&tag=&limit=48&rest=show"
        response = requests.get(url, headers=headers, proxies=proxies)
        
        if response.status_code == 200:
            data = response.json()
            works = data.get('body', {}).get('works', [])
            
            filtered_ids.extend([work['id'] for work in works if work.get('xRestrict') != 0 and work.get('aiType') == 0])
            # xRestrict == 1 == R18, xRestrict == 2 == R18G, aiType == 0 == not ai artwork, aiType == 2 == ai artwork
            offset += 48
        else:
            print(f"Failed to fetch data at offset {offset}. Status code: {response.status_code}")
            break
    
    return filtered_ids

def download_images(filtered_ids, cookie, user_agent, proxy):
    headers = {
        'User-Agent': user_agent,
        'Cookie': cookie
    }
    
    proxies = {
        'http': proxy,
        'https': proxy
    }
    
    for illust_id in filtered_ids:
        url = f"https://www.pixiv.net/ajax/illust/{illust_id}/pages"
        response = requests.get(url, headers=headers, proxies=proxies)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('body', [])
            
            for page in pages:
                original_url = page.get('urls', {}).get('original')
                if original_url:
                    download_file(original_url, proxies)
        else:
            print(f"Failed to fetch images for illust ID {illust_id}. Status code: {response.status_code}")

def download_file(url, proxies):
    downloaders = {
        'User-Agent': user_agent,
        'Referer': 'https://www.pixiv.net/'
    }
    response = requests.get(url, headers=downloaders, proxies=proxies, stream=True)
    
    if response.status_code == 200:
        filename = url.split('/')[-1]
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download file from {url}. Status code: {response.status_code}")

# replace to your id, cookie, UA and proxy
user_id = 'xxx'
cookie = 'xxx'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
proxy = 'http://xxx:xxx'
start_page = 1
# bookmark start page
end_page = 1
# bookmark end page

filtered_ids = get_filtered_ids(user_id, cookie, user_agent, proxy, start_page, end_page)
download_images(filtered_ids, cookie, user_agent, proxy)
print("Download done.")
