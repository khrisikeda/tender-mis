import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.audit import write_audit_log
from app.core.deps import get_current_user, require_roles
from app.core.enums import AuditAction, RoleName
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductMatchOut, ProductOut

router = APIRouter(prefix="/catalogue", tags=["product-catalogue"])
MANAGE_CATALOGUE = require_roles([RoleName.ADMIN, RoleName.MANAGEMENT, RoleName.PROCUREMENT])


def product_search_text(product: Product) -> str:
    values = [product.name, product.product_code, product.category, product.subcategory, product.manufacturer, product.brand, product.model]
    values.extend(product.keywords or [])
    values.extend(f"{key} {value}" for key, value in (product.technical_specifications or {}).items())
    return " ".join(str(value or "") for value in values).lower()


@router.get("", response_model=list[ProductOut])
def list_products(
    category: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Product).filter(Product.is_active.is_(True))
    if category:
        query = query.filter(Product.category == category)
    return query.order_by(Product.name).all()


@router.get("/search", response_model=list[ProductMatchOut])
def search_products(
    q: str = Query(min_length=2),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    terms = {term for term in re.findall(r"[a-z0-9]+", q.lower()) if len(term) > 2}
    matches = []
    for product in db.query(Product).filter(Product.is_active.is_(True)).all():
        text = product_search_text(product)
        matched_terms = sorted(term for term in terms if term in text)
        score = round((len(matched_terms) / len(terms)) * 100, 2) if terms else 0
        if score:
            matches.append((score, matched_terms, product))
    matches.sort(key=lambda item: (-item[0], item[2].name))
    return [ProductMatchOut.model_validate({**ProductOut.model_validate(product, from_attributes=True).model_dump(), "match_score": score, "matched_terms": terms_found, "match_reason": "Matched against the persistent catalogue name, category, keywords, manufacturer, and technical specifications."}) for score, terms_found, product in matches[:limit]]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id, Product.is_active.is_(True)).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalogue product not found")
    return product


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(MANAGE_CATALOGUE)])
def create_product(payload: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if db.query(Product).filter(Product.product_code == payload.product_code).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product code already exists")
    product = Product(**payload.model_dump())
    db.add(product)
    db.flush()
    write_audit_log(db, user_id=current_user.id, action=AuditAction.CREATE, entity_type="product", entity_id=product.id, new_value=payload.model_dump(mode="json"))
    db.commit()
    db.refresh(product)
    return product