from flask import Flask, render_template, jsonify
from threading import Thread
from drowsiness_detection import DrowsinessDetection

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/templates')

# Global status variable for frontend
status_data = {"status": "Normal", "latitude": None, "longitude": None}

# Update status from the drowsiness detection system
def update_status(new_status, latitude, longitude):
    global status_data
    status_data["status"] = new_status
    status_data["latitude"] = latitude
    status_data["longitude"] = longitude

# Route for serving the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to get the latest status
@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(status_data)

# Run the drowsiness detection system in a separate thread
def run_drowsiness_detection():
    detection_system = DrowsinessDetection(update_status)
    detection_system.run()

if __name__ == "__main__":
    # Start the detection system in a background thread
    thread = Thread(target=run_drowsiness_detection)
    thread.daemon = True
    thread.start()

    # Start the Flask app
    app.run(debug=True)
