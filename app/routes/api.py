from flask import Blueprint, request, jsonify, session
from app.models import User
from app.db import get_db
import sys
from app.models import User, Post, Comment, Vote

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/users', methods=['POST'])
def signup():
  data = request.get_json()
  db = get_db()

  try:
    # attempt creating a new user
    newUser = User(
      username = data['username'],
      email = data['email'],
      password = data['password']
    )

    db.add(newUser)
    db.commit()
  except:
    print(sys.exc_info()[0])

    # insert failed, so rollback and send error to front end
    db.rollback()
    return jsonify(message = 'Signup failed'), 500
  session.clear()
  session['user_id'] = newUser.id
  session['loggedIn'] = True  
  return jsonify(id = newUser.id)

@bp.route('/users/logout', methods=['POST'])
def logout():
  # remove session variables
  session.clear()
  return '', 204

@bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db()

    try:
        user = db.query(User).filter(User.email == data['email']).one()
    except Exception as e: # Catch specific exceptions
        print(sys.exc_info()[0])
        return jsonify(message='Incorrect credentials'), 400

    if not user.verify_password(data['password']): # Corrected password verification logic
        return jsonify(message='Incorrect credentials'), 400

    # After successful password verification, create the session and send back a valid response
    session.clear()
    session['user_id'] = user.id
    session['loggedIn'] = True
    return jsonify(id=user.id)

@bp.route('/comments', methods=['POST'])
def comment():
    data = request.get_json()
    db = get_db()

    try:
        # create a new comment
        newComment = Comment(
            comment_text=data['comment_text'],
            post_id=data['post_id'],
            user_id=session.get('user_id')
        )

        db.add(newComment)
        db.commit()
        return jsonify(id=newComment.id) # Moved inside the try block
    except Exception as e: # Catch specific exceptions
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message='Comment failed'), 500
    

@bp.route('/posts/upvote', methods=['PUT'])
def upvote():
  data = request.get_json()
  db = get_db()

  try:
    # create a new vote with incoming id and session id
    newVote = Vote(
      post_id = data['post_id'],
      user_id = session.get('user_id')
    )

    db.add(newVote)
    db.commit()
  except:
    print(sys.exc_info()[0])

    db.rollback()
    return jsonify(message = 'Upvote failed'), 500

  return '', 204
