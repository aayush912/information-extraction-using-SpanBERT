from googleapiclient.discovery import build

def google_search(query, googlekey, enginekey):

    # Build a service object for interacting with the API.
    search = build("customsearch", "v1", developerKey=googlekey)

    # Retrieve results
    results = search.cse().list(q=query, cx=enginekey,).execute()

    items = results['items']
    item_summary = [{'id': idx, 'url': item['link'], 'title': item['title'], 'summary': item['snippet']} for idx, item in enumerate(items)]

    return item_summary