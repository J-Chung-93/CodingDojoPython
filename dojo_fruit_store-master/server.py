from flask import Flask, render_template, request, redirect
app = Flask(__name__)  

@app.route('/')         
def index():
    return render_template("index.html")

@app.route('/checkout', methods=['POST'])         
def checkout():
    print(request.form)
    fruits={"strawberry" : request.form["strawberry"], "raspberry" : request.form["raspberry"], "apple" : request.form["apple"]}
    print(fruits.keys())
    count=int(request.form["strawberry"]) + int(request.form["raspberry"]) + int(request.form["apple"])
    first_name=request.form["first_name"]
    last_name=request.form["last_name"]
    student_id=request.form["student_id"]
    print("Charging " + first_name, last_name, "for", str(count), "fruits.")
    return render_template("checkout.html", strawberry=int(request.form["strawberry"]), raspberry=int(request.form["raspberry"]), apple=int(request.form["apple"]), count=count, first_name=first_name, last_name=last_name, student_id=student_id, fruits=fruits)

@app.route('/fruits')         
def fruits():
    return render_template("fruits.html")

if __name__=="__main__":   
    app.run(debug=True)    