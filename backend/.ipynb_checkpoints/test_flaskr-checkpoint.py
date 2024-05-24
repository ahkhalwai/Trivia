import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_NAME, DB_USER, DB_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DBNAME
        self.database_path ="postgresql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD,'localhost:5432', self.database_name)
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
    def test_all_available_category(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_category"])
        self.assertTrue(len(data["categories"]))
    
    def test_get_paginated_question(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["categories"])
        
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    def test_delete_question(self):
        res = self.client().delete("/questions/2")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 2)
        
    def test_422_if_question_id_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
    
    def test_create_new_question(self):
        self.new_question = {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "category": 3,
            "difficulty": 2,
        }
        
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        
    def test_405_if_question_creation_not_allowed(self):
        self.new_question = {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "category": 3,
            "difficulty": "easy", # Incorrect data type
        }
        
        res = self.client().post("/questions/45", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")
    
    def test_question_search_with_results(self):
        
        self.search = {"searchTerm": "Hall of Mirrors"}
        
        res = self.client().post("/questions/search", json=self.search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]),1)
        
    def test_question_search_error(self):
        self.search = {"searchTerm": "musef"}
        res = self.client().post("/questions/search", json=self.search)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], "resource not found")    
    
    def test_question_based_on_category(self):
        
        res = self.client().get("/categories/5/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        
    def test_questions_to_play_quiz(self):
        quiz_cond = {
            'previous_question':[2, 14],
            'category': {
                'id': 4,
                'type': 'History'
            }
        }
        
        res = self.client().post("/quizzes", json=quiz_cond)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
        self.assertNotEqual(data['question']['id'], 2)
        self.assertNotEqual(data['question']['id'], 14)
        self.assertEqual(data['question']['category'], 4)
        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()