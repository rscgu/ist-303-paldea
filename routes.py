from flask import render_template, request, redirect, url_for, flash
from app import app

@app.route("/")
def home():
    return redirect(url_for('budget'))

@app.route("/budget", methods=["GET", "POST"])
def budget():
    if request.method == "POST":
        category = request.form.get("category")
        amount = request.form.get("amount")
        flash(f"Budget saved for {category}: ${amount}")
        return redirect(url_for("budget"))
    return render_template("budget.html")