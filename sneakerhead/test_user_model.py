"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


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


class UserModelTestCase(TestCase):
    """Test views for messages."""
    ### Setup and tear down blocks: ###

    def setUp(self):
        """Create test users, and client"""
        # Renew tables
        db.drop_all()
        db.create_all()
        # Make a user
        user = User.signup('test1', 'test1@test.com', 'password', None)
        # Set id
        u_id = 500
        user.id = u_id
        # Save user to db
        db.session.commit()

        # Query for users
        u = User.query.get(u_id);
        

        # Set user and id for test context:
        self.user= u
        self.u_id = u.id
        self.client = app.test_client()
    
    def tearDown(self):
        
        db.session.rollback()
        return super().tearDown()
    
### Testing user model
    def test_user_model(self):
        """Does basic model work?"""
        u = self.user

        # User should have no liked shoes
        self.assertEqual(len(u.liked_shoes), 0)
    
### Testing signup
    def test_good_signup(self):
        '''Create new user, test that data is saved'''
        # Create a user with valid creds
        u= self.user
        user_id = self.u_id
        # Get user
        user = User.query.get(user_id)
        # Test that the correct data is retireved
        self.assertIsNotNone(u)
        self.assertIsNotNone(user)
        self.assertTrue(user is u)
        #Test that data is saved
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'test1')
        self.assertEqual(user.email, 'test1@test.com')
        # Test that pass is encrypted
        self.assertNotEqual(user.password, 'password')
        self.assertIn('2b$', user.password)
    
    ### Bad signup tests
    def test_bad_username(self):
        '''Create user with invalid username'''
        bad_user = User.signup(None, "test3@test.com", 'password', None)
        user_id = 505;
        bad_user.id = user_id
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_bad_email(self):
        '''Create user with invalid email'''
        bad_user = User.signup("test3", None, 'password', None)
        user_id = 505;
        bad_user.id = user_id
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_bad_password(self):
        '''Create user with invalid password'''
        with self.assertRaises(ValueError) as context:
            User.signup('test3', 'test3@test.com', '', None)
        
        with self.assertRaises(ValueError) as context:
            User.signup('test3', 'test3@test.com', None, None)
### Liking a shoe
    def test_user_likes(self):
        '''Appends shoe to user's liked_shoes'''
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
    
        # Check liked_shoe count
        self.assertEqual(len(self.user.liked_shoes), 0)
        # Add shoe to likes
        self.user.liked_shoes.append(s)
        db.session.commit()
        # Cgeck that liked_shoes updated
        self.assertEqual(len(self.user.liked_shoes), 1)

        # Check follower identity
        self.assertEqual(s.likes[0].id, self.u_id)
    

### Auth tests:
    def test_good_auth(self):
        user = User.authenticate(self.user.username, "password")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.u_id)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user.username, "badpassword"))