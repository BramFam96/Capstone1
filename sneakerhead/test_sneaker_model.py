"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Shoe

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///test_sneaker_head"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class SneakerModelTestCase(TestCase):
    """Test model for shoes."""

    def setUp(self):
        """Create test shoes, and user."""
        # Renew tables
        db.drop_all()
        db.create_all()
        
        self.uid = 200
        u = User.signup("testing", "test@test.com", "password", None)
        u.id = self.uid
        db.session.commit()

        s = Shoe(
        id = 'asd8f-fds89-asdf',
        brand = 'Nike',
        colorway = 'Blue',
        gender = 'Men',
        name = 'Dunk Low Blue Raspberry',
        year = 2022,
        release_date = '2022-01-09',
        retail_price = 109,
        style = 'dunks',
        title = 'Nike SB Dunk Low Blue Raspberry',
        img_original = 'https://images.stockx.com/images/Nike-PG-6-All-Star-Weekend-2022.jpg?fit=fill&bg=FFFFFF&w=700&h=500&fm=webp&auto=compress&trim=color&q=90&dpr=2&updated_at=1645038148',
        img_small = 'https://images.stockx.com/images/Nike-PG-6-All-Star-Weekend-2022.jpg?fit=fill&bg=FFFFFF&w=700&h=500&fm=webp&auto=compress&trim=color&q=90&dpr=2&updated_at=1645038148'
        )

        db.session.add(s)
        db.session.commit()
        
        
        self.u = User.query.get(u.id)
        self.s = Shoe.query.get(s.id)
        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()
        return super().tearDown()

    def test_sneaker_model(self):
        """Was the sneaker created with default values?"""
        # Sneaker should have no likes
        self.assertEqual(len(self.s.likes), 0)


    def test_shoe_likes(self):
        '''Does the model link liked shoes with users?'''
        self.s.likes.append(self.u)

        db.session.commit()

        # Sneaker should have one like
        self.assertEqual(len(self.s.likes), 1)