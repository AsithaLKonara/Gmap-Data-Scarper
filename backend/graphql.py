import graphene
from fastapi import APIRouter, Request, HTTPException, status
from starlette.graphql import GraphQLApp
from models import Users, Leads, Notifications
from database import SessionLocal
from auth import get_current_user
from jose import JWTError
import sqlalchemy

"""
GraphQL API for LeadTap: Unified endpoint for querying and mutating user, lead, notification, and analytics data.
- Authenticated via Bearer token (JWT)
- Exposes queries for users, leads, notifications, analytics
- Exposes mutations for lead CRUD, importing leads, marking notifications as read
- Context injection for current_user
- See /api/graphql for the interactive GraphQL playground
"""

class UserType(graphene.ObjectType):
    id = graphene.Int()
    email = graphene.String()
    plan = graphene.String()

class LeadType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    email = graphene.String()
    phone = graphene.String()
    company = graphene.String()
    tag = graphene.String()
    notes = graphene.String()
    status = graphene.String()
    source = graphene.String()
    user_id = graphene.Int()
    created_at = graphene.String()
    updated_at = graphene.String()

class NotificationType(graphene.ObjectType):
    id = graphene.Int()
    user_id = graphene.Int()
    type = graphene.String()
    message = graphene.String()
    read = graphene.Boolean()
    created_at = graphene.String()

class AnalyticsType(graphene.ObjectType):
    total_leads = graphene.Int()
    leads_by_status = graphene.JSONString()
    conversion_rate = graphene.Float()

class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    leads = graphene.List(LeadType)
    notifications = graphene.List(NotificationType)
    analytics = graphene.Field(AnalyticsType)

    def resolve_users(self, info):
        user = info.context.get('current_user')
        if not user:
            raise Exception("Authentication required")
        db = SessionLocal()
        users = db.query(Users).filter(Users.id == user.id).all()
        db.close()
        return users

    def resolve_leads(self, info):
        user = info.context.get('current_user')
        if not user:
            raise Exception("Authentication required")
        db = SessionLocal()
        leads = db.query(Leads).filter(Leads.user_id == user.id).all()
        db.close()
        return leads

    def resolve_notifications(self, info):
        user = info.context.get('current_user')
        if not user:
            raise Exception("Authentication required")
        db = SessionLocal()
        notifications = db.query(Notifications).filter(Notifications.user_id == user.id).all()
        db.close()
        return notifications

    def resolve_analytics(self, info):
        user = info.context.get('current_user')
        if not user:
            raise Exception("Authentication required")
        db = SessionLocal()
        total_leads = db.query(Leads).filter(Leads.user_id == user.id).count()
        # Leads by status
        status_counts = db.query(Leads.status, sqlalchemy.func.count(Leads.id)).filter(Leads.user_id == user.id).group_by(Leads.status).all()
        leads_by_status = {status: count for status, count in status_counts}
        # Conversion rate: converted / total
        converted = leads_by_status.get('converted', 0)
        conversion_rate = (converted / total_leads) if total_leads > 0 else 0.0
        db.close()
        return AnalyticsType(
            total_leads=total_leads,
            leads_by_status=leads_by_status,
            conversion_rate=conversion_rate
        )

class CreateLead(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()
        company = graphene.String()
        tag = graphene.String()
        notes = graphene.String()
        status = graphene.String()
        source = graphene.String()

    lead = graphene.Field(lambda: LeadType)

    def mutate(self, info, name, email, phone=None, company=None, tag=None, notes=None, status=None, source=None):
        user = info.context.get('current_user')
        if not user:
            raise Exception("Authentication required")
        db = SessionLocal()
        lead = Leads(
            name=name,
            email=email,
            phone=phone,
            company=company,
            tag=tag,
            notes=notes,
            status=status or 'new',
            source=source or 'manual',
            user_id=user.id
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        db.close()
        return CreateLead(lead=lead)

class UpdateLead(graphene.Mutation):
    class Arguments:
        lead_id = graphene.Int(required=True)
        name = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        company = graphene.String()
        tag = graphene.String()
        notes = graphene.String()
        status = graphene.String()
        source = graphene.String()

    lead = graphene.Field(lambda: LeadType)

    def mutate(self, info, lead_id, name=None, email=None, phone=None, company=None, tag=None, notes=None, status=None, source=None):
        user = info.context.get('current_user')
        if not user:
            raise Exception("Authentication required")
        db = SessionLocal()
        lead = db.query(Leads).filter(Leads.id == lead_id, Leads.user_id == user.id).first()
        if not lead:
            db.close()
            raise Exception("Lead not found")
        if name is not None:
            lead.name = name
        if email is not None:
            lead.email = email
        if phone is not None:
            lead.phone = phone
        if company is not None:
            lead.company = company
        if tag is not None:
            lead.tag = tag
        if notes is not None:
            lead.notes = notes
        if status is not None:
            lead.status = status
        if source is not None:
            lead.source = source
        db.commit()
        db.refresh(lead)
        db.close()
        return UpdateLead(lead=lead)

class DeleteLead(graphene.Mutation):
    class Arguments:
        lead_id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, lead_id):
        user = info.context.get('current_user')
        if not user:
            raise Exception("Authentication required")
        db = SessionLocal()
        lead = db.query(Leads).filter(Leads.id == lead_id, Leads.user_id == user.id).first()
        if not lead:
            db.close()
            raise Exception("Lead not found")
        db.delete(lead)
        db.commit()
        db.close()
        return DeleteLead(ok=True)

class LeadInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()
    company = graphene.String()
    tag = graphene.String()
    notes = graphene.String()
    status = graphene.String()
    source = graphene.String()

class ImportLeads(graphene.Mutation):
    class Arguments:
        leads = graphene.List(LeadInput, required=True)

    imported_count = graphene.Int()

    def mutate(self, info, leads):
        user = info.context.get('current_user')
        if not user:
            raise Exception("Authentication required")
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
        return ImportLeads(imported_count=count)

class MarkNotificationRead(graphene.Mutation):
    class Arguments:
        notification_id = graphene.Int(required=True)

    notification = graphene.Field(lambda: NotificationType)

    def mutate(self, info, notification_id):
        user = info.context.get('current_user')
        if not user:
            raise Exception("Authentication required")
        db = SessionLocal()
        notification = db.query(Notifications).filter(Notifications.id == notification_id, Notifications.user_id == user.id).first()
        if notification:
            notification.read = True
            db.commit()
            db.refresh(notification)
        db.close()
        return MarkNotificationRead(notification=notification)

class Mutation(graphene.ObjectType):
    create_lead = CreateLead.Field()
    update_lead = UpdateLead.Field()
    delete_lead = DeleteLead.Field()
    import_leads = ImportLeads.Field()
    mark_notification_read = MarkNotificationRead.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

# OpenAPI router for GraphQL endpoint
router = APIRouter(prefix="/api", tags=["graphql"])

# Custom GraphQLApp to inject current_user into context
def get_graphql_context(request: Request):
    """
    Extracts the current user from the Authorization header and injects it into the GraphQL context.
    """
    db = SessionLocal()
    user = None
    try:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]
            try:
                from jose import jwt
                from config import SECRET_KEY, ALGORITHM
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("sub")
                if user_id:
                    user = db.query(Users).filter(Users.id == int(user_id)).first()
            except JWTError:
                pass
    finally:
        db.close()
    return {"request": request, "current_user": user}

class AuthGraphQLApp(GraphQLApp):
    def __call__(self, scope, receive, send):
        async def app(request: Request):
            context = get_graphql_context(request)
            return await super().__call__(scope, receive, send, context=context)
        return app

# Add the /api/graphql endpoint with OpenAPI summary/description
router.add_route(
    "/graphql",
    AuthGraphQLApp(schema=schema),
    methods=["GET", "POST"],
    summary="GraphQL API endpoint",
    description="Unified GraphQL endpoint for querying and mutating user, lead, notification, and analytics data. Requires Bearer token authentication."
) 