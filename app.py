from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import locale
import requests
from flask import Flask
from models import db, Users  # <--- ambil db dan model dari models.py

app = Flask(__name__)
app.secret_key = "rahasia123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Hubungkan app ke database
db.init_app(app)


# Atur lokal ke Bahasa Indonesia untuk nama hari
try:
    locale.setlocale(locale.LC_TIME, "id_ID.utf8")
except:
    locale.setlocale(locale.LC_TIME, "id_ID")

quiz_data = [
    {
        "question": "Library Python mana yang paling umum digunakan untuk membangun model pembelajaran mesin (Machine Learning)?",
        "options": ["Flask", "Tensor Flow", "NumPy", "Beautiful Soup"],
        "answer": "TensorFlow"
    },
    {
        "question": "Dalam konteks Natural Language Processing (NLP), library Python apa yang digunakan untuk memproses teks seperti tokenisasi dan stemming?",
        "options": ["NLTK", "Open CV", "PyTorch", "Matplotlib"],
        "answer": "NLTK"
    },
    {
        "question": "Library Python apa yang digunakan untuk komputasi numerik dan operasi pada array?",
        "options": ["NumPy", "Seaborn", "Django", "Flask"],
        "answer": "NumPy"
    }
]

API_KEY = "8aba1313abb7e93b5bc1162c733b2d2f"
users = {}
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nick_name = request.form["nick_name"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not nick_name or not password or not confirm_password:
            flash("Semua field harus diisi!", "error")
        elif password != confirm_password:
            flash("Password dan konfirmasi tidak sama!", "error")
        else:
            # Cek apakah user sudah ada di database
            existing_user = Users.query.filter_by(nick_name=nick_name).first()
            if existing_user:
                flash("Nama pengguna sudah terdaftar!", "error")
            else:
                # Simpan user baru ke database
                new_user = Users(nick_name=nick_name, password=password)
                db.session.add(new_user)
                db.session.commit()
                flash(f"Registrasi berhasil untuk {nick_name}! Silakan login.", "success")
                return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = Users.query.filter_by(nick_name=username).first()

        if user and user.password == password:
            session["user"] = username
            flash("Login berhasil!", "success")
            return redirect(url_for("index"))
        else:
            flash("Username atau password salah!", "danger")
            return render_template("login.html")

    return render_template("login.html")



# 🔹 Halaman beranda + cuaca
@app.route("/", methods=["GET", "POST"])
def index():
    # Jika belum login, kembalikan ke halaman login
    if "user" not in session:
        return redirect(url_for("login"))
    
    weather_data = None
    city = ""
    username = session.get("user")


    if request.method == "POST":
        city = request.form["city"]
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=id"

        response = requests.get(url)
        data = response.json()

        if data.get("cod") == "200":
            weather_data = []
            forecast_list = data.get("list", [])
            # Ambil data tiap 24 jam
            for i in range(0, min(len(forecast_list), 24 * 3), 8):
                day_data = data["list"][i]
                date_obj = datetime.fromtimestamp(day_data["dt"])
                day_name = date_obj.strftime("%A")
                date_str = date_obj.strftime("%d-%m-%Y")

                day_temp = day_data["main"]["temp_max"]
                night_temp = day_data["main"]["temp_min"]

                weather_data.append({
                    "day": day_name,
                    "date": date_str,
                    "day_temp": round(day_temp, 1),
                    "night_temp": round(night_temp, 1),
                    "description": day_data["weather"][0]["description"].capitalize(),
                    "icon": day_data["weather"][0]["icon"],
                })

                if len(weather_data) == 3:
                    break
        else:
            weather_data = None
            flash(f"Kota '{city}' tidak ditemukan!", "danger")

    return render_template("index.html", city=city, weather_data=weather_data, username=username)
    

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        user_answers = {}
        for i, q in enumerate(quiz_data):
            user_answers[i] = request.form.get(f"question-{i}")
        
        # Hitung jumlah jawaban benar
        score = 0
        for i, q in enumerate(quiz_data):
            if user_answers.get(i) == q["answer"]:
                score += 1
        
        flash(f"Kamu menjawab {score} dari {len(quiz_data)} pertanyaan dengan benar!", "success")
        return redirect(url_for("quiz"))

    return render_template("quiz.html", quiz_data=quiz_data)

@app.route('/ranking-quiz')
def ranking_quiz():
    # contoh data ranking quiz
    rankings = [
        {"name": "Ainun", "score": 95},
        {"name": "Budi", "score": 88},
        {"name": "Citra", "score": 82},
        {"name": "Dewi", "score": 75},
    ]
    # urutkan berdasarkan score descending
    rankings = sorted(rankings, key=lambda x: x["score"], reverse=True)
    return render_template("ranking-quiz.html", rankings=rankings)


@app.route("/logout")
def logout():
    session.pop('user', None)
    flash("Anda telah logout.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
