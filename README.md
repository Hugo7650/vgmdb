# vgmdb
Python-based API for fetching music and soundtrack data from VGMDB.

## Installation
clone the repository and run
```
pip install vgmdb
```

## Usage
```python
from vgmdb import VGMdb

# Search
results = VGMdb.search('Final Fantasy')

# Search albums
albums = VGMdb.search_albums('Final Fantasy')

# Get album by ID
album = VGMdb.get_album(1)

# Set cookies (with login, there is more covers available)
VGMdb.set_cookies({'key': 'value'})

# Set proxies
VGMdb.set_proxies('https://host:port')
VGMdb.set_proxies('socks5://user:pass@host:port')  # requires PySocks or requests[socks]
```