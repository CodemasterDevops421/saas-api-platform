import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from typing import List, Dict

class AlertManager:
    def __init__(self, config: Dict):
        self.config = config
        self.alert_history = []
    
    async def process_alerts(self, alerts: List[Dict]):
        for alert in alerts:
            if self._should_notify(alert):
                await self._send_notifications(alert)
                self.alert_history.append(alert)
    
    def _should_notify(self, alert: Dict) -> bool:
        # Check alert history and cooldown
        similar_alerts = [
            a for a in self.alert_history[-10:]
            if a['message'] == alert['message']
        ]
        
        if similar_alerts:
            last_alert_time = similar_alerts[-1]['timestamp']
            cooldown = self.config.get('cooldown_minutes', 15)
            # Check if enough time has passed
            return (alert['timestamp'] - last_alert_time).total_seconds() > cooldown * 60
        
        return True
    
    async def _send_notifications(self, alert: Dict):
        if 'email' in self.config['channels']:
            await self._send_email(alert)
        
        if 'slack' in self.config['channels']:
            await self._send_slack(alert)
    
    async def _send_email(self, alert: Dict):
        msg = MIMEMultipart()
        msg['Subject'] = f"[{alert['level'].upper()}] Performance Alert"
        msg['From'] = self.config['email']['from']
        msg['To'] = self.config['email']['to']
        
        body = f"Alert: {alert['message']}\n\nTimestamp: {alert['timestamp']}"
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(self.config['email']['smtp_host']) as server:
            server.starttls()
            server.login(
                self.config['email']['username'],
                self.config['email']['password']
            )
            server.send_message(msg)
    
    async def _send_slack(self, alert: Dict):
        webhook_url = self.config['slack']['webhook_url']
        message = {
            'text': f"*[{alert['level'].upper()}] Performance Alert*\n{alert['message']}"
        }
        
        requests.post(webhook_url, json=message)