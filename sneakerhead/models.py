"""SQLAlchemy models for Warbler."""


from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList


bcrypt = Bcrypt()
db = SQLAlchemy()



def update_db(data):
  if type(data) is list:
    db.session.add_all(data);
    db.session.commit();
  else:
    db.session.add(data);
    db.session.commit();



class Shoe(db.Model):
    """Shoes in the system."""

    __tablename__ = 'shoes'

    id = db.Column(db.Text, primary_key=True)
    brand = db.Column(db.Text)
    colorway = db.Column(db.Text)
    gender = db.Column(db.Text)
    name = db.Column(db.Text)
    release_date = db.Column(db.Text)
    retail_price = db.Column(db.Integer)
    style = db.Column(db.Text)
    title = db.Column(db.Text)
    year = db.Column(db.Integer)
    img_original = db.Column(db.Text)
    img_small = db.Column(db.Text)

    likes = db.relationship('User',
     secondary = 'likes', 
     backref = 'liked_shoes')

    def __init__(self, id, brand, colorway, gender, name, year, release_date, retail_price, style, title, img_original, img_small):
        self.id = id
        self.brand = brand
        self.colorway = colorway
        self.gender = gender.title()
        self.name = name
        self.year = year
        self.release_date = release_date
        self.retail_price = retail_price
        self.style = style
        self.title = title
        self.img_original = img_original
        self.img_small = img_small

    def __repr__(self):
        return (f'''<Shoe #{self.id}: 
        {self.colorway} {self.brand} {self.name}
        Released in {self.year} for ${self.retail_price}>''')

class Like(db.Model):
    """Mapping user likes to shoes."""

    __tablename__ = 'likes' 


    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )

    shoe_id = db.Column(
        db.Text,
        db.ForeignKey('shoes.id'),
        primary_key=True
    )


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )


    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"


    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False




def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
