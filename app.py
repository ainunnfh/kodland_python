from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import locale
import requests


app = Flask(__name__)
app.secret_key = "rahasia123"

# Atur lokal ke Bahasa Indonesia untuk nama hari
try:
    locale.setlocale(locale.LC_TIME, "id_ID.utf8")
except:
    locale.setlocale(locale.LC_TIME, "id_ID")

API_KEY = "8aba1313abb7e93b5bc1162c733b2d2f"

# Dummy user (contoh login)
USER = {
    "username": "admin",
    "password": "qwerty"
}

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == USER["username"] and password == USER["password"]:
            session["user"] = username
            flash("Login berhasil!", "success")
            return redirect(url_for("index"))
        else:
            flash("Username atau password salah!", "danger")
            return redirect(url_for("login"))
    
    return render_template("login.html")

# 🔹 Halaman beranda + cuaca
@app.route("/", methods=["GET", "POST"])
def index():
    # Jika belum login, kembalikan ke halaman login
    if "user" not in session:
        return redirect(url_for("login"))

    weather_data = None
    city = ""


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
                date_str = date_obj.strftime("%d %B %Y")

                # Ambil suhu siang & malam
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
            print(f"Jumlah data diterima dari API: {len(forecast_list)}")

    return render_template("index.html", city=city, weather_data=weather_data)


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Kamu sudah logout.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
