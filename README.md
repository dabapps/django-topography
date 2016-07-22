# topography

Introspects the URL structure of a Django application and produces a JSON-encoded description.

Installation: `pip install django-topography` then add `topography` to `INSTALLED_APPS`.
Usage: `manage.py topography`

Example output:

```json
{
  "timestamp": "2016-07-22T09:07:58.940316",
  "version": 0,
  "urls": [
    {
      "url": "/",
      "view": {
        "docs": "This view is responsible for the homepage of the website",
        "name": "index",
        "methods": [
          {
            "docs": "Render the homepage",
            "lines": 2,
            "name": "GET"
          }
        ]
      }
    },
    ...
```
