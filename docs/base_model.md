# SDKBaseModel

Auto-cleaning Pydantic model for scraped data.

```python
from cmdop import SDKBaseModel

class Product(SDKBaseModel):
    __base_url__ = "https://shop.com"
    name: str = ""    # "  iPhone 15  \n" → "iPhone 15"
    price: int = 0    # "$1,299.00" → 1299
    rating: float = 0 # "4.5 stars" → 4.5
    url: str = ""     # "/p/123" → "https://shop.com/p/123"

products = Product.from_list(raw["items"])  # Auto dedupe + filter
```
