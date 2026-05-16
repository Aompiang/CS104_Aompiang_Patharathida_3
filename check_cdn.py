import urllib.request

urls = [
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js'
]
for url in urls:
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            print(url, r.status, r.getheader('Content-Type'))
    except Exception as e:
        print(url, 'ERROR', type(e).__name__, e)
