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
    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_messages_show(self):
        """Test if Messages show"""
        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.testuser.id
        with app.app_context():
            timestamp = datetime(2023, 5, 9, 12, 0, 0)    
            message = Message(text='test Message', timestamp=timestamp, user_id = self.testuser.id)
            db.session.add(message)
            db.session.commit()
            res = self.client.get(f'/messages/{message.id}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<p class="single-message">test Message</p>',html)

    def test_message_destroy(self):
        """Test Delete Messages"""

        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.testuser.id
        with app.app_context():
            timestamp = datetime(2023, 5, 9, 12, 0, 0)    
            message = Message(text='test Message', timestamp=timestamp, user_id = self.testuser.id)
            db.session.add(message)
            db.session.commit()
            res = self.client.post(f'/messages/{message.id}/delete')
            html = res.get_data(as_text=True)

            self.assertEqual(res.location, f"/users/{self.testuser.id}")
            self.assertEqual(res.status_code, 302)
            deleted_message = Message.query.get(message.id)
            res = self.client.get(f"/users/{self.testuser.id}")
            self.assertIsNone(deleted_message)