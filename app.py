# -*- coding: utf-8 -*-
import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# ----------------------------------------------------------------------
# Database configuration (SQLite)
# ----------------------------------------------------------------------
DATABASE_URL = "sqlite:///./enrique.db"
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    item = Column(String, nullable=False)
    amount = Column(Float, nullable=False)


# Create tables automatically if they do not exist
Base.metadata.create_all(bind=engine)


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def read_root():
    """Render the main page with a form, a table of saved sales and the total."""
    with SessionLocal() as db:
        sales = db.query(Sale).all()
        total = sum(s.amount for s in sales)

    # HTML with inline CSS (responsive)
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enrique Business</title>
        <style>
            body {{font-family:Arial, sans-serif; margin:20px;}}
            h1 {{color:#333;}}
            form {{margin-bottom:20px;}}
            input, button {{padding:8px; margin:4px;}}
            table {{width:100%; border-collapse:collapse;}}
            th, td {{border:1px solid #ddd; padding:8px; text-align:left;}}
            th {{background-color:#f2f2f2;}}
            @media (max-width:600px) {{
                table, thead, tbody, th, td, tr {{display:block;}}
                th {{position:absolute; left:-9999px;}}
                td {{border:none; position:relative; padding-left:50%;}}
                td::before {{
                    position:absolute;
                    left:6px;
                    width:45%;
                    white-space:nowrap;
                }}
                td:nth-of-type(1)::before {{content:"ID";}}
                td:nth-of-type(2)::before {{content:"Item";}}
                td:nth-of-type(3)::before {{content:"Amount";}}
            }}
        </style>
    </head>
    <body>
        <h1>Enrique Business - Sales Tracker</h1>
        <form action="/add" method="post">
            <input type="text" name="item" placeholder="Item name" required>
            <input type="number" step="0.01" name="amount" placeholder="Amount" required>
            <button type="submit">Add Sale</button>
        </form>

        <h2>Sales List</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>Item</th><th>Amount</th></tr>
            </thead>
            <tbody>
    """
    for s in sales:
        html += f"<tr><td>{s.id}</td><td>{s.item}</td><td>{s.amount:.2f}</td></tr>"
    html += f"""
            </tbody>
        </table>
        <h3>Total: ${total:.2f}</h3>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.post("/add")
def add_sale(item: str = Form(...), amount: float = Form(...)):
    """Receive form data, store it in SQLite and redirect back to the main page."""
    with SessionLocal() as db:
        new_sale = Sale(item=item, amount=amount)
        db.add(new_sale)
        db.commit()
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    import os, uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))