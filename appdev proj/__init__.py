from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime
import shelve
from apscheduler.schedulers.background import BackgroundScheduler
from models import *
from forms import BlogForm, CommentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
app.secret_key = 'your_secret_key'

DB_FILE = "data.db"
calculator = MetricsCalculator(DB_FILE)

with shelve.open(DB_FILE) as db:
    if "users" not in db:
        db["users"] = [
            {"user_id": 1, "name": "Alice", "email": "alice@example.com"},
            {"user_id": 2, "name": "Bob", "email": "bob@example.com"}
        ]
    if "products" not in db:
        db["products"] = [
            {"product_id": 1, "name": "Apples", "price": 1.2, "stock_quantity": 100},
            {"product_id": 2, "name": "Bananas", "price": 0.8, "stock_quantity": 150}
        ]
    if "orders" not in db:
        db["orders"] = [
            {"order_id": 1, "user_id": 1, "total_amount": 50.0, "user_name": "Alice", "date": "2025-01-14"},
            {"order_id": 2, "user_id": 2, "total_amount": 30.0, "user_name": "Bob", "date": "2025-01-13"}
        ]
    if "feedbacks" not in db:
        db["feedbacks"] = [
            {"feedback_id": 1, "user_id": 1, "content": "Great service!", "user_name": "Alice", "date": "2025-01-12"},
            {"feedback_id": 2, "user_id": 2, "content": "Fresh produce!", "user_name": "Bob", "date": "2025-01-11"}
        ]
    if "metric_history" not in db:
        db["metric_history"] = {
            "sales": [],
            "gross profit": [],
            "conversion rate": []
        }


def get_metrics():
    with shelve.open(DB_FILE) as db:
        if "metrics" not in db:
            db["metrics"] = []
        return db["metrics"]


def save_metrics(metrics):
    with shelve.open(DB_FILE) as db:
        db["metrics"] = metrics


def log_metrics_periodically():
    metrics = calculator.get_metrics()
    print(f"Metrics logged at {datetime.now()}: {metrics}")


def get_recent_activity(db_file):
    with shelve.open(db_file) as db:
        orders = db.get("orders", [])
        feedback = db.get("feedbacks", [])
    recent_orders = sorted(orders, key=lambda x: x["date"], reverse=True)[:5]
    recent_feedback = sorted(feedback, key=lambda x: x["date"], reverse=True)[:5]
    return recent_orders, recent_feedback


def get_all_posts():
    with shelve.open(DB_FILE) as db:
        posts = db.get("posts", [])
        return [BlogPost.from_dict(post) for post in posts]


def save_all_posts(posts):
    with shelve.open(DB_FILE) as db:
        db["posts"] = [post.to_dict() for post in posts]


scheduler = BackgroundScheduler()
scheduler.add_job(log_metrics_periodically, "interval", days=1)
scheduler.start()


@app.route("/")
def admin_dashboard():
    metrics = calculator.get_metrics()
    with shelve.open(DB_FILE) as db:
        metric_history = db.get("metric_history", {})

    metrics_with_history = {
        name: {
            "value": value,
            "history": metric_history.get(name.lower(), [])
        }
        for name, value in metrics.items()
    }

    recent_orders, recent_feedback = get_recent_activity(DB_FILE)

    return render_template("admin_dashboard.html", metrics=metrics_with_history, orders=recent_orders, feedback=recent_feedback)


@app.route('/admin/blogs')
def manage_blogs():
    posts = get_all_posts()
    return render_template('blog_list.html', posts=posts)


@app.route('/admin/blogs/add', methods=['GET', 'POST'])
def add_blog():
    form = BlogForm()
    if form.validate_on_submit():
        posts = get_all_posts()
        print('no problem')
        print(posts)
        post_id = max([post.id for post in posts], default=0) + 1
        post = BlogPost(
            post_id=post_id,
            title=form.title.data,
            content=form.content.data,
            author="Admin",
        )
        posts.append(post)
        save_all_posts(posts)
        return redirect(url_for('manage_blogs'))
    else:
        print('pain')
    return render_template('blog_form.html', form=form)


@app.route('/admin/blogs/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_blog(post_id):
    form = BlogForm()
    posts = get_all_posts()
    post = next((p for p in posts if p.id == post_id), None)

    if not post:
        return "Post not found", 404

    if request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        save_all_posts(posts)
        return redirect(url_for('manage_blogs'))

    return render_template('blog_form.html', form=form)


@app.route('/admin/blogs/delete/<int:post_id>')
def delete_blog(post_id):
    posts = get_all_posts()
    posts = [post for post in posts if post.id != post_id]
    save_all_posts(posts)
    return redirect(url_for('manage_blogs'))


@app.route('/blogs')
def view_blogs():
    posts = get_all_posts()
    posts.sort(key=lambda x: datetime.strptime(x.created_at, "%Y-%m-%d %H:%M:%S"), reverse=True)
    return render_template('user_blog_list.html', posts=posts)


@app.route('/blogs/<int:post_id>', methods=['GET', 'POST'])
def view_blog(post_id):
    posts = get_all_posts()
    post = next((p for p in posts if p.id == post_id), None)

    if not post:
        return "Post not found", 404

    form = CommentForm()
    if form.validate_on_submit():
        if form.validate_on_submit():
            new_comment = Comment(author=form.author.data, content=form.content.data)
            post.add_comment(new_comment)
            save_all_posts(posts)
            return redirect(url_for('view_blog', post_id=post_id))

    return render_template('user_blog_detail.html', post=post, form=form)


if __name__ == "__main__":
    app.run(debug=True)
