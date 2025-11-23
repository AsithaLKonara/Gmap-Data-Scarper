"""Service wrapper for orchestrator_core with WebSocket support."""
import threading
import uuid
from typing import Optional, Dict, Callable, List
import datetime
import os
import sys
import json
import asyncio

# Add parent directory to path to import orchestrator_core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator_core import run_orchestrator, StopFlag, PauseFlag
from backend.models.schemas import ScrapeRequest, TaskStatus, ScrapeResult, LogMessage, ProgressUpdate
from backend.services.lead_objective_config import LeadObjectiveConfig


class TaskManager:
    """Manages scraping tasks and their state."""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.websocket_connections: Dict[str, List] = {
            "logs": {},
            "progress": {},
            "results": {}
        }
    
    def create_task(self, request: ScrapeRequest, user_id: Optional[str] = None) -> str:
        """Create a new scraping task."""
        task_id = str(uuid.uuid4())
        
        # Use user_id from request or parameter
        task_user_id = request.user_id or user_id
        
        # Create user-specific output directory if user_id provided
        if task_user_id:
            output_dir = os.path.join(
                os.path.expanduser("~"),
                ".gmap_scraper",
                "users",
                task_user_id,
                "social_leads"
            )
        else:
            output_dir = os.path.expanduser("~/Documents/social_leads")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create temporary config file for this task
        config_path = os.path.join(
            os.path.expanduser("~"),
            ".gmap_scraper",
            f"task_{task_id}_config.yaml"
        )
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Apply lead objective configuration if specified
        request_dict = request.dict()
        if request.lead_objective:
            request_dict = LeadObjectiveConfig.apply_config_to_request(
                request.lead_objective,
                request_dict
            )
        
        # Write config
        import yaml
        config = {
            "enabled_platforms": request_dict.get("platforms", request.platforms),
            "max_results_per_query": request.max_results or 0,
            "headless": request.headless,
            "per_platform_delay_seconds": 8,
            "resume": True,
            "output_dir": output_dir,
            "filters": {
                "business_type": request_dict.get("business_type") or request.business_type or [],
                "job_level": request_dict.get("job_level") or request.job_level or [],
                "location": request_dict.get("location") or request.location,
                "radius_km": request_dict.get("radius_km") or request.radius_km,
                "education_level": request_dict.get("education_level") or request.education_level or [],
                "date_range": request_dict.get("date_range") or request.date_range,
                "active_within_days": request_dict.get("active_within_days") or request.active_within_days,
                "boosted_only": request_dict.get("boosted_only") or request.boosted_only or False,
                "student_only": request_dict.get("student_only") if "student_only" in request_dict else request.student_only,
            }
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        
        self.tasks[task_id] = {
            "task_id": task_id,
            "user_id": task_user_id,
            "status": "running",
            "progress": {},
            "total_results": 0,
            "current_query": None,
            "current_platform": None,
            "lead_objective": request.lead_objective,
            "started_at": datetime.datetime.now(),
            "completed_at": None,
            "error": None,
            "config_path": config_path,
            "stop_flag": StopFlag(),
            "pause_flag": PauseFlag(),
            "thread": None,
            "queries": request.queries,
        }
        
        return task_id
    
    def start_task(self, task_id: str, request: ScrapeRequest):
        """Start a scraping task in a background thread."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        stop_flag = task["stop_flag"]
        pause_flag = task["pause_flag"]
        
        # Create callbacks that emit WebSocket events
        def on_log(message: str):
            self._broadcast_log(task_id, message)
        
        def on_progress(progress: Dict[str, int]):
            task["progress"] = progress
            task["total_results"] = sum(progress.values())
            self._broadcast_progress(task_id, progress)
        
        def on_result(result: Dict):
            task["total_results"] += 1
            
            # Calculate lead score
            from backend.services.lead_scorer_ai import ai_lead_scorer
            query = result.get("Search Query", "")
            lead_score = ai_lead_scorer.calculate_score(result, query)
            result["lead_score"] = lead_score
            result["lead_score_category"] = ai_lead_scorer.get_score_category(lead_score)
            
            # AI enrichment
            from backend.services.ai_enrichment import ai_enrichment_service
            enriched_result = ai_enrichment_service.enrich_lead(result)
            result.update(enriched_result)
            
            # Prepare result dict for duplicate detection and enrichment
            result_dict = {
                "search_query": result.get("Search Query", ""),
                "platform": result.get("Platform", ""),
                "profile_url": result.get("Profile URL", ""),
                "handle": result.get("Handle"),
                "display_name": result.get("Display Name"),
                "bio_about": result.get("Bio/About"),
                "website": result.get("Website"),
                "email": result.get("Email"),
                "phone": result.get("Phone"),
                "followers": result.get("Followers"),
                "location": result.get("Location"),
                "business_type": result.get("business_type"),
                "industry": result.get("industry"),
                "city": result.get("city"),
                "region": result.get("region"),
                "country": result.get("country"),
                "job_title": result.get("job_title"),
                "seniority_level": result.get("seniority_level"),
                "education_level": result.get("education_level"),
                "institution_name": result.get("institution_name"),
                "lead_type": result.get("lead_type"),
                "field_of_study": result.get("field_of_study"),
                "degree_program": result.get("degree_program"),
                "graduation_year": result.get("graduation_year"),
                "lead_score": result.get("lead_score"),
                "lead_score_category": result.get("lead_score_category"),
                "keywords": result.get("keywords"),
                "estimated_revenue": result.get("estimated_revenue"),
                "employee_count": result.get("employee_count"),
            }
            
            # Extract phone data from result
            phones_data = result.get("phones", [])
            if phones_data and len(phones_data) > 0:
                result_dict["phones"] = phones_data
                result_dict["phone_normalized"] = phones_data[0].get("normalized_e164")
            elif result.get("phone_normalized"):
                result_dict["phone_normalized"] = result.get("phone_normalized")
            
            # Enhanced duplicate detection
            try:
                from backend.services.duplicate_detection import get_duplicate_detection_service
                duplicate_service = get_duplicate_detection_service()
                
                is_dup, dup_reason, existing_lead = duplicate_service.is_duplicate(
                    result_dict,
                    task_id=task_id,
                    check_across_tasks=True
                )
                
                if is_dup:
                    self._broadcast_log(task_id, f"[DEDUP] Skipped duplicate ({dup_reason}): {result_dict.get('display_name', 'N/A')}")
                    return  # Skip saving duplicate
            except Exception as e:
                # Log error but continue
                print(f"[DEDUP] Error checking duplicates: {e}")
            
            # Enrichment: Phone verification
            try:
                phone_to_verify = result_dict.get("phone_normalized") or result_dict.get("phone")
                if phone_to_verify and phone_to_verify != "N/A":
                    from backend.services.phone_verifier import get_phone_verifier
                    verifier = get_phone_verifier()
                    verification_result = verifier.verify(phone_to_verify)
                    
                    # Update phone data with verification
                    if phones_data and len(phones_data) > 0:
                        original_confidence = phones_data[0].get("confidence_score", 0)
                        updated_confidence = verifier.update_confidence_score(
                            original_confidence,
                            verification_result
                        )
                        phones_data[0]["confidence_score"] = updated_confidence
                        phones_data[0]["verification_status"] = "verified" if verification_result.get("is_valid") else "invalid"
                        phones_data[0]["carrier"] = verification_result.get("carrier")
                        phones_data[0]["line_type"] = verification_result.get("line_type")
                        # Update result dict
                        result["phones"] = phones_data
            except Exception as e:
                print(f"[ENRICH] Error verifying phone: {e}")
            
            # Enrichment: Business enrichment
            try:
                business_name = result_dict.get("display_name", "")
                website = result_dict.get("website", "")
                location = result_dict.get("location", "")
                
                if business_name and business_name != "N/A":
                    from backend.services.enrichment_service import get_enrichment_service
                    enrichment_service = get_enrichment_service()
                    enrichment_data = enrichment_service.enrich_business(
                        business_name=business_name,
                        website=website if website and website != "N/A" else None,
                        location=location if location and location != "N/A" else None
                    )
                    
                    # Merge enrichment data into result
                    if enrichment_data.get("industry") and enrichment_data["industry"] != "unknown":
                        result["industry"] = enrichment_data["industry"]
                        result_dict["industry"] = enrichment_data["industry"]
                    if enrichment_data.get("company_size") and enrichment_data["company_size"] != "unknown":
                        result["company_size"] = enrichment_data["company_size"]
                    if enrichment_data.get("description"):
                        result["business_description"] = enrichment_data["description"]
            except Exception as e:
                print(f"[ENRICH] Error enriching business: {e}")
            
            # Convert result dict to ScrapeResult schema
            scrape_result = self._dict_to_scrape_result(result)
            
            # Save to PostgreSQL (with dual-write to CSV)
            try:
                from backend.services.postgresql_storage import get_postgresql_storage
                storage = get_postgresql_storage()
                result_dict["phones"] = phones_data if phones_data else []
                storage.save_lead(task_id, result_dict)
                
                # Increment lead count for user plan
                user_id = task.get("user_id")
                if user_id:
                    try:
                        from backend.services.plan_service import get_plan_service
                        from backend.models.database import get_session
                        db = get_session()
                        try:
                            plan_service = get_plan_service(db)
                            plan_service.increment_lead_count(user_id)
                        finally:
                            db.close()
                    except Exception as e:
                        # Log but don't fail - plan tracking is non-critical
                        print(f"[PLAN] Error incrementing lead count: {e}")
            except Exception as e:
                # Log error but don't fail the task
                print(f"[POSTGRES] Error saving lead to database: {e}")
            
            # Trigger workflows for new lead
            try:
                user_id = task.get("user_id")
                if user_id:
                    from backend.services.workflow_engine import workflow_engine
                    from backend.models.database import get_session
                    from backend.models.workflow import Workflow
                    
                    db = get_session()
                    try:
                        # Find workflows with "new_lead" trigger
                        workflows = db.query(Workflow).filter(
                            Workflow.user_id == user_id,
                            Workflow.is_active == True,
                            Workflow.is_enabled == True
                        ).all()
                        
                        for workflow in workflows:
                            trigger = workflow.trigger or {}
                            if trigger.get("type") == "new_lead":
                                # Check trigger conditions
                                conditions = trigger.get("conditions", {})
                                should_trigger = True
                                
                                # Check lead score condition
                                if "min_lead_score" in conditions:
                                    if result_dict.get("lead_score", 0) < conditions["min_lead_score"]:
                                        should_trigger = False
                                
                                # Check platform condition
                                if "platforms" in conditions:
                                    if result_dict.get("platform") not in conditions["platforms"]:
                                        should_trigger = False
                                
                                # Check business type condition
                                if "business_types" in conditions:
                                    if result_dict.get("business_type") not in conditions["business_types"]:
                                        should_trigger = False
                                
                                if should_trigger:
                                    # Execute workflow in background
                                    import threading
                                    def execute_workflow():
                                        try:
                                            workflow_engine.execute_workflow(workflow, result_dict)
                                        except Exception as e:
                                            print(f"[WORKFLOW] Error executing workflow {workflow.workflow_id}: {e}")
                                    
                                    thread = threading.Thread(target=execute_workflow, daemon=True)
                                    thread.start()
                    finally:
                        db.close()
            except Exception as e:
                # Log but don't fail - workflow execution is non-critical
                print(f"[WORKFLOW] Error triggering workflows: {e}")
            
            self._broadcast_result(task_id, scrape_result)
        
        def on_finish():
            task["status"] = "completed"
            task["completed_at"] = datetime.datetime.now()
            self._broadcast_log(task_id, "[DONE] Scraping completed")
            self._broadcast_task_event(task_id, "task_completed", {
                "task_id": task_id,
                "status": "completed",
                "completed_at": task["completed_at"].isoformat() if task["completed_at"] else None,
                "total_results": task["total_results"]
            })
            # Send push notification for task completion
            self._send_push_notification(
                task_id=task_id,
                user_id=task.get("user_id"),
                event_type="task_completion",
                title="Task Completed",
                body=f"Scraping task completed with {task['total_results']} results",
                data={"task_id": task_id, "total_results": task["total_results"]}
            )
        
        # Start orchestrator in background thread
        def run_scraper():
            try:
                run_orchestrator(
                    config_path=task["config_path"],
                    queries_list=request.queries,
                    enabled_platforms=request.platforms,
                    skip_gmaps="google_maps" not in request.platforms,
                    max_results_override=request.max_results,
                    on_log=on_log,
                    on_progress=on_progress,
                    on_result=on_result,
                    on_finish=on_finish,
                    stop_flag=stop_flag,
                    pause_flag=pause_flag,
                    phone_only=request.phone_only or False,
                )
            except Exception as e:
                task["status"] = "error"
                task["error"] = str(e)
                task["completed_at"] = datetime.datetime.now()
                self._broadcast_log(task_id, f"[ERROR] {str(e)}")
                self._broadcast_task_event(task_id, "task_error", {
                    "task_id": task_id,
                    "status": "error",
                    "error": str(e),
                    "completed_at": task["completed_at"].isoformat() if task["completed_at"] else None
                })
                # Send push notification for task error
                self._send_push_notification(
                    task_id=task_id,
                    user_id=task.get("user_id"),
                    event_type="task_errors",
                    title="Task Error",
                    body=f"Scraping task encountered an error: {str(e)[:100]}",
                    data={"task_id": task_id, "error": str(e)}
                )
        
        thread = threading.Thread(target=run_scraper, daemon=True)
        thread.start()
        task["thread"] = thread
        
        # Broadcast task started event
        self._broadcast_task_event(task_id, "task_started", {
            "task_id": task_id,
            "status": "running",
            "started_at": task["started_at"].isoformat() if task["started_at"] else None,
            "queries": task["queries"]
        })
    
    def stop_task(self, task_id: str):
        """Stop a running task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        if task["status"] == "running":
            task["stop_flag"].set()
            task["status"] = "stopped"
            task["completed_at"] = datetime.datetime.now()
            self._broadcast_task_event(task_id, "task_stopped", {
                "task_id": task_id,
                "status": "stopped",
                "completed_at": task["completed_at"].isoformat() if task["completed_at"] else None
            })
    
    def pause_task(self, task_id: str):
        """Pause a running task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        if task["status"] == "running":
            task["status"] = "paused"
            pause_flag = task.get("pause_flag")
            if pause_flag:
                pause_flag.request_pause()
            self._broadcast_task_event(task_id, "task_paused", {
                "task_id": task_id,
                "status": "paused"
            })
            # Send push notification for task paused
            self._send_push_notification(
                task_id=task_id,
                user_id=task.get("user_id"),
                event_type="task_paused",
                title="Task Paused",
                body=f"Scraping task {task_id[:8]}... has been paused",
                data={"task_id": task_id}
            )
    
    def resume_task(self, task_id: str):
        """Resume a paused task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        if task["status"] == "paused":
            task["status"] = "running"
            pause_flag = task.get("pause_flag")
            if pause_flag:
                pause_flag.request_resume()
            self._broadcast_task_event(task_id, "task_resumed", {
                "task_id": task_id,
                "status": "running"
            })
            # Send push notification for task resumed
            self._send_push_notification(
                task_id=task_id,
                user_id=task.get("user_id"),
                event_type="task_resumed",
                title="Task Resumed",
                body=f"Scraping task {task_id[:8]}... has been resumed",
                data={"task_id": task_id}
            )
    
    def get_task_status(self, task_id: str, user_id: Optional[str] = None) -> Optional[TaskStatus]:
        """Get task status."""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        
        # Check user ownership if user_id provided
        if user_id and task.get("user_id") != user_id:
            return None  # Task belongs to different user
        
        return TaskStatus(
            task_id=task_id,
            status=task["status"],
            progress=task["progress"],
            total_results=task["total_results"],
            current_query=task["current_query"],
            current_platform=task["current_platform"],
            started_at=task["started_at"],
            completed_at=task["completed_at"],
            error=task["error"],
        )
    
    def get_user_tasks(self, user_id: str) -> List[Dict]:
        """Get all tasks for a user."""
        return [
            {
                "task_id": task_id,
                "status": task["status"],
                "progress": task["progress"],
                "total_results": task["total_results"],
                "started_at": task["started_at"],
                "completed_at": task.get("completed_at"),
            }
            for task_id, task in self.tasks.items()
            if task.get("user_id") == user_id
        ]
    
    def _dict_to_scrape_result(self, result_dict: Dict) -> ScrapeResult:
        """Convert result dict to ScrapeResult schema."""
        # Extract phone data if available
        phones = []
        if "phones" in result_dict and isinstance(result_dict["phones"], list):
            from backend.models.schemas import PhoneData
            for phone_dict in result_dict["phones"]:
                if isinstance(phone_dict, dict):
                    try:
                        phones.append(PhoneData(**phone_dict))
                    except Exception as e:
                        import logging
                        logging.debug(f"Error parsing phone data: {e}")
        
        # Parse extracted_at timestamp
        extracted_at = None
        if "extracted_at" in result_dict and result_dict["extracted_at"] != "N/A":
            try:
                if isinstance(result_dict["extracted_at"], str):
                    extracted_at = datetime.datetime.fromisoformat(result_dict["extracted_at"].replace("Z", "+00:00"))
                else:
                    extracted_at = result_dict["extracted_at"]
            except:
                extracted_at = datetime.datetime.now()
        else:
            extracted_at = datetime.datetime.now()
        
        return ScrapeResult(
            search_query=result_dict.get("Search Query", ""),
            platform=result_dict.get("Platform", ""),
            profile_url=result_dict.get("Profile URL", ""),
            handle=result_dict.get("Handle"),
            display_name=result_dict.get("Display Name"),
            bio_about=result_dict.get("Bio/About"),
            website=result_dict.get("Website"),
            email=result_dict.get("Email"),
            phone=result_dict.get("Phone"),  # Legacy field
            followers=result_dict.get("Followers"),
            location=result_dict.get("Location"),
            phones=phones,
            business_type=result_dict.get("business_type"),
            industry=result_dict.get("industry"),
            city=result_dict.get("city"),
            region=result_dict.get("region"),
            country=result_dict.get("country"),
            job_title=result_dict.get("job_title"),
            seniority_level=result_dict.get("seniority_level"),
            education_level=result_dict.get("education_level"),
            institution_name=result_dict.get("institution_name"),
            lead_type=result_dict.get("lead_type"),
            field_of_study=result_dict.get("field_of_study"),
            degree_program=result_dict.get("degree_program"),
            graduation_year=result_dict.get("graduation_year"),
            extracted_at=extracted_at,
        )
    
    def _broadcast_log(self, task_id: str, message: str):
        """Broadcast log message to WebSocket connections."""
        if task_id in self.websocket_connections["logs"]:
            log_msg = LogMessage(level="INFO", message=message)
            for ws in self.websocket_connections["logs"][task_id]:
                try:
                    ws.send_text(log_msg.model_dump_json())
                except:
                    pass  # Connection closed
    
    def _broadcast_progress(self, task_id: str, progress: Dict[str, int]):
        """Broadcast progress update to WebSocket connections."""
        if task_id in self.websocket_connections["progress"]:
            task = self.tasks[task_id]
            progress_update = ProgressUpdate(
                platform=task["current_platform"] or "",
                count=sum(progress.values()),
                total_queries=len(task["queries"]),
                current_query_index=0,  # Would need to track this
                current_query=task["current_query"] or "",
            )
            for ws in self.websocket_connections["progress"][task_id]:
                try:
                    ws.send_text(progress_update.model_dump_json())
                except:
                    pass  # Connection closed
    
    def _broadcast_result(self, task_id: str, result: ScrapeResult):
        """Broadcast result to WebSocket connections."""
        if task_id in self.websocket_connections["results"]:
            for ws in self.websocket_connections["results"][task_id]:
                try:
                    ws.send_text(result.model_dump_json())
                except:
                    pass  # Connection closed
    
    def _broadcast_task_event(self, task_id: str, event_type: str, data: Dict):
        """Broadcast task lifecycle event to all connected WebSocket clients."""
        message = json.dumps({
            "type": event_type,
            "data": data
        })
        
        # Broadcast to all WebSocket types
        for ws_type in ["logs", "progress", "results"]:
            if task_id in self.websocket_connections[ws_type]:
                disconnected = []
                for ws in self.websocket_connections[ws_type][task_id]:
                    try:
                        # Use asyncio to send message (WebSocket.send_text is async)
                        try:
                            loop = asyncio.get_event_loop()
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                        
                        if loop.is_running():
                            # Schedule coroutine
                            asyncio.ensure_future(ws.send_text(message))
                        else:
                            # Run in event loop
                            loop.run_until_complete(ws.send_text(message))
                    except Exception:
                        disconnected.append(ws)
                
                # Remove disconnected WebSockets
                for ws in disconnected:
                    if ws in self.websocket_connections[ws_type][task_id]:
                        self.websocket_connections[ws_type][task_id].remove(ws)
    
    def register_websocket(self, task_id: str, ws_type: str, websocket):
        """Register a WebSocket connection."""
        if task_id not in self.websocket_connections[ws_type]:
            self.websocket_connections[ws_type][task_id] = []
        self.websocket_connections[ws_type][task_id].append(websocket)
    
    def unregister_websocket(self, task_id: str, ws_type: str, websocket):
        """Unregister a WebSocket connection."""
        if task_id in self.websocket_connections[ws_type]:
            if websocket in self.websocket_connections[ws_type][task_id]:
                self.websocket_connections[ws_type][task_id].remove(websocket)
    
    def _send_push_notification(
        self,
        task_id: str,
        user_id: Optional[str],
        event_type: str,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ):
        """
        Send push notification based on user preferences.
        
        Args:
            task_id: Task ID
            user_id: Optional user ID
            event_type: Event type (task_completion, task_errors, task_paused, task_resumed)
            title: Notification title
            body: Notification body
            data: Optional notification data
        """
        try:
            from backend.services.push_service import get_push_service
            push_service = get_push_service()
            
            # Get user's subscriptions
            subscriptions = push_service.get_subscriptions(user_id=user_id)
            
            for subscription in subscriptions:
                if subscription.is_active != "true":
                    continue
                
                # Check user preferences
                prefs = subscription.notification_preferences or {}
                preference_key = event_type.replace("task_", "")
                
                # Check if user wants notifications for this event type
                if not prefs.get(preference_key, True):
                    continue  # User has disabled this notification type
                
                # Send notification
                push_service.send_notification(
                    subscription=subscription,
                    title=title,
                    body=body,
                    icon="/icon-192.png",
                    badge="/icon-192.png",
                    data=data or {},
                    tag=f"task-{task_id}",
                    require_interaction=False
                )
        except Exception as e:
            # Don't fail task if push notification fails
            print(f"[PUSH] Error sending push notification: {e}")


# Global task manager instance
task_manager = TaskManager()

