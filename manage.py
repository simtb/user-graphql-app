from flask_script import Manager

from app.app import app, db, User, Post, Information, app


manager: Manager = Manager(app)


@manager.command
def drop():
    db.drop_all()
    return "Database has been dropped"


@manager.command
def up():
    db.create_all()

    user: User = User(username="user123")

    post: Post = Post()
    post.title: str = "Hello World"
    post.content: str = "Welcome to this GraphQL Demo"
    post.author: User = user

    info = Information()
    info.first_name: str = "User"
    info.last_name: str = "Demo"
    info.age: str = 25
    info.education: str = "University"
    info.company: str = "Company A"
    city: str = "London"
    info.favourite_hobby: str = "Running"
    info.favourite_song: str = "Billie Jean - Michael Jackson"
    info.favourite_movie: str = "Rush Hour 2"
    info.info_for_user: USER = user

    db.session.add(user)
    db.session.add(post)
    db.session.add(info)
    db.session.commit()

    return "Database and tables with dummy data has been created"


if __name__ == "__main__":
    manager.run()
