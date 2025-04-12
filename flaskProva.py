from flask import Flask, jsonify
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Sample data
predictions = [
    {'name': 'Alice', 'prediction': 'accept', 'result': 'accept', 'outcome': 'active'},
    {'name': 'Bob', 'prediction': 'reject', 'result': 'accept', 'outcome': 'gameover'},
    {'name': 'Charlie', 'prediction': 'accept', 'result': 'accept', 'outcome': 'active'},
    {'name': 'David', 'prediction': 'reject', 'result': 'reject', 'outcome': 'active'},
    {'name': 'Eve', 'prediction': 'accept', 'result': 'accept', 'outcome': 'active'},
    {'name': 'Frank', 'prediction': 'reject', 'result': 'reject', 'outcome': 'active'},
    {'name': 'Grace', 'prediction': 'accept', 'result': 'accept', 'outcome': 'active'},
    {'name': 'Henry', 'prediction': 'reject', 'result': 'accept', 'outcome': 'gameover'},
    {'name': 'Ivy', 'prediction': 'accept', 'result': 'accept', 'outcome': 'active'},
    {'name': 'Jack', 'prediction': 'reject', 'result': 'reject', 'outcome': 'active'},
    {'name': 'Kelly', 'prediction': 'accept', 'result': 'accept', 'outcome': 'active'},
    {'name': 'Liam', 'prediction': 'reject', 'result': 'accept', 'outcome': 'gameover'},
    {'name': 'Mia', 'prediction': 'accept', 'result': 'accept', 'outcome': 'active'},
    {'name': 'Noah', 'prediction': 'reject', 'result': 'reject', 'outcome': 'active'},
    {'name': 'Olivia', 'prediction': 'accept', 'result': 'accept', 'outcome': 'active'},
    {'name': 'Peter', 'prediction': 'reject', 'result': 'reject', 'outcome': 'active'},
    {'name': 'Quinn', 'prediction': 'accept', 'result': 'accept', 'outcome': 'active'},
    {'name': 'Ryan', 'prediction': 'reject', 'result': 'accept', 'outcome': 'gameover'},
    {'name': 'Sophia', 'prediction': 'accept', 'result': 'accept', 'outcome': 'active'},
    {'name': 'Thomas', 'prediction': 'reject', 'result': 'reject', 'outcome': 'active'},
    {'name': 'Ursula', 'prediction': 'accept', 'result': 'accept', 'outcome': 'active'},
]

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    # Randomly select one prediction from the list to simulate real-time updates
    randomPred = random.choice(predictions)
    print(randomPred)
    return jsonify(randomPred)

if __name__ == '__main__':
    app.run()

