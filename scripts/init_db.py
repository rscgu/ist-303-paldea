from my_paldea import db, create_app
from my_paldea.paldea_app.models import Category

app = create_app()

with app.app_context():
    db.create_all()

    # Add default categories if they don't exist
    default_categories = ['Groceries', 'Entertainment', 'Rent', 'Utilities', 'Transportation', 'Dining', 'Healthcare', 'Shopping', 'Salary', 'Freelance', 'Investments']
    for cat_name in default_categories:
        if not Category.query.filter_by(name=cat_name).first():
            category = Category(name=cat_name)
            db.session.add(category)
    db.session.commit()

print("Database initialized with tables and default categories.")
