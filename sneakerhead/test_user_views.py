"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Shoe, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///test_sneaker_head"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for user routes."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.user = User.signup("test1", "test1@test.com", "password", None)
        self.u_id = 778
        self.user.id = self.u_id


        db.session.commit()

        
    
    def tearDown(self):
        db.session.rollback()
        return super().tearDown()

    def test_user_profile_no_likes_no_log(self):
        with self.client as client:
            resp = client.get(f"/users/{self.u_id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("<p>Test1\\\'s Profile</p>", str(resp.data))
            self.assertIn("Test1 has not liked any shoes", str(resp.data))
            self.assertNotIn("Delete", str(resp.data))


    
    def setup_likes(self):

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
        
        self.s = Shoe.query.get(s.id)

        self.user.liked_shoes.append(self.s)
        db.session.commit()
    def test_user_profile_w_likes_no_log(self):
        self.setup_likes()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['brands'] = ['Nike', 'Adidas']
            resp = c.get(f"/users/{self.u_id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("<p>Test1\\\'s Profile</p>", str(resp.data))
            
            self.assertIn("Nike", str(resp.data))
            self.assertNotIn("Delete", str(resp.data))
    
    def test_user_profile_w_likes_w_log(self):
        self.setup_likes()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u_id
                sess['brands'] = ['Nike', 'Adidas']
            resp = c.get(f'/users/{self.u_id}')

            self.assertEqual(resp.status_code, 200)

            self.assertIn("<p>Test1\\\'s Profile</p>", str(resp.data))

            self.assertIn("Nike", str(resp.data))
            
            self.assertIn("Delete", str(resp.data))
    
    