import requests


def abstract(term):
    term = "+".join(term.split(" "))
    url = f"https://api.duckduckgo.com/?q={term}&format=json&" + \
        "no_redirect=1&t=twitch_chatbot"
    r = requests.get(url).json()
    abstract = r['Abstract'][:300] + "[...]"
    credit = f"Results by duckduckgo.com/?q={term}"
    source = r['AbstractURL']

    if abstract == "[...]":
        return "No abstract found"
    else:
        return f'"{abstract}" ; {credit} ; Source: {source}'


if __name__ == "__main__":
    term = input("What is your search term? ")
    print(abstract(term))
