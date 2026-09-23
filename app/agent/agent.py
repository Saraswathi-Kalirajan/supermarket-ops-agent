import json

from ollama import chat

from app.tools.inventory import (
    get_stock,
    get_low_stock,
    receive_stock,
)

from app.tools.checkout import checkout

from app.tools.khata import (
    add_credit,
    get_balance,
    record_payment,
)


# =========================================================
# CONFIGURATION
# =========================================================

MODEL = "llama3.2:3b"


# =========================================================
# TOOL DEFINITIONS
# =========================================================

TOOLS = [

    # =====================================================
    # 1. GET STOCK
    # =====================================================

    {
        "type": "function",
        "function": {
            "name": "get_stock",
            "description": (
                "Check the current stock of a supermarket product. "
                "Use this when the user asks how much of a product "
                "is available, how many items are left, or whether "
                "a product is available."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": (
                            "The supermarket product name, "
                            "for example Maggi."
                        ),
                    }
                },
                "required": ["product_name"],
            },
        },
    },

    # =====================================================
    # 2. GET LOW STOCK
    # =====================================================

    {
        "type": "function",
        "function": {
            "name": "get_low_stock",
            "description": (
                "Check which supermarket products are currently "
                "low in stock. Use this when the user asks which "
                "products are running low, which products need "
                "restocking, or what should be restocked."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },

    # =====================================================
    # 3. RECEIVE STOCK
    # =====================================================

    {
        "type": "function",
        "function": {
            "name": "receive_stock",
            "description": (
                "Add newly received stock to a supermarket product. "
                "Use this when the store owner says that new stock "
                "has arrived or they received more quantity of "
                "a product."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": (
                            "The supermarket product that was received."
                        ),
                    },
                    "quantity": {
                        "type": "number",
                        "description": (
                            "The quantity of stock received."
                        ),
                    },
                },
                "required": [
                    "product_name",
                    "quantity",
                ],
            },
        },
    },

    # =====================================================
    # 4. CHECKOUT
    # =====================================================

    {
        "type": "function",
        "function": {
            "name": "checkout",
            "description": (
                "Complete a customer purchase. "
                "Use this when a customer buys a product. "
                "The tool updates inventory and creates the bill."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": (
                            "The customer's name."
                        ),
                    },
                    "product_name": {
                        "type": "string",
                        "description": (
                            "The product purchased."
                        ),
                    },
                    "quantity": {
                        "type": "number",
                        "description": (
                            "The quantity purchased."
                        ),
                    },
                    "payment_method": {
                        "type": "string",
                        "description": (
                            "Payment method. "
                            "Usually cash, upi, or credit."
                        ),
                    },
                },
                "required": [
                    "customer_name",
                    "product_name",
                    "quantity",
                    "payment_method",
                ],
            },
        },
    },

    # =====================================================
    # 5. ADD CREDIT
    # =====================================================

    {
        "type": "function",
        "function": {
            "name": "add_credit",
            "description": (
                "Add an amount to a customer's khata credit balance. "
                "Use this when the store owner says that a customer "
                "owes money or wants to add credit to the customer's "
                "account."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": (
                            "The customer's name."
                        ),
                    },
                    "amount": {
                        "type": "number",
                        "description": (
                            "The credit amount to add."
                        ),
                    },
                },
                "required": [
                    "customer_name",
                    "amount",
                ],
            },
        },
    },

    # =====================================================
    # 6. GET BALANCE
    # =====================================================

    {
        "type": "function",
        "function": {
            "name": "get_balance",
            "description": (
                "Check how much money a customer currently owes "
                "the supermarket. Use this when the store owner "
                "asks for a customer's khata balance or outstanding "
                "amount."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": (
                            "The customer's name."
                        ),
                    }
                },
                "required": [
                    "customer_name",
                ],
            },
        },
    },

    # =====================================================
    # 7. RECORD PAYMENT
    # =====================================================

    {
        "type": "function",
        "function": {
            "name": "record_payment",
            "description": (
                "Record a payment made by a customer toward "
                "their outstanding khata balance."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": (
                            "The customer's name."
                        ),
                    },
                    "amount": {
                        "type": "number",
                        "description": (
                            "The amount paid by the customer."
                        ),
                    },
                },
                "required": [
                    "customer_name",
                    "amount",
                ],
            },
        },
    },
]


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are an AI agent for an Indian kirana/supermarket store.

Your job is to understand the store owner's natural-language
request and use the correct tool.

IMPORTANT RULES:

1. Never guess information from the database.

2. Always use the appropriate tool when the user is asking
   about inventory, purchases, or customer accounts.

3. For a specific product stock question, use get_stock.

4. For questions about products running low, use get_low_stock.

5. When new stock is received, use receive_stock.

6. When a customer buys a product, use checkout.

7. When money is added to a customer's credit/khata account,
   use add_credit.

8. When the store owner asks how much a customer owes,
   use get_balance.

9. When a customer pays part or all of their outstanding amount,
   use record_payment.

10. After receiving the real tool result, give a short,
    clear and natural response.

11. Never invent stock quantities, prices, balances, bills,
    or payment information.

12. Do not expose technical tool names to the user.

13. If the user gives an unclear request and important
    information is missing, ask for the missing information.

Examples:

USER:
How much Maggi do we have?

TOOL:
get_stock(product_name="Maggi")


USER:
How many Maggi packets are left?

TOOL:
get_stock(product_name="Maggi")


USER:
Which products are running low?

TOOL:
get_low_stock()


USER:
What should I restock?

TOOL:
get_low_stock()


USER:
We received 20 Maggi packets.

TOOL:
receive_stock(
    product_name="Maggi",
    quantity=20
)


USER:
Add 10 Maggi packets to stock.

TOOL:
receive_stock(
    product_name="Maggi",
    quantity=10
)


USER:
Ramesh bought 2 Maggi 70g and paid cash.

TOOL:
checkout(
    customer_name="Ramesh",
    product_name="Maggi 70g",
    quantity=2,
    payment_method="cash"
)


USER:
Ramesh bought 2 Maggi and paid through UPI.

TOOL:
checkout(
    customer_name="Ramesh",
    product_name="Maggi",
    quantity=2,
    payment_method="upi"
)


USER:
Ramesh bought 2 Maggi on credit.

TOOL:
checkout(
    customer_name="Ramesh",
    product_name="Maggi",
    quantity=2,
    payment_method="credit"
)


USER:
Ramesh owes me 500.

TOOL:
add_credit(
    customer_name="Ramesh",
    amount=500
)


USER:
Add 500 credit to Ramesh.

TOOL:
add_credit(
    customer_name="Ramesh",
    amount=500
)


USER:
How much does Ramesh owe?

TOOL:
get_balance(
    customer_name="Ramesh"
)


USER:
What is Ramesh's balance?

TOOL:
get_balance(
    customer_name="Ramesh"
)


USER:
Ramesh paid me 300.

TOOL:
record_payment(
    customer_name="Ramesh",
    amount=300
)


USER:
Ramesh paid 300.

TOOL:
record_payment(
    customer_name="Ramesh",
    amount=300
)
"""


# =========================================================
# PROCESS MESSAGE
# =========================================================

def process_message(message: str):

    message = message.strip()

    if not message:
        return {
            "success": False,
            "message": "Please send a message.",
        }

    try:

        # =================================================
        # FIRST AI CALL
        # Understand the user's request
        # =================================================

        response = chat(
            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],

            tools=TOOLS,
        )

        assistant_message = response["message"]

        # =================================================
        # CHECK TOOL CALLS
        # =================================================

        tool_calls = assistant_message.get(
            "tool_calls"
        )

        # =================================================
        # NO TOOL REQUIRED
        # =================================================

        if not tool_calls:

            content = assistant_message.get(
                "content"
            )

            return {
                "success": True,
                "message": (
                    content
                    or "I couldn't understand the request."
                ),
            }

        # =================================================
        # BUILD MESSAGE HISTORY
        # =================================================

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": message,
            },
            assistant_message,
        ]

        # =================================================
        # EXECUTE ALL TOOL CALLS
        # =================================================

        for tool_call in tool_calls:

            function_name = tool_call["function"]["name"]

            arguments = tool_call["function"].get(
                "arguments",
                {},
            )

            # -------------------------------------------------
            # Ollama can return arguments as JSON string
            # -------------------------------------------------

            if isinstance(arguments, str):

                try:

                    arguments = json.loads(
                        arguments
                    )

                except json.JSONDecodeError:

                    return {
                        "success": False,
                        "message": (
                            "Invalid tool arguments."
                        ),
                    }

            # =================================================
            # GET STOCK
            # =================================================

            if function_name == "get_stock":

                product_name = arguments.get(
                    "product_name"
                )

                if not product_name:

                    return {
                        "success": False,
                        "message": (
                            "Product name was not identified."
                        ),
                    }

                tool_result = get_stock(
                    product_name
                )

            # =================================================
            # GET LOW STOCK
            # =================================================

            elif function_name == "get_low_stock":

                tool_result = get_low_stock()

            # =================================================
            # RECEIVE STOCK
            # =================================================

            elif function_name == "receive_stock":

                product_name = arguments.get(
                    "product_name"
                )

                quantity = arguments.get(
                    "quantity"
                )

                if not product_name:

                    return {
                        "success": False,
                        "message": (
                            "Product name was not identified."
                        ),
                    }

                if quantity is None:

                    return {
                        "success": False,
                        "message": (
                            "Stock quantity was not identified."
                        ),
                    }

                try:

                    quantity = float(quantity)

                except (TypeError, ValueError):

                    return {
                        "success": False,
                        "message": (
                            "Quantity must be a number."
                        ),
                    }

                tool_result = receive_stock(
                    product_name=product_name,
                    quantity=quantity,
                )

            # =================================================
            # CHECKOUT
            # =================================================

            elif function_name == "checkout":

                customer_name = arguments.get(
                    "customer_name"
                )

                product_name = arguments.get(
                    "product_name"
                )

                quantity = arguments.get(
                    "quantity"
                )

                payment_method = arguments.get(
                    "payment_method"
                )

                if not customer_name:

                    return {
                        "success": False,
                        "message": (
                            "Customer name was not identified."
                        ),
                    }

                if not product_name:

                    return {
                        "success": False,
                        "message": (
                            "Product name was not identified."
                        ),
                    }

                if quantity is None:

                    return {
                        "success": False,
                        "message": (
                            "Purchase quantity was not identified."
                        ),
                    }

                if not payment_method:

                    return {
                        "success": False,
                        "message": (
                            "Payment method was not identified."
                        ),
                    }

                try:

                    quantity = float(quantity)

                except (TypeError, ValueError):

                    return {
                        "success": False,
                        "message": (
                            "Quantity must be a number."
                        ),
                    }

                payment_method = (
                    str(payment_method)
                    .strip()
                    .lower()
                )

                tool_result = checkout(
                    customer_name=customer_name,
                    product_name=product_name,
                    quantity=quantity,
                    payment_method=payment_method,
                )

            # =================================================
            # ADD CREDIT
            # =================================================

            elif function_name == "add_credit":

                customer_name = arguments.get(
                    "customer_name"
                )

                amount = arguments.get(
                    "amount"
                )

                if not customer_name:

                    return {
                        "success": False,
                        "message": (
                            "Customer name was not identified."
                        ),
                    }

                if amount is None:

                    return {
                        "success": False,
                        "message": (
                            "Credit amount was not identified."
                        ),
                    }

                try:

                    amount = float(amount)

                except (TypeError, ValueError):

                    return {
                        "success": False,
                        "message": (
                            "Amount must be a number."
                        ),
                    }

                tool_result = add_credit(
                    customer_name=customer_name,
                    amount=amount,
                    description="AI agent credit",
                )

            # =================================================
            # GET BALANCE
            # =================================================

            elif function_name == "get_balance":

                customer_name = arguments.get(
                    "customer_name"
                )

                if not customer_name:

                    return {
                        "success": False,
                        "message": (
                            "Customer name was not identified."
                        ),
                    }

                tool_result = get_balance(
                    customer_name
                )

            # =================================================
            # RECORD PAYMENT
            # =================================================

            elif function_name == "record_payment":

                customer_name = arguments.get(
                    "customer_name"
                )

                amount = arguments.get(
                    "amount"
                )

                if not customer_name:

                    return {
                        "success": False,
                        "message": (
                            "Customer name was not identified."
                        ),
                    }

                if amount is None:

                    return {
                        "success": False,
                        "message": (
                            "Payment amount was not identified."
                        ),
                    }

                try:

                    amount = float(amount)

                except (TypeError, ValueError):

                    return {
                        "success": False,
                        "message": (
                            "Amount must be a number."
                        ),
                    }

                tool_result = record_payment(
                    customer_name=customer_name,
                    amount=amount,
                    description="AI agent payment",
                )

            # =================================================
            # UNKNOWN TOOL
            # =================================================

            else:

                return {
                    "success": False,
                    "message": (
                        f"Unknown tool requested: "
                        f"{function_name}"
                    ),
                }

            # =================================================
            # SEND TOOL RESULT BACK TO OLLAMA
            # =================================================

            messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(
                        tool_result
                    ),
                }
            )

        # =================================================
        # SECOND AI CALL
        # Generate natural-language response
        # =================================================

        final_response = chat(
            model=MODEL,
            messages=messages,
        )

        final_message = final_response["message"].get(
            "content"
        )

        if not final_message:

            return {
                "success": False,
                "message": (
                    "The AI did not generate a response."
                ),
            }

        # =================================================
        # RETURN RESULT
        # =================================================

        return {
            "success": True,
            "message": final_message,
        }

    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as e:

        return {
            "success": False,
            "message": f"Agent error: {str(e)}",
        }

