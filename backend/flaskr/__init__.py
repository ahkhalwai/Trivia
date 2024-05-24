import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

# Learn from Endpoints and Payloads and API Testing chapter and most of them start implement then i also make changes in frontend due to error by creating empty box question, thanks to mentor for guiding me https://knowledge.udacity.com/questions/1033082, https://knowledge.udacity.com/questions/1033022, https://knowledge.udacity.com/questions/1032852

QUESTIONS_PER_PAGE = 10


# Implementing Pagination chapter 7 talk about how to implement paginate
def paginate_questions(request,question_set):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE # start = (1-1) * 10 = 0
    end = start + QUESTIONS_PER_PAGE # end = 0 + 10 = 10 
    
    format_question = [questions.format() for questions in question_set] 
    current_question = format_question[start:end]
    
    return current_question

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    #CORS(app)
    
    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}}) # Implementing Flask-CORS chapter 5 of Endpoints and Payloads
    
    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """
    # Implementing Flask-CORS chapter 5 of Endpoints and Payloads
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    
    
    # Flask - Route Decorator and Pagination of Endpoints and Payloads chapter 6 learn about route
    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def all_available_category():
        category = Category.query.all()
        cat = {}
        for categories in category:
            cat[categories.id] = categories.type
        
        return jsonify({
          'success':True,
          'categories':cat,
          'total_category':len(cat) #checking the no of category.
        })

    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_question():
        # (every 10 questions)pagination
        # list of questions
        question = Question.query.all()
        paginate =  paginate_questions(request,question) # 
        
        if len(paginate) == 0:
            abort(404) # throw this "message": "resource not found"
        
        # number of total questions
        total_questions = len(question)
                
        # categories
        category = Category.query.all()
        cat = {}
        for categories in category:
            cat[categories.id] = categories.type
        
        return jsonify({
            'success':True,
            'questions':paginate,
            'totalQuestions':total_questions,
            'categories':cat
        })
    
    """
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all() #Sorting by question id
            current_question =  paginate_questions(request,selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "question": current_question,
                    "total_question": len(Question.query.all()),
                }
            )

        except:
            abort(422)
    
    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def new_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category,difficulty=new_difficulty)
            
            if(new_question is None or new_answer is None or new_category is None or new_difficulty is None):
                   abort(400) # due to error in empty question created i implement this and mentor guide me
            
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)
    
    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=["POST"])
    def search_question():
        search_term = request.json.get("searchTerm", "")
        matching_question = Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()

        if not matching_question:
            abort(404) # error in search term, whenever i type, it create new question now resolve.

        format_question = paginate_questions(request, matching_question)    

        return jsonify({
                "success": True,
                "questions": format_question,
                "total_questions": len(matching_question)
            })     
            
    
    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_question_based_on_category(category_id):
        question = Question.query.filter_by(category=category_id).all()
        
        if question is None:
                abort(404)
        
        format_question = [questions.format() for questions in question]
        
        return jsonify({
          'success':True,
          'questions':format_question,  
          'total_questions':len(question)
        })
    
    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def get_questions_to_play_quiz():
        data = request.get_json()
        category_id = data.get("category", {}).get("id")
        previous_question_id = data.get("previous_question", [])

        # Define filters
        
        # The category of questions the player wants to play
        category_filter = (Question.category == category_id) if category_id else True
        
        # The ID of the question that was previously asked.
        previous_question_filter = ~Question.id.in_(previous_question_id) if previous_question_id else True

        # Apply filters and retrieve matching questions
        matching_questions = Question.query.filter(category_filter, previous_question_filter, ).all() 

        if matching_questions:
            # Select a random question from the matching questions
            selected_question = random.choice(matching_questions).format()

            # Return the selected question
            return jsonify({
                "success": True,
                "question": selected_question,
                "total_question":len(selected_question)
            })
        else:
            return jsonify({
                "success": False,
                "message": "No matching questions found."
            })

    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    
    # Flask Error Handling chapter help me in this
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405
    
    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500
    return app
