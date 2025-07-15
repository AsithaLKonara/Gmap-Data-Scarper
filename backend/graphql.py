import graphene
from fastapi import APIRouter
from starlette.graphql import GraphQLApp
from models import User
from database import SessionLocal

class UserType(graphene.ObjectType):
    id = graphene.Int()
    email = graphene.String()
    plan = graphene.String()

class Query(graphene.ObjectType):
    users = graphene.List(UserType)

    def resolve_users(self, info):
        db = SessionLocal()
        users = db.query(User).all()
        db.close()
        return users

schema = graphene.Schema(query=Query)

router = APIRouter()
router.add_route("/graphql", GraphQLApp(schema=schema)) 