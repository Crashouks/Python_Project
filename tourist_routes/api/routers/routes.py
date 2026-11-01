from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select

from tourist_routes.api.dependencies import DbSession, get_current_user
from tourist_routes.api.models import RouteRecord
from tourist_routes.api.schemas import RouteCreate, RouteRead, RouteType

router = APIRouter(prefix="/routes", tags=["routes"])

# Читання відкрите для всіх; створення, зміна й видалення — лише з дійсним JWT.
protected = [Depends(get_current_user)]


def to_read_schema(record: RouteRecord) -> RouteRead:
    result = RouteRead.model_validate(record)
    domain_route = record.to_domain()
    average = domain_route.average_rating()
    result.average_rating = round(average, 2) if average is not None else None
    result.estimated_duration_hours = round(domain_route.estimated_duration_hours(), 2)
    return result


def get_record_or_404(db, route_id: int) -> RouteRecord:
    record = db.get(RouteRecord, route_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Маршрут з ID {route_id} не знайдено.")
    return record


@router.get("", response_model=list[RouteRead])
def list_routes(
    db: DbSession,
    name: Annotated[Optional[str], Query(description="Пошук за частиною назви")] = None,
    country: Annotated[Optional[str], Query(description="Пошук за частиною назви країни")] = None,
    route_type: Annotated[Optional[RouteType], Query(alias="type")] = None,
    min_length_km: Annotated[Optional[float], Query(ge=0)] = None,
    max_length_km: Annotated[Optional[float], Query(ge=0)] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
):
    """Список маршрутів із фільтрацією: `/routes?name=карпат&type=HikingRoute&min_length_km=10`."""
    query = select(RouteRecord).order_by(RouteRecord.id)
    if route_type:
        query = query.where(RouteRecord.type == route_type)
    if min_length_km is not None:
        query = query.where(RouteRecord.length_km >= min_length_km)
    if max_length_km is not None:
        query = query.where(RouteRecord.length_km <= max_length_km)
    records = db.scalars(query).all()

    # Текстовий пошук робимо в Python: LIKE у SQLite не чутливий до регістру лише для латиниці.
    if name:
        records = [r for r in records if name.casefold() in r.name.casefold()]
    if country:
        records = [r for r in records if country.casefold() in r.country.casefold()]
    return [to_read_schema(r) for r in records[skip : skip + limit]]


@router.get("/{route_id}", response_model=RouteRead)
def get_route(route_id: int, db: DbSession):
    return to_read_schema(get_record_or_404(db, route_id))


@router.post("", response_model=RouteRead, status_code=status.HTTP_201_CREATED,
             dependencies=protected)
def create_route(payload: RouteCreate, db: DbSession):
    record = RouteRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return to_read_schema(record)


@router.put("/{route_id}", response_model=RouteRead, dependencies=protected)
def update_route(route_id: int, payload: RouteCreate, db: DbSession):
    """Повна заміна даних маршруту."""
    record = get_record_or_404(db, route_id)
    for field, value in payload.model_dump().items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return to_read_schema(record)


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=protected)
def delete_route(route_id: int, db: DbSession):
    record = get_record_or_404(db, route_id)
    db.delete(record)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
