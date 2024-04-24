import json, os
from hashlib import sha256
from flask import Flask, request, jsonify

# Function responsible for encrypt data confidential input
def crypt(data):
  return sha256(data.encode()).hexdigest()

path_db = os.path.join(os.getcwd(), "db.json")
if(not os.path.exists(path_db)):
  with open(path_db, "w") as file:
    file.write('{"logins": []}')

# responsible for verify if the code was started directly
if __name__ == '__main__':
  app = Flask(__name__)

# Root of routes for verify if as API is online
@app.route('/')
def homepage():
  return "API Online"

# Route responsible for register new users
@app.route('/register', methods=["POST"])
def register():
  try:
    information = request.get_json()
    information["password"] = crypt(information["password"])
    response = {"status": 200, "message": "success"}
    with open('db.json', 'r+') as file:
      json_string = file.read()
      data = json.loads(json_string)
      data["logins"].append(information)
      file.seek(0)
      file.write(json.dumps(data))
      file.truncate()
  except KeyError:
    response = {"status": 400, "message": "Bad request. Missing required fields."}
  except Exception as e:
    response = {"status": 500, "message": "Internal server error. Please try again later."}
  return jsonify(response)

# Route responsible for a check if emails already exists
@app.route('/register/<string:mail>', methods=["GET"])
def verify_existence_mail(mail):
  try:
    response = {"status": 200, "message": "E-mail avaible"}
    with open('db.json', 'r+') as file:
      json_string = file.read()
      data = json.loads(json_string)
      for i in data['logins']:
        if i['mail'] == mail:
          response = {"status": 409, "message": "E-mail already"}
          break
  except Exception as e:
    response = {"status": 500, "message": "Internal server error. Please try again later."}
  return jsonify(response)

# Route responsible for a check emails and passwords for login
@app.route('/login', methods=["POST"])
def login():
  try:
    response = {"status": 404, "message": "Incorrect user or password "}
    login = request.get_json()
    login["password"] = crypt(login["password"])
    with open('db.json', 'r') as file:
      json_string = file.read()
      data = json.loads(json_string)
      for logins in data["logins"]:
        if logins["mail"] == login["mail"] and logins["password"] == login["password"]:
          response = {"status": 200, "message": "success"}
          break
  except Exception as e:
    response = {"status": 500, "message": "Internal server error. Please try again later."}
  return jsonify(response)

# more funcionalities will be added in updates futures
app.run(host='0.0.0.0')
