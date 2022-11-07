import requests

def count_words(url):
    response = requests.get(url).text
    return len(response.split())

# print(count_words('https://www.cricbuzz.com'))