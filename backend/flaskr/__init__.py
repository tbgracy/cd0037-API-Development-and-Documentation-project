import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import choice

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)

    def get_paginated_questions(selection, page, item_per_page):
        start = (page - 1) * item_per_page
        end = start + item_per_page
        questions = [question.format() for question in selection]
        if len(questions[start:end]) == 0:
            abort(404, 'This page is empty')
        return questions[start:end]

    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET, POST, PUT, PATCH, OPTIONS")
        return response

    @app.route("/categories")
    def get_categories():
        categories = Category.query.all()
        formated_categories = {}
        for category in categories:
            formated_categories[category.id] = category.type
        return jsonify({
            "success": True,
            "categories": formated_categories,
        })

    @app.route("/questions")
    def get_questions():
        page = request.args.get("page", 1, type=int)

        categories = Category.query.all()
        formated_categories = {}
        for category in categories:
            formated_categories[category.id] = category.type

        all_questions = Question.query.all()

        paginated_questions = get_paginated_questions(
            Question.query.all(), page, QUESTIONS_PER_PAGE)

        return jsonify({
            "success": True,
            "questions": paginated_questions,
            "total_questions": len(all_questions),
            "categories": formated_categories,
        })

    @app.route("/questions/<int:id>", methods=['DELETE'])
    def delete_question(id):
        question = Question.query.get(id)
        if question is None:
            abort(404, "Question not found")
        question.delete()
        return jsonify({
            "success": True,
            "deleted_question": question.id,
        })

    @app.route("/questions", methods=["POST"])
    def add_question():
        data = request.get_json()
        if data is None:
            abort(400, "Missing fields")
        try:
            question = Question(
                question=data['question'],
                answer=data['answer'],
                category=data['category'],
                difficulty=data['difficulty'],
            )
        except:
            abort(400, "Missing fields")
            
        question.insert()

        return jsonify({"success": True})

    @app.route("/search", methods=["POST"])
    def search_question():
        data = request.get_json()
        if data is None:
            abort(400)
        page = request.args.get("page", 1, type=int)
        try:
            search_query = data['searchTerm']
        except:
            abort(400)
        questions = Question.query.filter(
            Question.question.ilike(f"%{search_query}%")).all()
        paginated_questions = get_paginated_questions(
            questions, page, QUESTIONS_PER_PAGE)
        return jsonify({
            "success": True,
            "questions": paginated_questions,
            "total_questions": len(questions),
        })

    @app.route("/categories/<int:id>/questions")
    def get_questions_by_categories(id):
        category = Category.query.get(id)
        questions = Question.query.filter(Question.category == id).all()
        page = request.args.get('page', 1, type=int)
        
        return jsonify({
            "questions": get_paginated_questions(questions, page, QUESTIONS_PER_PAGE),
            "totalQuestions": len(questions),
            "currentCategory": category.type
        })

    @app.route('/quizzes', methods=['POST'])
    def play_trivia():
        request_body = request.get_json()
        if request_body is None:
            abort(400)

        previous_questions_id = request_body['previous_questions']
        category = request_body['quiz_category']

        if category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=category['id']).all()

        selection = []

        for question in questions:
            if question.id not in previous_questions_id:
                selection.append(question.format())

        quizz_question = choice(questions)

        return jsonify({
            'question': {
                'id': quizz_question.id,
                'question': quizz_question.question,
                'answer': quizz_question.answer,
                'difficulty': quizz_question.difficulty,
                'category': category['id'],
            }
        })

    @app.errorhandler(404)
    def not_found(e):
        messages = ["not found"]
        messages.append(e.description)
        return jsonify({
            "error": 404,
            "messages": messages,
        })

    @app.errorhandler(422)
    def unprocessable(e):
        messages = ["unprocessable"]
        messages.append(e.description)
        return jsonify({
            "error": 422,
            "messages": messages,
        })

    @app.errorhandler(500)
    def internal_server_error(e):
        messages = ["internal server error"]
        messages.append(e.description)
        return jsonify({
            "error": 500,
            "messages": messages,
        })

    @app.errorhandler(400)
    def bad_request(e):
        messages = ["bad request"]
        messages.append(e.description)
        return jsonify({
            "error": 400,
            "messages": messages,
        })

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            "error": 405,
            "messages": e.description
        })

    return app
