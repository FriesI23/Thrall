# Thrall
> amap/qqmap/admap python api

## Usage AMAP

```python
from thrall.amap import session

r = session.riding('116.434307,39.90909', destination=(116.434446,39.90816))
r.data
```

### Use for your own amap-key:

```python
from thrall.amap.session import AMapSession

session = AMapSession(default_key=your_key)
r = session.riding('116.434307,39.90909', destination=(116.434446,39.90816))
```

## AMAP Interface

- `batch *`
- `geo_code`
- `regeo_code`
- `search_text`
- `search_around`
- `suggest`
- `distance`
- `riding`

# AMAP Batch interface support

- `geo_code`
- `regeo_code`
- `search_text`
- `search_around`
- `suggest`
- `distance`

