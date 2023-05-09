"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, bcrypt

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


class UserModelTestCase(TestCase):
    def setUp(self):
        """Creates a new database for the unit test to use."""
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Closes the database again at the end of the test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
            

    def test_user_password_hashing(self):
        with app.app_context():
            u = User.signup(username='test', password='password', email='test@example.com', image_url='')
            
            self.assertFalse(User.authenticate('test','not-password'))
            self.assertTrue(User.authenticate('test', 'password'))

    def test_user_repr(self):
        with app.app_context():
            u = User.signup(username='test', password='password', email='test@example.com', image_url='')
            
            db.session.commit()
            self.assertEqual(str(u), '<User #1: test, test@example.com>')

    def test_user_signup(self):
        with app.app_context():
            u = User.signup(username='test', password='password', email='test@example.com', image_url='')
            db.session.commit()
            self.assertEqual(u.username, 'test')
            self.assertEqual(u.email, 'test@example.com')
            

    def test_user_authenticate(self):
        with app.app_context():
            u = User.signup(username='test', password='password', email='test@example.com', image_url='')
            db.session.commit()
            user = User.authenticate('test', 'password')
            self.assertTrue(user)
            self.assertEqual(user.username, 'test')
            self.assertEqual(user.email, 'test@example.com')
            self.assertFalse(User.authenticate('test', 'not-password'))

    def test_user_following(self):
        with app.app_context():
            u1 = User.signup(username='test', password='password', email='test@example.com', image_url='')
            u2 = User.signup(username='test2', password='password', email='test2@example.com', image_url='')
            
            db.session.commit()
            self.assertFalse(u1.is_following(u2))
            u1.following.append(u2)
            db.session.commit()
            self.assertTrue(u1.is_following(u2))
            self.assertTrue(u2.is_followed_by(u1))

