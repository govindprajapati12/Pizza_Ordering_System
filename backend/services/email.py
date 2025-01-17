import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr
from sqlalchemy.orm import Session
from models.models import Order, OrderItem, OrderTopping

async def send_email(subject: str, body: str, recipient_email: str):
    try:
        # SMTP server setup (using Gmail as an example)
        sender_email = "travelcrafters10@gmail.com"
        sender_password = "vbrr nssf mvvm kfvg"  # Use app-specific password if using Gmail

        msg = MIMEMultipart()
        msg['From'] = formataddr(('PIzza Par5adise', sender_email))
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        # Sending the email via Gmail's SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Secure connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise

async def generate_order_email(order_data: dict):
    # Extract order details from the data
    order = order_data['order']
    items = order_data['order_items']
    toppings = order_data['order_toppings']
 
    email_body = f"""
    <h1>Order Confirmation</h1>
    <p>Thank you for your order!</p>
    <p><strong>Order ID:</strong> {order.id}</p>
    <p><strong>Order Date:</strong> {order.created_at}</p>
    <p><strong>Total Price:</strong> ₹{order.total_price}</p>
    <p><strong>Status:</strong> {order.status}</p>
    
    <h2>Order Items:</h2>
    <ul>
    """
    for item in items:
        pizza_name = item.pizza.name  # Accessing the pizza name through the relationship
        item_price = item.pizza.price  # Accessing the pizza price through the relationship
        quantity = item.quantity

        email_body += f"""
        <li>
            <strong>{pizza_name}</strong> x {quantity} - ₹{item_price * quantity}
            <ul>
        """

        for topping in toppings:
            if topping.order_item_id == item.id:
                topping_name = topping.topping.name  # Accessing the topping name through the relationship
                topping_price = topping.topping.price
                email_body += f"""
                    <li>{topping_name} - ₹{topping_price}</li>
                """

        email_body += "</ul></li>"

    email_body += "</ul>"

    return email_body




async def send_order_confirmation_service(order_id: int, db: Session):
    # Fetch the order and its items
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise Exception("Order not found")

    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    order_toppings = db.query(OrderTopping).filter(OrderTopping.order_item_id.in_([item.id for item in order_items])).all()

    # Generate the email body
    order_data = {
        "order": order,
        "order_items": order_items,
        "order_toppings": order_toppings
    }
    order.status = "Received"
    db.commit()
    db.refresh(order)
    email_body = await generate_order_email(order_data)

    # Send email to the user
    user_email = order.user.email  # Assuming user's email is stored in the order object
    await send_email("Order Confirmation - Your Pizza Order", email_body, user_email)


    return {"message": "Order confirmation email sent and order status updated successfully."}