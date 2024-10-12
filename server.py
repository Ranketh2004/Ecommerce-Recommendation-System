from flask import Flask, render_template, request, redirect, url_for, flash, session
import pickle
from models.content_based import content_based_recommendation
from models.userbased import userbased_recommendation
from models.new_userbased import new_user_recommendation
from models.ratingbased import rating_based_recommendations
from pymongo import MongoClient

app = Flask(__name__)

# Load dataset
with open('models/data.pkl', 'rb') as file:
    data = pickle.load(file)

# DB configuration
app.secret_key = "testing"  # Ensure that the secret key is set for session management

# Connect to MongoDB database
def MongoDB():
    client = MongoClient("mongodb+srv://sadu:sadu123@irwadb.acyam.mongodb.net/?retryWrites=true&w=majority&appName=irwaDb")
    db = client.get_database('total_records')
    register_collection = db.register
    old_users_collection = db.old_users
    return register_collection, old_users_collection

register_collection, old_users_collection = MongoDB()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        categories = request.form.getlist('categories')  # Collects multiple selected categories
        brands = request.form.getlist('brands')  # Collects multiple selected brands

        # Check if the email already exists
        user_found = register_collection.find_one({"email": email})
        if user_found:
            flash('Email address already exists. Please try logging in.', 'warning')
            return redirect(url_for('signup'))

        # Insert user details into MongoDB
        user_data = {
            "name": name,
            "email": email,
            "password": password,
            "categories": categories,
            "brands": brands
        }
        register_collection.insert_one(user_data)

        flash('Successfully registered! You can now log in.', 'success')
        return redirect(url_for('signin'))

    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print(f"Trying to log in with email: {email}")  # Debug print

        # Check if the user exists in the old_users collection
        old_user = old_users_collection.find_one({"email": email})
        print(f"Old user data: {old_user}")  # Debug print

        if old_user and old_user['password'] == password:
            # Store the old user's ID and username in the session
            session['user_id'] = old_user['userId']
            session['username'] = old_user['name']
            session['is_new_user'] = False  # Mark as an old user
            flash(f'Welcome back, {old_user["name"]}!', 'success')
            return redirect(url_for('home'))

        # Check if the user exists in the register collection (new users)
        user = register_collection.find_one({"email": email})
        print(f"New user data: {user}")  # Debug print

        if user and user['password'] == password:
            # Store the new user's email as user ID and their name in the session
            session['user_id'] = user['email']  # Use email as user ID for new users
            session['username'] = user['name']
            session['is_new_user'] = True  # Mark as a new user
            flash(f'Welcome, {user["name"]}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('signin.html')


@app.route('/')
def home():
    # Check if the user is logged in and has a username stored in session
    username = session.get('username')
    user_id = session.get('user_id')
    is_new_user = session.get('is_new_user', False)  # Check if it's a new user
    user_recommendations = None
    new_user_recommendations = None  # Variable to store new user recommendations
    trending_products = rating_based_recommendations(data)  # Fetch trending products
    trending_products_list = trending_products.to_dict(orient='records')  # Convert to dictionary

    if user_id:
        if is_new_user:
            # If the user is new, get recommendations based on preferred categories and brands
            print(f"New user detected. Email: {user_id}")  # Debug print
            user = register_collection.find_one({"email": user_id})  # Fetch new user details based on email (user_id)
            print(f"New user data from database: {user}")  # Debug print
            if user:
                preferred_categories = user.get("categories", [])
                preferred_brands = user.get("brands", [])
                print(f"New user's preferred categories: {preferred_categories}")  # Debug print
                print(f"New user's preferred brands: {preferred_brands}")  # Debug print

                new_user_recommendations = new_user_recommendation(
                    df=data,
                    preferred_categories=preferred_categories,
                    preferred_brands=preferred_brands,
                    top=5
                )
                print(f"New user recommendations: {new_user_recommendations}")  # Debug print
                if new_user_recommendations is not None and not new_user_recommendations.empty:
                    new_user_recommendations = new_user_recommendations.to_dict(orient='records')
                else:
                    new_user_recommendations = None
            print(f"New user logged in. Showing recommendations based on categories and brands.")
        else:
            # If it's an old user, get user-based recommendations as before
            print(f"Fetching recommendations for old user ID: {user_id}")  # Debug print
            user_recommendations = userbased_recommendation(data, target_user=user_id, top=5)
            if user_recommendations is not None and not user_recommendations.empty:
                user_recommendations = user_recommendations.to_dict(orient='records')
            else:
                user_recommendations = None

    return render_template('main.html',
                           username=username,
                           user_recommendations=user_recommendations,
                           new_user_recommendations=new_user_recommendations,
                           trending_products=trending_products_list)




@app.route('/content', methods=['POST'])
def contentRecommend():
    item = request.form['item'].strip().lower()  # Strip spaces and convert to lower case
    num = int(request.form['nbr'])  # Number of recommendations to fetch
    
    # Call the updated content-based recommendation function
    recommendation = content_based_recommendation(data, item, num)

    if recommendation is None or recommendation.empty:
        return render_template('main.html', error='Could not fetch recommendations.')
    else:
        recommendations_list = recommendation.to_dict(orient='records')
        return render_template('main.html', recommendation=recommendations_list, username=session.get('username'))


@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('signin'))

if __name__ == "__main__":
    app.run(debug=True)
