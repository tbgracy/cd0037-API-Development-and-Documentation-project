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
        self.database_path = "postgres://{}/{}".format(
            'postgres:abc@localhost:5432', self.database_name)
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

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data.get('categories', None))

    def test_categories_false_method(self):
        res = self.client().post('/categories')
        data = json.loads(res.data)

        self.assertEqual(data['error'], 405)
        self.assertTrue(data['messages'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'])

    def test_page_not_found_error(self):
        res = self.client().get('/questions?page=999')
        data = json.loads(res.data)

        self.assertEqual(data['error'], 404)
        self.assertIsNotNone(data['messages'])

    def test_delete_question(self):
        res = self.client().delete('/questions/4')
        data = json.loads(res.data)

        self.assertTrue(data['success'])
        self.assertEqual(data['deleted_question'], 4)
        # @TODO : re-insert deleted data

    def test_delete_question_error(self):
        res = self.client().delete('/questions/999')
        data = json.loads(res.data)

        self.assertEqual(data['error'], 404)

    def test_add_question_successfully(self):
        res = self.client().post('/questions', json={
            "question": "What's the name of this book?",
            "answer": "I have no idea.",
            "category": 1,
            "difficulty": 3
        })
        data = json.loads(res.data)

        self.assertTrue(data['success'])

    def test_add_question_error(self):
        res = self.client().post('/questions', json={
            "question": "What's your name?"
        })
        data = json.loads(res.data)

        self.assertEqual(data['error'], 400)

    def test_search_question(self):
        res = self.client().post('/search', json={
            'searchTerm': "What",
        })
        data = json.loads(res.data)

        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'] > 0)

    def test_search_no_result(self):
        res = self.client().post('/search')
        data = json.loads(res.data)

        self.assertEqual(data['error'], 400)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(data['currentCategory'], 'Science')
        self.assertTrue(data['totalQuestions'] > 0)

    def test_questions_by_category_not_found(self):
        res = self.client().get('/categories/9/questions')
        data = json.loads(res.data)

        self.assertEqual(data['error'], 404)

    def test_get_quiz_question(self):
        res = self.client().post(
            '/quizzes',
            json={
                'previous_questions': [],
                'quiz_category': {
                    'id': 1,
                    'type': 'Science'
                }
            }
        )
        data = json.loads(res.data)

        self.assertEqual(data['question']['category'], 1)
        self.assertEqual(len(data), 1)
        self.assertEqual(len(data['question']), 5)

    def test_quiz_bad_request(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(data['error'], 400)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
