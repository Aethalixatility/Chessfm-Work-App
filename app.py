from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def dashboard():
    data = {
        "total_lessons": 12,
        "completed": 9,
        "cancelled": 3,
        "alerts": [
            "Student John hasn't paid",
            "2 lessons need rescheduling",
            "Teacher unavailable tomorrow"
        ]
    }
    return render_template("dashboard.html", data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
