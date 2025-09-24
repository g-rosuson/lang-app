lang-app/
├── main.py                    # App initialization only
├── src/
│   ├── api/
│   │   ├── deps.py           # Dependencies (auth, services)
│   │   └── v1/
│   │       ├── api.py        # Main router aggregator
│   │       └── endpoints/    # Individual route files
│   │           ├── language.py
│   │           ├── health.py
│   │           └── auth.py
│   ├── models/               # Pydantic models
│   ├── services/             # Business logic
│   └── core/                 # Configuration