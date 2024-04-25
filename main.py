import json, os
from hashlib import sha256
from flask import Flask, request, jsonify


def standartsize_user(user):
  user = user
  user["approved"] = False  # Set approved to false
  user["admin"] = False  #Set admin to false
  user["blocked"] = False  #Set blocked to false
  user["password"] = crypt(user["password"])
  return user
  

# Function responsible for encrypt data confidential input
def crypt(data):
  return sha256(data.encode()).hexdigest()


MAX_ATTEMPTS = 5  # Maximum number of attempts login
app = Flask(__name__)
user_attempts = []

# Verify for existence of the data-base, and create if not exists
path_db = os.path.join(os.getcwd(), "db.json")
if (not os.path.exists(path_db)):
  with open(path_db, "w") as file:
    file.write('{"logins": []}')


# Root of routes for verify if as API is online
@app.route('/')
def homepage():
  return "API Online"


# Route responsible for register new users
@app.route('/register', methods=["POST"])
def register():
  try:
    response = {"status": 202, "message": "Register sent, wait for approval"}
    information = standartsize_user(request.json)

    # Open de json responsible for data-base
    with open('db.json', 'r+') as file:
      json_string = file.read()
      data = json.loads(json_string)

      #Verify if user already exists for the mail
      for logins in data["logins"]:
        if logins["mail"] == information["mail"]:
          response = {"status": 409, "message": "User already registered"}
          return jsonify(response)  # return case mail already exist

      # add new user to the waiting list
      data["logins"].append(information)
      file.seek(0)
      file.write(json.dumps(data))
      file.truncate()

  except KeyError:
    response = {
        "status": 400,
        "message": "Bad request. Missing required fields."
    }

  except Exception as e:
    response = {
        "status": 500,
        "message": "Internal server error. Please try again later."
    }

  return jsonify(response)


# Route responsible for a check emails and passwords for login
@app.route('/login', methods=["POST"])
def login():
  try:
    response = {"status": 404, "message": "User not found"}
    login = request.get_json()
    login["password"] = crypt(login["password"])

    # Open de json responsible for data-base
    with open('db.json', 'r+') as file:
      json_string = file.read()
      data = json.loads(json_string)
      # login validation
      for logins in data["logins"]:
        if logins["mail"] == login["mail"]:  # Checks the credentials of user
          if not logins["blocked"]:
            if logins["password"] == login["password"]:
              for user in user_attempts:
                if user["mail"] == login["mail"]:
                  user_attempts.remove(user) # Remove user from list of attempts case use a correctly password, before of maximum attempts
              if logins["approved"]:  # Checks if the user is approved of admin
                response = {"status": 200, "message": "success"}
                break
              else:
                response = {"status": 403, "message": "User not yet approved"}
                break
            else:
  
              if len(user_attempts) != 0:
                for index, users in enumerate(user_attempts):
                  if login["mail"] == users["mail"]:  # Checks if the user is already in the attempts of login list
                    print(123)
                    if users["attempts"] < MAX_ATTEMPTS:
                      users["attempts"] += 1  # adds attempts case number of attempts is less than the maximum number of attempts
                      response = {"status": 401, "message": "Password incorrect"}
                      print(users["attempts"])
                      break
                    else:
                      # modify for blocked after achieve the maximum number of attempts
                      logins["blocked"] = True
                      response = {"status": 401,"message": "User blocked for too many attempts, contact admin"}
                      file.seek(0)
                      file.write(json.dumps(data))
                      file.truncate()
                      break
                  elif index == (len(users) - 1): # If the user is not in the list of attempts. If the user no first user in the list of attempts
                    user_attempts.append({"mail": login["mail"], "attempts": 1})
                    response = {"status": 401, "message": "Password incorrect"}
              else:# If the user is not in the list of attempts, while it is empty
                user_attempts.append({"mail": login["mail"], "attempts": 1})
                response = {"status": 401, "message": "Password incorrect"}
          else:
            response = {"status": 401, "message": "User blocked for too many attempts, contact admin"}

  except Exception as e:
    response = {
        "status": 500,
        "message": "Internal server error. Please try again later."
    }

  return jsonify(response)


# more funcionalities will be added in updates futures
app.run(host='0.0.0.0')
