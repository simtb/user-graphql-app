import datetime
import os

from flask import Flask
from flask_graphql import GraphQLView
from flask_sqlalchemy import SQLAlchemy
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField


app: Flask = Flask(__name__)
base_directory: str = os.path.abspath(os.path.dirname(__file__))


# Configs
app.config["SQLALCHEMY_DATABASE_URI"]: str = "sqlite:///" + os.path.join(
    base_directory, "data.sqlite"
)
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"]: bool = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]: bool = True


# Modules
db: SQLAlchemy = SQLAlchemy(app)


# Models
class User(db.Model):
    __tablename__: str = "users"

    uuid: db.Column = db.Column(db.Integer, primary_key=True)
    username: db.Column = db.Column(db.String(256), index=True, unique=True)
    datetime_created: db.Column = db.Column(
        db.DateTime, default=datetime.datetime.now()
    )
    posts: db.relationship = db.relationship("Post", backref="author")
    informantion: db.relationship = db.relationship(
        "Information", backref="info_for_user"
    )

    def __repr__(self):
        return "<User: {}>".format(self.username)


class Post(db.Model):
    __tablename__: str = "posts"

    uuid: db.Column = db.Column(db.Integer, primary_key=True)
    title: db.Column = db.Column(db.String(256), index=True)
    content: db.Column = db.Column(db.Text)
    datetime_created: db.Column = db.Column(
        db.DateTime, default=datetime.datetime.now()
    )
    author_id: db.Column = db.Column(db.Integer, db.ForeignKey("users.uuid"))

    def __repr__(self):
        return "<Post: {}>".format(self.title)


class Information(db.Model):
    __tablename__: str = "informations"

    uuid: db.Column = db.Column(db.Integer, primary_key=True)
    first_name: db.Column = db.Column(db.String, nullable=False)
    last_name: db.Column = db.Column(db.String, nullable=False)
    age: db.Column = db.Column(db.Integer, nullable=False)
    education: db.Column = db.Column(db.String)
    company: db.Column = db.Column(db.String)
    city: db.Column = db.Column(db.String)
    favourite_hobby: db.Column = db.Column(db.String)
    favourite_song: db.Column = db.Column(db.String)
    favourite_movie: db.Column = db.Column(db.String)
    information_id: db.Column = db.Column(db.Integer, db.ForeignKey("users.uuid"))

    def __repr__(self):
        return "<Information for user: {}>".format(self.information_id)


# Schema Objects


class PostObject(SQLAlchemyObjectType):
    class Meta:
        model = Post
        interfaces = (graphene.relay.Node,)


class UserObject(SQLAlchemyObjectType):
    class Meta:
        model = User
        interfaces = (graphene.relay.Node,)


class InformationObject(SQLAlchemyObjectType):
    class Meta:
        model: db.Model = Information
        interfaces: tuple = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_posts = SQLAlchemyConnectionField(PostObject)
    all_users = SQLAlchemyConnectionField(UserObject)
    all_information = SQLAlchemyConnectionField(InformationObject)


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)

    user = graphene.Field(lambda: UserObject)

    def mutate(self, info, username):
        user = User(username=username)

        db.session.add(user)
        db.session.commit()

        return CreateUser(user=user)


class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        username = graphene.String(required=True)

    post = graphene.Field(lambda: PostObject)

    def mutate(self, info, title, content, username):
        user = User.query.filter_by(username=username).first()
        post = Post(title=title, content=content)
        if user is not None:
            post.author = user
        db.session.add(post)
        db.session.commit()

        return CreatePost(post=post)


class CreateInformation(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        age = graphene.Int(required=True)
        education = graphene.String(required=False)
        company = graphene.String(required=False)
        city = graphene.String(required=False)
        favourite_hobby = graphene.String(required=False)
        favourite_song = graphene.String(required=False)
        favourite_movie = graphene.String(required=False)

    information = graphene.Field(lambda: InformationObject)

    def mutate(
        self,
        info,
        username,
        first_name,
        last_name,
        age,
        education,
        company,
        city,
        favourite_hobby,
        favourite_song,
        favourite_movie,
    ):
        user = User.query.filter_by(username=username).first()
        information = Information(
            first_name=first_name,
            last_name=last_name,
            age=age,
            education=education,
            company=company,
            city=city,
            favourite_hobby=favourite_hobby,
            favourite_song=favourite_song,
            favourite_movie=favourite_movie,
        )
        if user is not None:
            information.info_for_user = user
        db.session.add(information)
        db.session.commit()

        return CreateInformation(information=information)


class Mutation(graphene.ObjectType):
    create_user: CreateUser.Field() = CreateUser.Field()
    create_post: CreatePost.Field() = CreatePost.Field()
    created_information: CreateInformation.Field() = CreateInformation.Field()


schema: graphene.Schema = graphene.Schema(query=Query, mutation=Mutation)

# Routes


@app.route("/")
def index_page():
    return "<h1> AN AMAZING SOCIAL MEDIA WEBSITE - GraphQL </h1>"


app.add_url_rule(
    "/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True)
)

if __name__ == "__main__":
    app.run(debug=True)
