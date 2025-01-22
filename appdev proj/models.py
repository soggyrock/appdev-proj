from typing import List, Dict, Optional
from datetime import datetime
import shelve


# CORE CLASSES
class User:
    def __init__(self, user_id, name, email, created_at=None, is_admin: bool = False):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.created_at = created_at or datetime.now()
        self.is_admin = is_admin


class Product:
    def __init__(self, product_id, name, price, stock_quantity):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock_quantity = stock_quantity


class Order:
    def __init__(self, order_id, user_id, total_amount, order_date=None):
        self.order_id = order_id
        self.user_id = user_id
        self.total_amount = total_amount
        self.order_date = order_date or datetime.now()


class Feedback:
    def __init__(self, feedback_id, user_id, content, created_at=None):
        self.feedback_id = feedback_id
        self.user_id = user_id
        self.content = content
        self.created_at = created_at or datetime.now()


# MAIN CLASSES
class MetricsCalculator:
    def __init__(self, db_file):
        self.db_file = db_file

    def fetch_data(self):
        with shelve.open(self.db_file) as db:
            users = db.get("users", [])
            products = db.get("products", [])
            orders = db.get("orders", [])
            feedbacks = db.get("feedbacks", [])
        return users, products, orders, feedbacks

    def calculate_sales(self, orders):
        return sum(order["total_amount"] for order in orders)

    def calculate_average_order_value(self, orders):
        if len(orders) == 0:
            return 0
        return self.calculate_sales(orders) / len(orders)

    def calculate_inventory_levels(self, products):
        return sum(product["stock_quantity"] for product in products)

    def calculate_gross_profit(self, orders):
        return self.calculate_sales(orders) * 0.3  # Assuming 30% profit margin

    def calculate_conversion_rate(self, users, orders):
        if len(users) == 0:
            return 0
        return (len(orders) / len(users)) * 100

    def log_metric_history(self, metric_name, value):
        with shelve.open(self.db_file) as db:
            history = db["metric_history"]
            if metric_name not in history:
                history[metric_name] = []
            history[metric_name].append({"date": datetime.now().strftime("%Y-%m-%d"), "value": value})
            db["metric_history"] = history

    def get_metrics(self):
        users, products, orders, feedbacks = self.fetch_data()
        sales = self.calculate_sales(orders)
        gross_profit = self.calculate_gross_profit(orders)
        conversion_rate = self.calculate_conversion_rate(users, orders)

        self.log_metric_history("sales", sales)
        self.log_metric_history("gross profit", gross_profit)
        self.log_metric_history("conversion rate", conversion_rate)

        return {
            "Sales": sales,
            "Average Order Value": self.calculate_average_order_value(orders),
            "Inventory Levels": self.calculate_inventory_levels(products),
            "Gross Profit": gross_profit,
            "Conversion Rate": conversion_rate,
        }


class BlogPost:
    def __init__(self, post_id, title, content, author, created_at=None, comments=None):
        self.id = post_id
        self.title = title
        self.content = content
        self.author = author
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.comments = comments or []  # List of Comment objects

    def add_comment(self, comment):
        self.comments.append(comment)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "created_at": self.created_at,
            "comments": [comment.to_dict() for comment in self.comments],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            post_id=data["id"],
            title=data["title"],
            content=data["content"],
            author=data["author"],
            created_at=data["created_at"],
            comments=[Comment.from_dict(c) for c in data.get("comments", [])],
        )


class Comment:
    def __init__(self, author, content, created_at=None):
        self.author = author
        self.content = content
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "author": self.author,
            "content": self.content,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            author=data["author"],
            content=data["content"],
            created_at=data["created_at"],
        )

