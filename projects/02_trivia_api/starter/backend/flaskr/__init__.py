import json
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app)

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorizations")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, DELETE")
        return response

    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''

    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        categories_list = {category.id: category.type for category in categories}
        return jsonify({'categories': categories_list})

    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
  
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''

    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, int)
        questions = Question.query.paginate(page, 10, False)
        list_questions = [question.format() for question in questions.items]
        if len(list_questions) == 0:
            abort(404)
        categories = Category.query.all()
        categories_list = {}
        current_categories = [current_category.category for current_category in questions.items]
        for category in categories:
            categories_list[category.id] = category.type

        return jsonify({
            'questions': list_questions,
            'page': questions.page,
            'total_questions': questions.total,
            'categories': categories_list,
            'current_category': current_categories
        })

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
  
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        question = Question.query.get(question_id)
        if question:
            question.delete()
            return jsonify({
                "success": True,
                "delete": question.id
            })
        else:
            abort(422)

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
  
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''

    @app.route('/questions', methods=['POST'])
    def create_question():
        data = request.json
        if data is None:
            return abort(400)
        search = data.get('searchTerm')
        if search:
            questions = Question.query.filter(Question.question.ilike("%{}%".format(search))).all()
            list_questions = [question.format() for question in questions]
            current_categories = [current_category.category for current_category in questions]
            return jsonify({
                "questions": list_questions,
                "current_category": current_categories,
                "total_questions": len(questions)
            })
        else:
            try:
                question = Question(
                    question=data['question'],
                    answer=data['answer'],
                    difficulty=data['difficulty'],
                    category=data['category']
                )
                question.insert()
                return jsonify({
                    "success": True,
                    "created": question.id
                })
            except:
                abort(422)

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
  
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
  
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        questions = Question.query.filter_by(category=category_id).paginate()
        current_categories = [current_category.category for current_category in questions.items]
        questions_list = [question.format() for question in questions.items]
        return jsonify({
            "questions": questions_list,
            "total_questions": questions.total,
            "current_category": current_categories
        })

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
  
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    @app.route('/quizzes', methods=['POST'])
    def quizzing():
        res = request.json
        if res is None:
            return abort(400)
        quiz_category = res['quiz_category']
        questions = Question.query.filter_by(category=quiz_category['id']).all() if quiz_category['id']\
            else Question.query.all()
        random.shuffle(questions)
        for question in questions:
            for previous_question in res['previous_questions']:
                if previous_question == question.id:
                    break
            else:
                return jsonify({
                    "question": {
                        "id": question.id,
                        "question": question.question,
                        "answer": question.answer,
                        "difficulty": question.difficulty,
                        "category": question.category
                    }
                })
        else:
            return jsonify({"question": False})

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''

    # TODO write documentations for api errors that used

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessed(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable entity"
        }), 422

    @app.errorhandler(500)
    def unprocessed(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
