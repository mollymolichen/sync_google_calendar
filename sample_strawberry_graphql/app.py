from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry
from typing import List, Optional
from models import USERS, POSTS

# --- GraphQL Object Types ---

@strawberry.type
class Post:
    id: str
    title: str

@strawberry.type
class User:
    id: str
    name: str

    @strawberry.field
    def posts(self) -> List[Post]:
        user_posts = [p for p in POSTS if p["user_id"] == self.id]
        return [Post(**p) for p in user_posts]


# --- Queries ---

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: str) -> Optional[User]:
        data = USERS.get(id)
        if not data:
            return None
        return User(**data)

    @strawberry.field
    def users(self) -> List[User]:
        return [User(**u) for u in USERS.values()]


# --- Mutations ---

@strawberry.type
class Mutation:
    @strawberry.field
    def create_post(self, user_id: str, title: str) -> Post:
        new_id = str(len(POSTS) + 100)
        post = {"id": new_id, "title": title, "user_id": user_id}
        POSTS.append(post)
        return Post(**post)


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
