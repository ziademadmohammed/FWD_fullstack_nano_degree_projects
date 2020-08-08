import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql.expression import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
  # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    DONE : Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={r'*': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        '''
        Use the after_request decorator to set Access-Control-Allow-Headers
        Use the after_request decorator to set Access-Control-Allow-Methods
        Use the after_request decorator to set Access-Control-Allow-Credentials
        '''
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')

        return response

    @app.route('/categories', methods=['GET'])
    def getCategories():
        '''
        An endpoint to handle GET requests for all available categories.
        '''
        try:
            categories = Category.query.all()
            if (len(categories) == 0):
                abort(404)

            parsedCategories = {
                category.id: category.type for category in categories}

            return jsonify({
                'success': True,
                'categories': parsedCategories,
                'total_categories': len(Category.query.all())
            })

        except Exception:
            abort(422)

    @app.route('/questions', methods=['GET'])
    def get_questions():
        '''
        An endpoint to handle GET requests for questions, including pagination (10 questions).
        returns a list of questions, number of total questions, current category, categories.
        '''
        selection = Question.query.order_by(Question.id).all()
        currentPaginatedQuestions = paginate(request, selection)

        if (len(currentPaginatedQuestions) == 0):
            abort(404)

        parsedCategories = {
            category.id: category.type for category in Category.query.all()}

        return jsonify({
            'success': True,
            'questions': currentPaginatedQuestions,
            'total_questions': len(Question.query.all()),
            'current_category': [],
            'categories': parsedCategories
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        '''
        An endpoint to DELETE question using a question ID.
        '''
        questionToDelete = Question.query.filter(
            Question.id == question_id).one_or_none()
        if (questionToDelete is None):
            abort(404)

        try:
            questionToDelete.delete()
            return jsonify({
                'success': True,
                'question': questionToDelete.id,
                'total_questions': len(Question.query.all())
            })

        except Exception:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        '''
        An endpoint to POST a new question, which will require the question and answer text,
        category, and difficulty score.

        a POST endpoint to get questions based on a search term.
        It should return any questions for whom the search term is a substring of the question.
        '''

        body = request.get_json()

        newQuestion = body.get('question', None)
        newAnswer = body.get('answer', None)
        newDifficulty = body.get('difficulty', None)
        newCategory = body.get('category', None)
        searchTerm = body.get('searchTerm', None)

        try:
            if searchTerm:  # handles search
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike('%{}%'.format(search_term)))
                currentQuestions = paginate(request, selection)

                if (len(currentQuestions) == 0):
                    abort(404)
                else:
                    return jsonify({
                        'questions': currentQuestions,
                        'total_questions': len(Question.query.all()),
                        'current_category': [(question['category'])
                                             for question in currentQuestions]
                    })
            else:  # handles creation of new question
                question = Question(question=newQuestion,
                                    answer=newAnswer,
                                    difficulty=newDifficulty,
                                    category=newCategory)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                questions = paginate(request, selection)

                return jsonify({
                    'success': True,
                    'questions': questions,
                    'created': question.id,
                    'total_questions': len(Question.query.all())
                })

        except Exception:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json(force=True)
        search = body.get('searchTerm', None)

        try:
            if search is not None:
                questions = Question.query.order_by(Question.id)\
                    .filter(Question.question.ilike('%{}%'.format(search)))
                current_questions = paginate(request, questions)

                if len(questions.all()) != 0:
                    return jsonify({
                        'success': True,
                        'questions': current_questions,
                        'total_questions': len(questions.all())
                    })
            abort(404)
        except Exception as ex:
            print(2, ex)
            abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_categories(category_id):
        '''
        A GET endpoint to get questions based on category.
        '''
        currentCategory = Category.query.filter(
            Category.id == category_id).one_or_none()
        if (currentCategory is None):
            abort(404)

        selection = Question.query.filter(
            Question.category == category_id).all()
        currentQuestions = paginate(request, selection)
        if (len(currentQuestions) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'questions': currentQuestions,
            'total_questions': len(Question.query.all()),
            'current_category': currentCategory.format()
        })

    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        '''
        A POST endpoint to get questions to play the quiz. takes category and previous question parameters
        returns a random questions within the given category, if provided, and that is not one of the previous questions.
        '''
        body = request.get_json()
        id = body['quiz_category']['id']
        previousQuestions = body['previous_questions']
#         category = body.get('quiz_category', None)
#        i changes the entire previous implementations entirely as it was
#        going to be a mess to fix because of all the nested if statements
        try:
            if id == 0:  # id is 0 in case of all is chosen
                questions = Question.query.all()
                randomQuestion = random.choice(questions)

                quizData = {
                    'id': randomQuestion.id,
                    'question': randomQuestion.question,
                    'answer': randomQuestion.answer,
                    'category': randomQuestion.category,
                    'difficulty': randomQuestion.difficulty
                }

                return jsonify({
                    "question": quizData,
                    "previousQuestions": []
                })

            else:
                questions = Question.query.filter(
                    Question.category == id,
                    ~Question.id.in_(previousQuestions)).all()
                randomQuestion = random.choice(questions)

                quizData = {
                    'id': randomQuestion.id,
                    'question': randomQuestion.question,
                    'answer': randomQuestion.answer,
                    'category': randomQuestion.category,
                    'difficulty': randomQuestion.difficulty}

                return jsonify({
                    "question": quizData,
                    "previousQuestions": []})
        except BaseException:
            abort(422)

    @app.errorhandler(422)
    def unprocessable_error_handler(error):
        '''
        Error handler for status code 422.
        '''
        return jsonify({
            'success': False,
            'message': 'Unprocessable'
        }), 422

    @app.errorhandler(404)
    def resource_not_found_error_handler(error):
        '''
        Error handler for status code 404.
        '''
        return jsonify({
            'success': False,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(400)
    def bad_request_error_handler(error):
        '''
        Error handler for status code 400.
        '''
        return jsonify({
            'success': False,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(405)
    def method_not_allowed_error_handler(error):
        '''
        Error handler for status code 405.
        '''
        return jsonify({
            'success': False,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(500)
    def internal_server_error_handler(error):
        '''
        Error handler for status code 500.
        '''
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

    return app
