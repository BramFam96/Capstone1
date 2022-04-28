import os

from flask import Flask, render_template, request, flash, redirect, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, UserEditForm, SearchForm
from models import db, connect_db, User, Shoe
from api.calls import *

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///sneaker_head'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)
######
# Set-up
# Set user for each page
@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

#Get brand and gender choices 
@app.before_request
def add_brands_g():
    '''If session does not already have it, query the api for a brands'''
    if 'brands' in session:
        g.brands = session['brands']
    else:
        session['brands'] = get_brands()
        g.brands = session['brands']

@app.before_request
def add_genders_to_g():
    '''If seesion does not already have it, query api for genders'''
    if 'genders' in session:
        g.genders = session['genders']    
    else:
        session['genders'] = get_genders()
        g.genders = session['genders']

# Log-in/Log-out/Sign-up
def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    if not g.user:
        flash('Not logged in')
        return redirect('/')
        
    do_logout()
    flash(f'Goodbye {g.user.username}')
    return redirect('/login')
        
#############################################################################
# Home Route:
@app.route('/')
def homepage():
    """Homepage:
    Shows list of brand and gender choices
    Brand buttons
    """

    brands = g.brands
    return render_template('home.html', brands = brands)



##############################################################################
# Shoes
def format_data(shoe):
    return {
            'id':shoe['id'],
            'brand':shoe['brand'].title(),
            'colorway': shoe['colorway'],
            'gender': shoe['gender'].title(),
            'name': shoe['name'],
            'year': shoe['year'],
            'release_date': shoe['releaseDate'],
            'retail_price': shoe['retailPrice'],
            'style':shoe['shoe'],
            'title':shoe['title'],
            'img_original':shoe['media']['imageUrl'],
            'img_small': shoe['media']['smallImageUrl']
            }  
def save_new_shoes(shoe_list):
    '''Checks if shoe exists in db, saves new shoes'''
    saved_shoes = Shoe.query.all()
    saved_ids = [shoe.id for shoe in saved_shoes]
    new_shoes = []
    for shoe in shoe_list:
        if shoe['id'] not in saved_ids:
            new_shoes.append(Shoe(**shoe))
    if len(new_shoes) > 0:
        db.session.add_all(new_shoes)
        db.session.commit()
        
def config_shoe_data(shoe_list):
    '''serializes shoe data, checks for duplicates in db, saves new shoe data'''
    
    shoes = [format_data(shoe) for shoe in shoe_list]
    save_new_shoes(shoes)

    return shoes
########################################################################
# Shoe routes

# View all shoes
@app.route('/shoes', methods=["GET"])
def show_all_shoes():
    """Show a list of shoes."""
    shoes= get_sneakers()
    s = config_shoe_data(shoes)
    return render_template('shoes/list.html', shoes=s)

# View brands
@app.route('/search/<shoe_brand>')
def show_shoe_brand(shoe_brand):
    '''Show a list of shoes by brand'''
    
    shoes = get_sneakers({'brand':shoe_brand})
    s = config_shoe_data(shoes)
    return render_template('shoes/list.html', title = shoe_brand, shoes=s)

#  show a shoe
@app.route('/shoes/<shoe_id>', methods=["GET"])
def show_shoe(shoe_id):
    """Show a shoe profile."""
    s = Shoe.query.get(shoe_id)
    if not s:
        shoe_data = get_sneaker_by_id(shoe_id)
        s = config_shoe_data(shoe_data)
        return s
    recommended = get_sneakers({'brand':s.brand, 'page':1})
    formatted_recs = config_shoe_data(recommended)
    return render_template('shoes/detail.html', shoe=s, rec=formatted_recs)

@app.route('/shoes/<shoe_id>/like', methods=['POST'])
def toggle_likes(shoe_id):
    """Toggle a liked shoe for the currently-logged-in user."""

    if not g.user:
        flash("You must log in to favorite shoes.", "danger")
        return redirect("login")

    clicked_shoe = Shoe.query.get(shoe_id)
    liked_shoes = g.user.liked_shoes

    if clicked_shoe in liked_shoes:
        g.user.liked_shoes = [like for like in liked_shoes if like != clicked_shoe]
    else:
        g.user.liked_shoes.append(clicked_shoe)

    db.session.commit()
    return redirect(f'shoes/{shoe_id}')

##############################################################################
# User routes:
    # View Profile
@app.route('/users/<int:user_id>')
def user_profile(user_id):
    """Shows user profile."""
    user = User.query.get_or_404(user_id)

    return render_template('users/profile.html', user=user)

    #  View likes
@app.route('/users/<int:user_id>/likes')
def show_likes(user_id):
        user = User.query.get_or_404(user_id)
        return render_template('users/likes.html', user=user)
###########################################################################

# Edit user profile
@app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def edit_profile(user_id):
    """Update profile for current user."""
# Check for no global user:
    if not g.user:
        flash('Access denied, please log in', 'danger')
        return redirect('/login')
# Check for global user on wrong profile:
    if g.user.id != user_id:
        flash('Access denied, redirecting to your profile', 'danger')
        return redirect(f'/user/{g.user.id}')

    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)

# Check for invalid form -> get route  
    if not form.validate_on_submit():
        return render_template('users/edit.html', form = form, user= user)
    # Check for bad auth
    if not User.authenticate(user.username, form.password.data):
        flash('Invalid password', 'danger')
        return render_template('users/edit.html', form=form, user = user)
    # If everything passes we update user:
    
    user.username = form.username.data
    user.email = form.email.data
    user.image_url = form.image_url.data or "/static/images/default-pic.png"
    
    db.session.commit()    
    return redirect(f'/users/{user.id}')


# Delete user profile
@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access denied.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")



#  Turn off all caching:
@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
