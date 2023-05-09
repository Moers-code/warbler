from unittest import TestCase
from datetime import datetime
from models import db, Message, User
from app import app
import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

class TestMessageModel(TestCase):
    """Test Message Model"""

    def setUp(self):
        """Creates a new database for the unit test to use."""
        with app.app_context():
            db.create_all()
            self.user = User.signup(username='netesting', email='netesting@example.com', password='testpass', image_url='')
            db.session.commit()
            db.session.refresh(self.user)
            
    def tearDown(self):
        """Closes the database again at the end of the test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_message_text(self):
        with app.app_context():
            timestamp = datetime(2023, 5, 9, 12, 0, 0)
            message = Message(text='12test message', timestamp=timestamp, user_id=self.user.id)
            db.session.add(message)
            db.session.commit()
            self.assertEqual(message.text, '12test message')
            db.session.delete(message)
            
    def test_message_timestamp(self):
        with app.app_context():
            message = Message(text='2test message', timestamp=datetime.utcnow(), user_id=self.user.id)
            db.session.add(message)
            db.session.commit()
            self.assertIsNotNone(message.timestamp)
            db.session.delete(message)

    def test_message_user(self):
        with app.app_context():
            message = Message(text='7test message', timestamp=datetime.utcnow(), user_id=self.user.id)
            db.session.add(message)
            db.session.commit()
            self.assertEqual(message.user_id, self.user.id)
            db.session.delete(message)
            db.session.commit()
            self.assertIsNone(db.session.query(Message).filter_by(id=message.id).first())
