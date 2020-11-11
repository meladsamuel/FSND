import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('melad', '511998', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_questions(self):
        """ check that all questions return as expect from the database"""
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 10)

    def test_get_question_not_found(self):
        """Check if the resource was not found, it will return the appropriate status code and error message"""
        res = self.client().get('/questions?page=1000')
        data = res.json
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        """Ensure that the question has been successfully deleted"""
        res = self.client().delete('/questions/9')
        data = res.json
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_failed_delete_question(self):
        """Ensure that returned the corresponding error if there is an error when deleting the question """
        res = self.client().delete('/questions/1000')
        data = res.json
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable entity')

    def test_create_new_question(self):
        """ test create new question successfully and check if the questions store successfully in the database"""
        question = {"answer": "ali", "category": 6, "difficulty": 1,
                    "question": "what is your name's?"}
        res = self.client().post('/questions', json=question)
        data = res.json
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        question_db = Question.query.get(data['created'])
        self.assertTrue(question_db)

    def test_failed_create_new_question(self):
        """Ensure that returned the corresponding error if there is an error when creating the new question"""
        res = self.client().post('/questions')
        self.assertEqual(res.status_code, 400)

    def test_search_on_question(self):
        """Make sure the question you want to search for is successfully returned"""
        search = {"searchTerm": "what is"}
        res = self.client().post('/questions', json=search)
        data = res.json
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['current_category'])
        self.assertTrue(data['total_questions'])

    def test_play_quiz(self):
        """ Ensure the questions return successfully and this questions is unique"""
        res1 = self.client().post('/quizzes',
                                  json={"previous_questions": [], "quiz_category": {"type": "Science", "id": "1"}})
        res2 = self.client().post('/quizzes',
                                  json={"previous_questions": [res1.json['question']['id']],
                                        "quiz_category": {"type": "Science", "id": "1"}})
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res2.status_code, 200)
        self.assertTrue(res1.json['question'])
        self.assertTrue(res2.json['question'])
        self.assertNotEqual(res1.json['question']['id'], res2.json['question']['id'])

    def test_400_play_quiz(self):
        """ Ensure the questions return successfully and this questions is unique"""
        res = self.client().post('/quizzes')
        self.assertEqual(res.status_code, 400)

    def test_send_not_allowed_method(self):
        """ check if Access-Control-Allow-Methods work"""
        res = self.client().put('/question')
        self.assertEqual(res.status_code, 405)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
