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
        self.database_path = "postgres://postgres:postgres@{}/{}".format(
            'localhost:5432', self.database_name)
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
    Write at least one test for each test for successful operation and for expected errors.
    """

    def testGetCategories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def testGetPaginatedQuestions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories'].keys()), 6)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['total_questions'], len(Question.query.all()))

    def test404SentRequestingBeyondValidPage(self):
        res = self.client().get('/questions?page=10000')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def testGetSpecificQuestionsByCategory(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category']['id'], 1)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']), 3)
        self.assertEqual(data['total_questions'], len(Question.query.all()))

    def test404SentRequestingQuestionsForInvalidCategory(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def testDeleteSpecificQuestion(self):
        #         totalQuestionsBeforeDeleting = len(Question.query.all())

        res = self.client().delete('/questions/6')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
#         self.assertTrue(data['question'])
#         self.assertEqual(data['question'], 5)
#         self.assertEqual(data['total_questions'], totalQuestionsBeforeDeleting -1)

    def test404SentDeletingNonExistentQuestions(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test405SentRequestingQuestionsViaGet(self):
        res = self.client().get('/questions/1000')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')

    def testCreateQuestion(self):
        totalQuestionsBeforeCreatingNewQuestion = len(Question.query.all())

        res = self.client().post(
            '/questions',
            json={
                'question': 'test question',
                'answer': 'answer',
                'difficulty': 1,
                'category': 1})
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'],
                         totalQuestionsBeforeCreatingNewQuestion + 1)

    def testSearchQuestion(self):
        searchTerm = {'searchTerm': 'title'}
        res = self.client().post('/questions/search', json=searchTerm)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_quizzes(self):
        res = self.client().post(
            '/quizzes',
            json={
                'previous_questions': [20],
                'quiz_category': {
                    'id': '1',
                    'type': 'Science'}})
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 1)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
