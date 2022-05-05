"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, Shoe, User

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


class ShoeViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

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
        self.client = app.test_client()
 
    def test_show_all(self):
        """Does shoe route render list of all shoes?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with self.client as c:
        #     with c.session_transaction() as sess:
        #         sess[CURR_USER_KEY] = self.user.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.get("/shoes")

            # Make sure it redirects
            self.assertEqual(resp.status_code, 200)

            self.assertIn('Nike SB Dunk Low Blue Raspberry', str(resp.data))

    def test_show_brand(self):
        with self.client as c:
            resp = c.get("/shoes/Nike")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    # def test_add_invalid_user(self):
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = 99222224 # user does not exist

    #         resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("Access unauthorized", str(resp.data))
    
    # def test_message_show(self):

    #     m = Message(
    #         id=1234,
    #         text="a test message",
    #         user_id=self.user_id
    #     )
        
    #     db.session.add(m)
    #     db.session.commit()

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.user.id
            
    #         m = Message.query.get(1234)

    #         resp = c.get(f'/messages/{m.id}')

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn(m.text, str(resp.data))

    # def test_invalid_message_show(self):
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.user.id
            
    #         resp = c.get('/messages/99999999') # does not exist!

    #         self.assertEqual(resp.status_code, 404)

    # def test_message_delete(self):

    #     m = Message(
    #         id=1234,
    #         text="a test message",
    #         user_id=self.user_id
    #     )
    #     db.session.add(m)
    #     db.session.commit()

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.user.id

    #         resp = c.post("/messages/1234/delete", follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)

    #         m = Message.query.get(1234)
    #         self.assertIsNone(m)

    # def test_unauthorized_message_delete(self):

    #     # A second user that will try to delete the message
    #     u = User.signup(username="unauthorized-user",
    #                     email="testtest@test.com",
    #                     password="password",
    #                     image_url=None)
    #     u.id = 76543

    #     #Message is owned by user
    #     m = Message(
    #         id=1234,
    #         text="a test message",
    #         user_id=self.user_id
    #     )
    #     db.session.add_all([u, m])
    #     db.session.commit()
    #     m = Message.query.get(m.id)
    #     self.assertIsNotNone(m)
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = 76543

    #         resp = c.post("/messages/1234/delete", follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('You do not have permission to do this', str(resp.data))

    # def test_message_delete_no_authentication(self):

    #     m = Message(
    #         id=1234,
    #         text="a test message",
    #         user_id=self.user_id
    #     )
    #     db.session.add(m)
    #     db.session.commit()

    #     with self.client as c:
    #         resp = c.post("/messages/1234/delete", follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('Access unauthorized.', str(resp.data))

    #         m = Message.query.get(1234)
    #         self.assertIsNotNone(m)
