# 🛒 Supermarket Ops Agent

A conversational AI agent for managing an Indian kirana/supermarket through **Telegram**.

Instead of requiring the store owner to remember fixed commands, the agent understands natural-language requests, identifies the required operation, calls the appropriate backend tool, and returns a natural-language response.

## 🚀 Project Overview

The Supermarket Ops Agent allows a store owner to perform common supermarket operations through a Telegram chat.

For example, instead of typing:

```text
check Maggi
```

the user can simply ask:

```text
How much Maggi do we have?
```

The AI understands the request, identifies the `get_stock` operation, retrieves the actual stock from PostgreSQL, and generates a natural response.

## 🧠 Architecture

```text
                    Telegram
                       │
                       ▼
                    bot.py
                       │
                       ▼
                  AI Agent
                       │
                       ▼
                Ollama / Llama 3.2
                       │
                 Tool Selection
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   Inventory       Checkout         Khata
     Tools           Tool            Tools
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                  PostgreSQL
                       │
                       ▼
              Natural-language
                   response
```

## ✨ Features

### 📦 Inventory Management

The agent can:

* Check product stock
* Find products with low stock
* Receive new stock

Examples:

```text
How much Maggi do we have?
```

```text
Are any products running low?
```

```text
We received 10 Maggi packets
```

### 🧾 Checkout

The agent can process customer purchases.

Example:

```text
Ramesh bought 2 Maggi 70g packets and paid cash
```

The system calculates:

* Subtotal
* CGST
* SGST
* Total tax
* Grand total
* Bill number
* Payment method

### 📒 Khata Management

The agent supports customer credit management.

Examples:

```text
Ramesh bought items on credit worth 500
```

```text
How much does Ramesh owe?
```

```text
Ramesh paid 100
```

The system maintains the customer's outstanding balance.

## 🛠️ AI Tools

The agent uses backend tools to perform real supermarket operations.

```text
get_stock
get_low_stock
receive_stock
checkout
add_credit
get_balance
record_payment
```

The AI does not invent inventory or customer information.

It identifies the required operation and calls the corresponding backend function, which retrieves or modifies the actual PostgreSQL data.

## 💻 Technologies Used

* Python
* Telegram Bot API
* `python-telegram-bot`
* Ollama
* Llama 3.2 3B
* PostgreSQL
* SQLAlchemy
* Alembic
* Pydantic
* Python-dotenv

## 📁 Project Structure

```text
supermarket_ops_agent/
│
├── app/
│   ├── agent/
│   │   └── agent.py
│   │
│   ├── tools/
│   │   ├── inventory.py
│   │   ├── checkout.py
│   │   └── khata.py
│   │
│   ├── database.py
│   └── models.py
│
├── alembic/
│   └── versions/
│
├── bot.py
├── create_tables.py
├── alembic.ini
├── test_agent.py
├── test_checkout.py
├── test_inventory.py
├── test_khata.py
├── test_low_stock.py
├── test_receive_stock.py
├── .gitignore
└── README.md
```

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd supermarket_ops_agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not present, install the required packages:

```bash
pip install python-telegram-bot sqlalchemy psycopg2-binary python-dotenv ollama
```

### 4. Configure environment variables

Create a `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=your_postgresql_database_url
```

Do **not** upload `.env` to GitHub.

## 🤖 Ollama Setup

Install Ollama and download the model:

```bash
ollama pull llama3.2:3b
```

Check the installed model:

```bash
ollama list
```

The project uses:

```text
llama3.2:3b
```

## 🗄️ Database

The project uses PostgreSQL for storing supermarket data such as:

* Products
* Stock quantities
* Prices
* Reorder levels
* Customers
* Khata balances
* Bills
* Payments

Database migrations are managed using Alembic.

## ▶️ Run the Telegram Bot

Make sure Ollama is running and the required environment variables are configured.

Then run:

```powershell
python bot.py
```

You should see:

```text
🤖 Telegram AI Supermarket Agent is running...
```

Open Telegram and send a message to your bot.

## 💬 Example Conversations

### Inventory

**Store Owner:**

```text
How much Maggi do we have?
```

**Agent:**

```text
We have 106 packets of Maggi 70g in stock.
```

### Low Stock

**Store Owner:**

```text
Are any products running low?
```

**Agent:**

```text
We don't have any products currently running low.
```

### Receiving Stock

**Store Owner:**

```text
We received 10 Maggi packets
```

The agent identifies the receiving-stock operation and updates the database.

### Checkout

**Store Owner:**

```text
Ramesh bought 2 Maggi 70g packets and paid cash
```

The agent processes the purchase and generates the bill.

### Khata

**Store Owner:**

```text
How much does Ramesh owe?
```

The agent retrieves Ramesh's current outstanding balance.

## 🔐 Security

Sensitive configuration is stored in `.env`.

The following files should not be committed to GitHub:

```text
.env
venv/
__pycache__/
*.pyc
```

Never expose API keys, Telegram bot tokens, database passwords, or other credentials in source code.

## 🎯 Assignment Goal

The project demonstrates the concept of:

> **"An agent, not a menu."**

Instead of forcing the store owner to select predefined commands, the system allows natural-language interaction.

The AI interprets the user's request, selects the appropriate operation, executes the backend tool, accesses the real database when required, and produces a natural-language response.


