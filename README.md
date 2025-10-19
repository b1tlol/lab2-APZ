# Financial Manager — Multilayer Architecture

**Layers**: UI (console) → BLL (services) → DAL (repositories + Unit of Work, SQLAlchemy)
**Mapping**: explicit functions map ORM ↔ domain entities (dataclasses)

## Requirements
python3.11 or venv

## Quick start
```
pip install -r requirements.txt
python -m app.ui.console
```

The first run creates `fin.db` (SQLite) and seeds a few demo accounts/categories

## Structure
- `app/domain`: pure domain entities (dataclasses) & enums
- `app/dal`: SQLAlchemy models, generic repository, Unit of Work, mappers
- `app/bll`: services (use cases)
- `app/ui`: console UI only; you can add another UI later without touching BLL/DAL
- `app/common`: shared DTOs and mapping helpers

## Notes
- Repository + Unit of Work are isolated behind interfaces-like base classes
- Mapping ensures UI/BLL work with **domain** entities (no DAL types leak)
- You can switch the DAL (e.g., file or NoSQL) by implementing the same repos/UoW API
