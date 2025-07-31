import strawberry
from fastapi import APIRouter, Request, Depends, HTTPException
from strawberry.fastapi import GraphQLRouter
from models import Users, Leads, Notifications
from database import SessionLocal
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM
from typing import List, Optional
import sqlalchemy

# Strawberry types
@strawberry.type
class UserType:
    id: int
    email: str
    plan: str

@strawberry.type
class LeadType:
    id: int
    name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    tag: Optional[str]
    notes: Optional[str]
    status: Optional[str]
    source: Optional[str]
    user_id: int
    created_at: Optional[str]
    updated_at: Optional[str]

@strawberry.type
class NotificationType:
    id: int
    user_id: int
    type: str
    message: str
    read: Optional[bool]
    created_at: Optional[str]

@strawberry.type
class AnalyticsType:
    total_leads: int
    leads_by_status: strawberry.scalar(dict)
    conversion_rate: float

# Auth context
class Context:
    def __init__(self, request: Request):
        self.request = request
        self.current_user = None
        db = SessionLocal()
        try:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1]
                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    user_id = payload.get("sub")
                    if user_id:
                        self.current_user = db.query(Users).filter(Users.id == int(user_id)).first()
                except JWTError:
                    pass
        finally:
            db.close()

def get_context_dependency(request: Request) -> Context:
    return Context(request)

# Query
@strawberry.type
class Query:
    @strawberry.field
    def users(self, info) -> List[UserType]:
        user = info.context.current_user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        db = SessionLocal()
        users = db.query(Users).filter(Users.id == user.id).all()
        db.close()
        return users

    @strawberry.field
    def leads(self, info) -> List[LeadType]:
        user = info.context.current_user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        db = SessionLocal()
        leads = db.query(Leads).filter(Leads.user_id == user.id).all()
        db.close()
        return leads

    @strawberry.field
    def notifications(self, info) -> List[NotificationType]:
        user = info.context.current_user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        db = SessionLocal()
        notifications = db.query(Notifications).filter(Notifications.user_id == user.id).all()
        db.close()
        return notifications

    @strawberry.field
    def analytics(self, info) -> AnalyticsType:
        user = info.context.current_user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        db = SessionLocal()
        total_leads = db.query(Leads).filter(Leads.user_id == user.id).count()
        status_counts = db.query(Leads.status, sqlalchemy.func.count(Leads.id)).filter(Leads.user_id == user.id).group_by(Leads.status).all()
        leads_by_status = {status: count for status, count in status_counts}
        converted = leads_by_status.get('converted', 0)
        conversion_rate = (converted / total_leads) if total_leads > 0 else 0.0
        db.close()
        return AnalyticsType(
            total_leads=total_leads,
            leads_by_status=leads_by_status,
            conversion_rate=conversion_rate
        )

# Input types
@strawberry.input
class LeadInput:
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    tag: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None

# Mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_lead(self, info, input: LeadInput) -> LeadType:
        user = info.context.current_user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        db = SessionLocal()
        lead = Leads(
            name=input.name,
            email=input.email,
            phone=input.phone,
            company=input.company,
            tag=input.tag,
            notes=input.notes,
            status=input.status or 'new',
            source=input.source or 'manual',
            user_id=user.id
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        db.close()
        return lead

    @strawberry.mutation
    def update_lead(self, info, lead_id: int, input: LeadInput) -> LeadType:
        user = info.context.current_user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        db = SessionLocal()
        lead = db.query(Leads).filter(Leads.id == lead_id, Leads.user_id == user.id).first()
        if not lead:
            db.close()
            raise HTTPException(status_code=404, detail="Lead not found")
        for field, value in input.__dict__.items():
            if value is not None:
                setattr(lead, field, value)
        db.commit()
        db.refresh(lead)
        db.close()
        return lead

    @strawberry.mutation
    def delete_lead(self, info, lead_id: int) -> bool:
        user = info.context.current_user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        db = SessionLocal()
        lead = db.query(Leads).filter(Leads.id == lead_id, Leads.user_id == user.id).first()
        if not lead:
            db.close()
            raise HTTPException(status_code=404, detail="Lead not found")
        db.delete(lead)
        db.commit()
        db.close()
        return True

    @strawberry.mutation
    def import_leads(self, info, leads: List[LeadInput]) -> int:
        user = info.context.current_user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        db = SessionLocal()
        count = 0
        for lead_data in leads:
            lead = Leads(
                name=lead_data.name,
                email=lead_data.email,
                phone=lead_data.phone,
                company=lead_data.company,
                tag=lead_data.tag,
                notes=lead_data.notes,
                status=lead_data.status or 'new',
                source=lead_data.source or 'import',
                user_id=user.id
            )
            db.add(lead)
            count += 1
        db.commit()
        db.close()
        return count

    @strawberry.mutation
    def mark_notification_read(self, info, notification_id: int) -> Optional[NotificationType]:
        user = info.context.current_user
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        db = SessionLocal()
        notification = db.query(Notifications).filter(Notifications.id == notification_id, Notifications.user_id == user.id).first()
        if notification:
            notification.read = True
            db.commit()
            db.refresh(notification)
        db.close()
        return notification

schema = strawberry.Schema(query=Query, mutation=Mutation)

# Strawberry GraphQL router
router = APIRouter(prefix="/api", tags=["graphql"])

graphql_app = GraphQLRouter(schema, context_getter=get_context_dependency)
router.include_router(graphql_app, prefix="/graphql") 