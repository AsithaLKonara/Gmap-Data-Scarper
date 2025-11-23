"""Scheduled report execution service."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
from backend.models.database import get_session
from backend.models.scheduled_report import ScheduledReport
from backend.services.report_builder import report_builder_service
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


class ScheduledReportService:
    """Service for managing and executing scheduled reports."""
    
    def create_scheduled_report(
        self,
        user_id: str,
        name: str,
        report_config: Dict[str, Any],
        schedule: Dict[str, Any],
        delivery_method: str = "email",
        delivery_config: Optional[Dict[str, Any]] = None,
        format: str = "json",
        team_id: Optional[str] = None
    ) -> ScheduledReport:
        """
        Create a scheduled report.
        
        Args:
            user_id: User ID
            name: Report name
            report_config: Report builder configuration
            schedule: Schedule config (frequency, day, time)
            delivery_method: Delivery method (email, webhook, s3)
            delivery_config: Delivery configuration
            format: Report format (json, csv, pdf)
            team_id: Optional team ID
            
        Returns:
            Created ScheduledReport
        """
        db = get_session()
        try:
            report_id = str(uuid.uuid4())
            
            # Calculate next run time
            next_run = self._calculate_next_run(schedule)
            
            report = ScheduledReport(
                report_id=report_id,
                user_id=user_id,
                team_id=team_id,
                name=name,
                report_config=report_config,
                schedule=schedule,
                delivery_method=delivery_method,
                delivery_config=delivery_config or {},
                format=format,
                is_active=True,
                next_run_at=next_run
            )
            
            db.add(report)
            db.commit()
            db.refresh(report)
            return report
        finally:
            db.close()
    
    def _calculate_next_run(self, schedule: Dict[str, Any]) -> datetime:
        """Calculate next run time based on schedule."""
        frequency = schedule.get("frequency", "daily")
        time_str = schedule.get("time", "09:00")
        hour, minute = map(int, time_str.split(":"))
        
        now = datetime.utcnow()
        
        if frequency == "daily":
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        elif frequency == "weekly":
            day = schedule.get("day", 0)  # 0 = Monday
            days_ahead = (day - now.weekday()) % 7
            if days_ahead == 0 and now.hour >= hour:
                days_ahead = 7
            next_run = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        elif frequency == "monthly":
            day = schedule.get("day", 1)
            if now.day >= day and now.hour >= hour:
                # Next month
                if now.month == 12:
                    next_run = datetime(now.year + 1, 1, day, hour, minute)
                else:
                    next_run = datetime(now.year, now.month + 1, day, hour, minute)
            else:
                # This month
                next_run = datetime(now.year, now.month, day, hour, minute)
        else:
            next_run = now + timedelta(days=1)
        
        return next_run
    
    def get_due_reports(self) -> List[ScheduledReport]:
        """Get reports that are due to run."""
        db = get_session()
        try:
            now = datetime.utcnow()
            return db.query(ScheduledReport).filter(
                ScheduledReport.is_active == True,
                ScheduledReport.next_run_at <= now
            ).all()
        finally:
            db.close()
    
    def execute_report(self, report: ScheduledReport) -> Dict[str, Any]:
        """
        Execute a scheduled report.
        
        Args:
            report: ScheduledReport instance
            
        Returns:
            Execution result
        """
        db = get_session()
        try:
            # Build report
            report_data = report_builder_service.build_report(
                user_id=report.user_id,
                report_config=report.report_config
            )
            
            # Export report
            report_bytes = report_builder_service.export_report(
                report_data=report_data,
                format=report.format
            )
            
            # Deliver report
            delivery_result = self._deliver_report(
                report=report,
                report_data=report_data,
                report_bytes=report_bytes
            )
            
            # Update report
            report.last_run_at = datetime.utcnow()
            report.next_run_at = self._calculate_next_run(report.schedule)
            report.run_count += 1
            db.commit()
            
            return {
                "success": True,
                "report_id": report.report_id,
                "delivery_result": delivery_result,
                "next_run_at": report.next_run_at.isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    def _deliver_report(
        self,
        report: ScheduledReport,
        report_data: Dict[str, Any],
        report_bytes: bytes
    ) -> Dict[str, Any]:
        """Deliver report via configured method."""
        if report.delivery_method == "email":
            return self._deliver_email(report, report_data, report_bytes)
        elif report.delivery_method == "webhook":
            return self._deliver_webhook(report, report_data, report_bytes)
        elif report.delivery_method == "s3":
            return self._deliver_s3(report, report_data, report_bytes)
        else:
            return {"success": False, "error": f"Unknown delivery method: {report.delivery_method}"}
    
    def _deliver_email(
        self,
        report: ScheduledReport,
        report_data: Dict[str, Any],
        report_bytes: bytes
    ) -> Dict[str, Any]:
        """Deliver report via email."""
        try:
            emails = report.delivery_config.get("emails", [])
            if not emails:
                return {"success": False, "error": "No email addresses configured"}
            
            # Get SMTP config
            smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER")
            smtp_password = os.getenv("SMTP_PASSWORD")
            
            if not smtp_user or not smtp_password:
                return {"success": False, "error": "SMTP not configured"}
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = ", ".join(emails)
            msg['Subject'] = f"Scheduled Report: {report.name}"
            
            body = f"Please find attached the scheduled report: {report.name}\n\n"
            body += f"Total Leads: {report_data.get('total_leads', 0)}\n"
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach report file
            from email.mime.base import MIMEBase
            from email import encoders
            
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(report_bytes)
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename=report_{report.report_id}.{report.format}'
            )
            msg.attach(attachment)
            
            # Send email
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            return {"success": True, "emails_sent": len(emails)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _deliver_webhook(
        self,
        report: ScheduledReport,
        report_data: Dict[str, Any],
        report_bytes: bytes
    ) -> Dict[str, Any]:
        """Deliver report via webhook."""
        try:
            import requests
            
            webhook_url = report.delivery_config.get("url")
            if not webhook_url:
                return {"success": False, "error": "Webhook URL not configured"}
            
            # Send POST request
            response = requests.post(
                webhook_url,
                json=report_data,
                files={"report": report_bytes},
                timeout=30
            )
            response.raise_for_status()
            
            return {"success": True, "status_code": response.status_code}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _deliver_s3(
        self,
        report: ScheduledReport,
        report_data: Dict[str, Any],
        report_bytes: bytes
    ) -> Dict[str, Any]:
        """Deliver report to S3."""
        try:
            import boto3
            
            bucket = report.delivery_config.get("bucket")
            key = report.delivery_config.get("key", f"reports/{report.report_id}.{report.format}")
            
            if not bucket:
                return {"success": False, "error": "S3 bucket not configured"}
            
            s3 = boto3.client('s3')
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=report_bytes
            )
            
            return {"success": True, "s3_key": key}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global instance
scheduled_report_service = ScheduledReportService()

