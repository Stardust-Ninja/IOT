from flask import Flask, request, jsonify

app = Flask(__name__)
THRESHOLD = 25.0

@app.route("/temperature", methods=["POST"])
def temperature():
    data = request.json
    temp = data.get("temperature")
    print(f"Got: {temp}C from {request.remote_addr}")
    
    warning = temp > THRESHOLD
    return jsonify({"warning": warning})  # <-- MUST return JSON

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)