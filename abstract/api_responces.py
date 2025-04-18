from fastapi.responses import JSONResponse
from fastapi import Request
from typing import Any, Optional, List
from math import ceil


class Helper:
    def response(self, status_code: int, message: str, data: Any = None) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={
                "status": status_code,
                "message": message,
                "data": data
            }
        )

    def error_response(self, status_code: int, message: str, errors: Optional[List[str]] = None) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={
                "status": status_code,
                "message": message,
                "success": False,
                "errors": errors or []
            }
        )

    def success_response(self, status_code: int, message: str, data: Any = None) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={
                "status": status_code,
                "message": message,
                "data": data
            }
        )

    def list_response(
        self,
        request: Request,
        status_code: int,
        message: str,
        paginated_by: int,
        current_page: int,
        serializer_class,  # Assumes Pydantic model or callable
        qs,  # Query result list
        order_field: str = "id",
        filter_params: Optional[dict] = None
    ) -> JSONResponse:

        query_params = dict(request.query_params)
        page = int(query_params.get("page", current_page))
        limit = int(query_params.get("limit", paginated_by))

        # Filtering
        if filter_params:
            for query_key, db_field in filter_params.items():
                filter_value = query_params.get(query_key)
                if filter_value:
                    qs = [obj for obj in qs if str(getattr(obj, db_field)) == filter_value]

        # Ordering
        qs = sorted(qs, key=lambda x: getattr(x, order_field))

        # Pagination
        total_records = len(qs)
        total_pages = ceil(total_records / limit)
        start = (page - 1) * limit
        end = start + limit
        paginated_data = qs[start:end]

        # Serialize
        serialized = [serializer_class.from_orm(obj).dict() for obj in paginated_data]

        return JSONResponse(
            status_code=status_code,
            content={
                "status": status_code,
                "total_pages": total_pages,
                "current_page": page,
                "total_records": total_records,
                "message": message,
                "data": serialized
            }
        )
