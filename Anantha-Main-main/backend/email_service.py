from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import logging

logger = logging.getLogger(__name__)

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@ananthalakshmi.com')

async def send_order_confirmation_email(to_email: str, order_data: dict):
    """Send order confirmation email with order details"""
    try:
        if not SENDGRID_API_KEY:
            logger.warning("SendGrid API key not configured. Email not sent.")
            return False
            
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=f'Order Confirmation - #{order_data["order_id"]}',
            html_content=f'''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #f97316; text-align: center;">🎉 Order Confirmed!</h2>
                    <p>Dear {order_data["customer_name"]},</p>
                    <p>Thank you for your order from Anantha Lakshmi Traditional Foods!</p>
                    
                    <div style="background-color: #fff7ed; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #ea580c; margin-top: 0;">Order Details</h3>
                        <p><strong>Order ID:</strong> {order_data["order_id"]}</p>
                        <p><strong>Tracking Code:</strong> {order_data["tracking_code"]}</p>
                        <p><strong>Order Date:</strong> {order_data["order_date"]}</p>
                        <p><strong>Total Amount:</strong> ₹{order_data["total"]}</p>
                    </div>
                    
                    <div style="background-color: #f0fdf4; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #16a34a; margin-top: 0;">Delivery Address</h3>
                        <p>{order_data["address"]}<br>
                        {order_data["location"]}</p>
                        <p><strong>Phone:</strong> {order_data["phone"]}</p>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <h3 style="color: #1e40af;">Items Ordered</h3>
                        {order_data["items_html"]}
                    </div>
                    
                    <div style="background-color: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h4 style="margin-top: 0;">📦 Track Your Order</h4>
                        <p>You can track your order anytime using your Order ID or Tracking Code on our website.</p>
                    </div>
                    
                    <p style="margin-top: 30px;">If you have any questions, feel free to contact us at <strong>9985116385</strong></p>
                    
                    <p style="text-align: center; color: #666; margin-top: 30px; font-size: 12px;">
                        Thank you for choosing Anantha Lakshmi Traditional Foods!<br>
                        Handcrafted with love and tradition 💚
                    </p>
                </div>
            </body>
            </html>
            '''
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Email sent successfully to {to_email}. Status code: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False
