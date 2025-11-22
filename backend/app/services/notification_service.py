"""
Notification Service
Handles push notifications and email alerts
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from pathlib import Path

from app.core.config import settings


class NotificationService:
    """
    Service for sending notifications
    """
    
    @staticmethod
    def send_push_notification(
        user_token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ) -> bool:
        """
        Send push notification via Firebase Cloud Messaging
        
        Args:
            user_token: FCM device token
            title: Notification title
            body: Notification body
            data: Additional data to send
        
        Returns:
            True if successful, False otherwise
        
        Note:
            Requires Firebase Admin SDK to be configured
            For now, this is a placeholder that logs the notification
        """
        try:
            # TODO: Implement Firebase Cloud Messaging
            # This requires Firebase credentials to be configured
            
            # For now, just log the notification
            print("\n" + "="*60)
            print("📱 PUSH NOTIFICATION")
            print("="*60)
            print(f"To: {user_token[:20]}...")
            print(f"Title: {title}")
            print(f"Body: {body}")
            if data:
                print(f"Data: {data}")
            print("="*60 + "\n")
            
            # In production, use Firebase:
            """
            from firebase_admin import messaging
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=user_token,
            )
            
            response = messaging.send(message)
            return True
            """
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send push notification: {e}")
            return False
    
    
    @staticmethod
    def send_email_alert(
        recipient_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send email alert
        
        Args:
            recipient_email: Email address to send to
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
        
        Returns:
            True if successful, False otherwise
        """
        # Check if email is configured
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            print("⚠️  Email not configured. Skipping email notification.")
            print(f"   Would have sent: {subject} to {recipient_email}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.EMAILS_FROM_EMAIL or settings.SMTP_USER
            msg['To'] = recipient_email
            
            # Attach plain text
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Attach HTML if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Connect to SMTP server and send
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            print(f"✅ Email sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    
    @staticmethod
    def create_event_notification_message(event: Dict) -> tuple[str, str]:
        """
        Create notification message for an event
        
        Args:
            event: Event dictionary
        
        Returns:
            Tuple of (title, body)
        """
        event_type = event.get('event_type', 'unknown')
        confidence = event.get('confidence', 0.0)
        description = event.get('description', 'No description')
        
        # Create user-friendly title
        titles = {
            'fast_movement': '🚨 Fast Movement Detected',
            'loitering': '⏰ Loitering Detected',
            'erratic_movement': '⚠️ Suspicious Behavior',
            'theft': '🚨 THEFT ALERT',
            'suspicious_behavior': '⚠️ Suspicious Activity'
        }
        
        title = titles.get(event_type, '⚠️ Security Alert')
        
        # Create body
        body = f"{description}\n"
        body += f"Confidence: {confidence:.1%}\n"
        body += f"Time: {event.get('timestamp', 'Unknown')}"
        
        return title, body
    
    
    @staticmethod
    def create_event_email_html(event: Dict, user_name: str) -> str:
        """
        Create HTML email for event notification
        
        Args:
            event: Event dictionary
            user_name: Name of user
        
        Returns:
            HTML string
        """
        event_type = event.get('event_type', 'unknown')
        confidence = event.get('confidence', 0.0)
        description = event.get('description', 'No description')
        timestamp = event.get('timestamp', 'Unknown')
        
        # Choose color based on event type
        colors = {
            'fast_movement': '#ff6b6b',
            'loitering': '#ffd93d',
            'erratic_movement': '#ff8c42',
            'theft': '#ff0000',
            'suspicious_behavior': '#ff8c42'
        }
        color = colors.get(event_type, '#6c757d')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: {color};
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 0 0 5px 5px;
                }}
                .info-box {{
                    background-color: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid {color};
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: #6c757d;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Security Alert</h1>
                </div>
                <div class="content">
                    <p>Hello {user_name},</p>
                    <p>A security event has been detected by your CCTV system:</p>
                    
                    <div class="info-box">
                        <h3>Event Details</h3>
                        <p><strong>Type:</strong> {event_type.replace('_', ' ').title()}</p>
                        <p><strong>Description:</strong> {description}</p>
                        <p><strong>Confidence:</strong> {confidence:.1%}</p>
                        <p><strong>Time:</strong> {timestamp}</p>
                    </div>
                    
                    <p>Please review this event in your mobile app.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from your CCTV Security System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    
    @staticmethod
    def notify_user_of_event(
        user_email: str,
        user_name: str,
        user_fcm_token: Optional[str],
        event: Dict
    ) -> Dict[str, bool]:
        """
        Send all configured notifications for an event
        
        Args:
            user_email: User's email address
            user_name: User's name
            user_fcm_token: Firebase Cloud Messaging token (if available)
            event: Event dictionary
        
        Returns:
            Dictionary with success status for each notification type
        """
        results = {
            'push': False,
            'email': False
        }
        
        # Create notification content
        title, body = NotificationService.create_event_notification_message(event)
        
        # Send push notification if token available
        if user_fcm_token:
            results['push'] = NotificationService.send_push_notification(
                user_fcm_token,
                title,
                body,
                data={
                    'event_id': str(event.get('id', '')),
                    'event_type': event.get('event_type', ''),
                    'confidence': str(event.get('confidence', 0.0))
                }
            )
        
        # Send email notification
        html_body = NotificationService.create_event_email_html(event, user_name)
        results['email'] = NotificationService.send_email_alert(
            user_email,
            title,
            body,
            html_body
        )
        
        return results
