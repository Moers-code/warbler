"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from datetime import datetime
from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

with app.app_context():
    db.drop_all()
    db.create_all()
# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            User.query.delete()
            Message.query.delete()

            self.client = app.test_client()

            self.testuser = User.signup(username="testuser",
                                        email="test@test.com",
                                        password="testuser",
                                        image_url=None)

            db.session.commit()
            db.session.refresh(self.testuser)
            
    def test_list_users(self):
        """test Listing Users"""
        
        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.testuser.id


        res = self.client.get("/users")
        html = res.get_data(as_text=True)
        
        self.assertEqual(res.status_code, 200)
        self.assertIn('<p>@testuser</p>', html)

    def test_users_show(self):
        """Test if Users Show"""
        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.testuser.id
        with app.app_context():
            timestamp = datetime(2023, 5, 9, 12, 0, 0)    
            message = Message(text='test Message', timestamp=timestamp, user_id = self.testuser.id)
            db.session.add(message)
            db.session.commit()

            res = self.client.get(f'/users/{self.testuser.id}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f'<a href="/users/{self.testuser.id}">@testuser</a>',html)
            self.assertIn('<p>test Message</p>',html)


    
    def test_users_following(self):
        """Test if Following List Show"""
        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.testuser.id

        with app.app_context():
            
            followed = User.signup(username="testfollowed",
                                        email="followed@test.com",
                                        password="testuser",
                                        image_url=None)
            db.session.commit()

            res = self.client.post(f'/users/follow/{followed.id}')

            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, f"/users/{self.testuser.id}/following")

            res = self.client.get(f'/users/{self.testuser.id}/following')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<p>@testfollowed</p>', html)

    
   
    def test_followers(self):
        """Test Add Followers and Display"""
        
        

        with app.app_context():
            follower = User.signup(username="testfollower",
                                        email="follower@test.com",
                                        password="testuser",
                                        image_url=None)
            db.session.commit()

            with self.client.session_transaction() as sess:
                sess[CURR_USER_KEY] = follower.id

            res = self.client.post(f'/users/follow/{self.testuser.id}')

            self.assertEqual(res.status_code, 302)
           

            res = self.client.get(f'/users/{follower.id}/following')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<p>@testuser</p>', html)
            