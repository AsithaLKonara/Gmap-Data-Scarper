"""Workflow execution engine for automation."""
from typing import Dict, Any, List, Optional
import uuid
import json
from datetime import datetime
from backend.models.database import get_session
from backend.models.workflow import Workflow, WorkflowExecution


class WorkflowEngine:
    """Engine for executing automation workflows."""
    
    def __init__(self):
        """Initialize workflow engine."""
        self.action_handlers = {
            "add_to_google_sheet": self._handle_add_to_google_sheet,
            "send_email": self._handle_send_email,
            "send_whatsapp": self._handle_send_whatsapp,
            "send_sms": self._handle_send_sms,
            "push_to_crm": self._handle_push_to_crm,
            "add_to_telegram": self._handle_add_to_telegram,
            "apply_scoring": self._handle_apply_scoring,
            "categorize": self._handle_categorize,
        }
    
    def execute_workflow(
        self,
        workflow: Workflow,
        trigger_data: Dict[str, Any]
    ) -> WorkflowExecution:
        """
        Execute a workflow with trigger data.
        
        Args:
            workflow: Workflow model instance
            trigger_data: Data that triggered the workflow
            
        Returns:
            WorkflowExecution instance
        """
        execution_id = str(uuid.uuid4())
        db = get_session()
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow.workflow_id,
            user_id=workflow.user_id,
            trigger_data=trigger_data,
            status="running",
            started_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()
        
        action_results = []
        
        try:
            # Execute each action
            for action in workflow.actions:
                action_type = action.get("type")
                action_config = action.get("config", {})
                
                if action_type in self.action_handlers:
                    try:
                        result = self.action_handlers[action_type](trigger_data, action_config)
                        action_results.append({
                            "action_type": action_type,
                            "status": "success",
                            "result": result
                        })
                    except Exception as e:
                        action_results.append({
                            "action_type": action_type,
                            "status": "failed",
                            "error": str(e)
                        })
                else:
                    action_results.append({
                        "action_type": action_type,
                        "status": "unknown",
                        "error": f"Unknown action type: {action_type}"
                    })
            
            # Update execution
            execution.action_results = action_results
            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            execution.duration_seconds = int(
                (execution.completed_at - execution.started_at).total_seconds()
            )
            
            # Update workflow stats
            workflow.execution_count += 1
            workflow.last_executed_at = datetime.utcnow()
            
        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)
            execution.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(execution)
        db.close()
        
        return execution
    
    def _handle_add_to_google_sheet(
        self,
        trigger_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle add to Google Sheet action."""
        try:
            import gspread
            from oauth2client.service_account import ServiceAccountCredentials
            
            sheet_id = config.get("sheet_id")
            worksheet_name = config.get("worksheet_name", "Sheet1")
            credentials_path = config.get("credentials_path")
            
            if not sheet_id or not credentials_path:
                raise ValueError("sheet_id and credentials_path required")
            
            # Authenticate
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                credentials_path, scope
            )
            client = gspread.authorize(creds)
            
            # Open sheet
            sheet = client.open_by_key(sheet_id)
            worksheet = sheet.worksheet(worksheet_name)
            
            # Prepare row data
            row_data = [
                trigger_data.get("display_name", ""),
                trigger_data.get("phone", ""),
                trigger_data.get("email", ""),
                trigger_data.get("location", ""),
                trigger_data.get("platform", ""),
                datetime.utcnow().isoformat()
            ]
            
            # Append row
            worksheet.append_row(row_data)
            
            return {"success": True, "message": "Added to Google Sheet"}
        except Exception as e:
            raise Exception(f"Failed to add to Google Sheet: {str(e)}")
    
    def _handle_send_email(
        self,
        trigger_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle send email action."""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            api_key = config.get("sendgrid_api_key") or os.getenv("SENDGRID_API_KEY")
            if not api_key:
                raise ValueError("SendGrid API key required")
            
            sg = SendGridAPIClient(api_key)
            
            message = Mail(
                from_email=config.get("from_email", "noreply@example.com"),
                to_emails=config.get("to_email"),
                subject=config.get("subject", "New Lead Found"),
                html_content=config.get("html_content", f"New lead: {trigger_data.get('display_name')}")
            )
            
            response = sg.send(message)
            
            return {"success": True, "message_id": response.headers.get("X-Message-Id")}
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")
    
    def _handle_send_whatsapp(
        self,
        trigger_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle send WhatsApp action."""
        try:
            from twilio.rest import Client
            
            account_sid = config.get("twilio_account_sid") or os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = config.get("twilio_auth_token") or os.getenv("TWILIO_AUTH_TOKEN")
            from_number = config.get("from_number")
            to_number = config.get("to_number")
            message = config.get("message", f"New lead: {trigger_data.get('display_name')}")
            
            if not all([account_sid, auth_token, from_number, to_number]):
                raise ValueError("Twilio credentials and phone numbers required")
            
            client = Client(account_sid, auth_token)
            
            # Send WhatsApp message
            message_obj = client.messages.create(
                body=message,
                from_=f"whatsapp:{from_number}",
                to=f"whatsapp:{to_number}"
            )
            
            return {"success": True, "message_sid": message_obj.sid}
        except Exception as e:
            raise Exception(f"Failed to send WhatsApp: {str(e)}")
    
    def _handle_send_sms(
        self,
        trigger_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle send SMS action."""
        try:
            from twilio.rest import Client
            
            account_sid = config.get("twilio_account_sid") or os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = config.get("twilio_auth_token") or os.getenv("TWILIO_AUTH_TOKEN")
            from_number = config.get("from_number")
            to_number = config.get("to_number")
            message = config.get("message", f"New lead: {trigger_data.get('display_name')}")
            
            if not all([account_sid, auth_token, from_number, to_number]):
                raise ValueError("Twilio credentials and phone numbers required")
            
            client = Client(account_sid, auth_token)
            
            message_obj = client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            
            return {"success": True, "message_sid": message_obj.sid}
        except Exception as e:
            raise Exception(f"Failed to send SMS: {str(e)}")
    
    def _handle_push_to_crm(
        self,
        trigger_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle push to CRM action."""
        crm_type = config.get("crm_type", "hubspot")
        
        if crm_type == "hubspot":
            return self._push_to_hubspot(trigger_data, config)
        elif crm_type == "zoho":
            return self._push_to_zoho(trigger_data, config)
        elif crm_type == "pipedrive":
            return self._push_to_pipedrive(trigger_data, config)
        else:
            raise ValueError(f"Unsupported CRM type: {crm_type}")
    
    def _push_to_hubspot(
        self,
        trigger_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Push lead to HubSpot."""
        try:
            import requests
            
            api_key = config.get("hubspot_api_key") or os.getenv("HUBSPOT_API_KEY")
            if not api_key:
                raise ValueError("HubSpot API key required")
            
            url = "https://api.hubapi.com/crm/v3/objects/contacts"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            properties = {
                "firstname": trigger_data.get("display_name", "").split()[0] if trigger_data.get("display_name") else "",
                "lastname": " ".join(trigger_data.get("display_name", "").split()[1:]) if trigger_data.get("display_name") else "",
                "phone": trigger_data.get("phone", ""),
                "email": trigger_data.get("email", ""),
                "city": trigger_data.get("city", ""),
            }
            
            data = {"properties": properties}
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            return {"success": True, "contact_id": response.json().get("id")}
        except Exception as e:
            raise Exception(f"Failed to push to HubSpot: {str(e)}")
    
    def _push_to_zoho(
        self,
        trigger_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Push lead to Zoho CRM."""
        try:
            from backend.services.zoho_crm import zoho_crm_service
            result = zoho_crm_service.create_contact(trigger_data)
            return result
        except Exception as e:
            return {"success": False, "error": f"Failed to push to Zoho: {str(e)}"}
    
    def _push_to_pipedrive(
        self,
        trigger_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Push lead to Pipedrive."""
        try:
            from backend.services.pipedrive_crm import pipedrive_crm_service
            
            # Determine if it's a person or organization
            lead_type = trigger_data.get("lead_type", "individual")
            
            if lead_type == "business":
                result = pipedrive_crm_service.create_organization(trigger_data)
            else:
                result = pipedrive_crm_service.create_person(trigger_data)
            
            return result
        except Exception as e:
            return {"success": False, "error": f"Failed to push to Pipedrive: {str(e)}"}
    
    def _handle_add_to_telegram(
        self,
        trigger_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle add to Telegram notification."""
        try:
            import requests
            
            bot_token = config.get("telegram_bot_token") or os.getenv("TELEGRAM_BOT_TOKEN")
            chat_id = config.get("telegram_chat_id")
            message = config.get("message", f"New lead: {trigger_data.get('display_name')}")
            
            if not bot_token or not chat_id:
                raise ValueError("Telegram bot token and chat ID required")
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            return {"success": True, "message_id": response.json().get("result", {}).get("message_id")}
        except Exception as e:
            raise Exception(f"Failed to send Telegram message: {str(e)}")
    
    def _handle_apply_scoring(
        self,
        trigger_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle apply scoring action."""
        # Scoring is already applied during lead extraction
        # This action can be used to re-score or apply custom scoring
        from backend.services.lead_scorer_ai import ai_lead_scorer
        
        query = trigger_data.get("search_query", "")
        score = ai_lead_scorer.calculate_score(trigger_data, query)
        
        return {"success": True, "score": score, "category": ai_lead_scorer.get_score_category(score)}
    
    def _handle_categorize(
        self,
        trigger_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle categorize action."""
        # Categorization is already done during extraction
        # This can be used for custom categorization rules
        return {"success": True, "categories": trigger_data.get("categories", [])}


# Global instance
workflow_engine = WorkflowEngine()

