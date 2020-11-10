import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks_all():
    try:
        drinks = Drink.query.all()
        formatted_drinks = [drink.short() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        })

    except Exception as e:
        abort(404)

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):
    try:
        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks] # formattedDrinks !
        })
    except Exception as e:
        print(e)
        abort(401)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    req = request.get_json()
    # validate data
    title = req.get('title', None)
    recipe = req.get('recipe', None)
    if title is None or title == '' or recipe is None:
        abort(422)

    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except BaseException:
        abort(400)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    req = request.get_json()
    # issue the query
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    # handle not found
    if not drink:
        abort(404)

    try:
        req_title = req.get('title')
        req_recipe = req.get('recipe')
        #update the data
        if req_title:
            drink.title = req_title

        if req_recipe:
            drink.recipe = json.dumps(req['recipe'])

        drink.update()
    except BaseException:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]}), 200

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)

    try:
        drink.delete()
    except BaseException:
        abort(400)

    return jsonify({'success': True, 'delete': id}), 200


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405