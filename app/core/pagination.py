# pagination.py
from functools import wraps
from fastapi import Query, Depends
from pydantic import BaseModel
from typing import Any, Tuple

class PaginationParams(BaseModel):
    limit: int
    offset: int

def pagination_params(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return PaginationParams(limit=limit, offset=offset)

def paginated(func):
    @wraps(func)
    async def wrapper(
        *args,
        pagination: PaginationParams = Depends(pagination_params),
        **kwargs
    ):
        # Call the original function
        result = await func(*args, **kwargs, pagination=pagination)
        print('pagination: ',pagination)
        if isinstance(result, tuple) and len(result) == 2:
            items, total = result
            
            # Ensure items are serializable
            if items and hasattr(items[0], 'dict'):
                items = [item.dict() for item in items]
            
            return {
                "items": items,
                "pagination": {
                    "total": total,
                    "limit": pagination.limit,
                    "offset": pagination.offset,
                },
            }
        else:
            return result
    
    return wrapper