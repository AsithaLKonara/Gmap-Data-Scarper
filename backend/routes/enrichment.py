"""Enrichment endpoints for phone verification and business enrichment."""
from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Optional, List, Dict, Any
from backend.services.phone_verifier import get_phone_verifier
from backend.services.enrichment_service import get_enrichment_service
from backend.services.ai_enhancement import get_ai_enhancement_service
from backend.middleware.auth import get_optional_user

router = APIRouter(prefix="/api/enrichment", tags=["enrichment"])


@router.post("/verify-phone")
async def verify_phone(
    phone_number: str = Query(..., description="Phone number in E.164 format (e.g., +15551234567)"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Verify a phone number using Twilio Lookup API."""
    try:
        verifier = get_phone_verifier()
        result = verifier.verify(phone_number)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phone verification failed: {str(e)}")


@router.post("/verify-phones")
async def verify_phones_batch(
    phone_numbers: List[str],
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Verify multiple phone numbers in batch."""
    try:
        verifier = get_phone_verifier()
        results = {}
        for phone in phone_numbers:
            try:
                results[phone] = verifier.verify(phone)
            except Exception as e:
                results[phone] = {"error": str(e)}
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch phone verification failed: {str(e)}")


@router.post("/enrich-business")
async def enrich_business(
    business_name: str = Query(..., description="Name of the business"),
    website: Optional[str] = Query(None, description="Business website URL"),
    location: Optional[str] = Query(None, description="Business location"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Enrich business data with company information."""
    try:
        enrichment_service = get_enrichment_service()
        result = enrichment_service.enrich_business(
            business_name=business_name,
            website=website,
            location=location
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Business enrichment failed: {str(e)}")


@router.post("/enrich-lead")
async def enrich_lead(
    business_name: str = Query(..., description="Name of the business"),
    phone_number: Optional[str] = Query(None, description="Phone number in E.164 format"),
    website: Optional[str] = Query(None, description="Business website URL"),
    location: Optional[str] = Query(None, description="Business location"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Enrich a complete lead with phone verification and business enrichment."""
    try:
        result = {
            "business_name": business_name,
            "phone_verification": None,
            "business_enrichment": None,
            "ai_enhancement": None
        }
        
        # Verify phone if provided
        if phone_number:
            verifier = get_phone_verifier()
            result["phone_verification"] = verifier.verify(phone_number)
        
        # Enrich business
        enrichment_service = get_enrichment_service()
        result["business_enrichment"] = enrichment_service.enrich_business(
            business_name=business_name,
            website=website,
            location=location
        )
        
        # AI enhancement
        ai_service = get_ai_enhancement_service()
        result["ai_enhancement"] = {
            "business_description": ai_service.generate_business_description(
                business_name=business_name,
                industry=result["business_enrichment"].get("industry"),
                location=location,
                website=website,
                additional_info=result["business_enrichment"]
            ),
            "quality_assessment": ai_service.assess_lead_quality(
                business_name=business_name,
                phone_number=phone_number,
                website=website,
                enrichment_data=result["business_enrichment"],
                phone_verification=result["phone_verification"]
            ),
            "key_insights": ai_service.extract_key_insights(
                business_name=business_name,
                enrichment_data=result["business_enrichment"],
                phone_verification=result["phone_verification"]
            )
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lead enrichment failed: {str(e)}")


@router.post("/assess-quality")
async def assess_lead_quality(
    data: Dict[str, Any] = Body(..., description="Lead data for quality assessment"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Assess lead quality and generate quality score."""
    try:
        ai_service = get_ai_enhancement_service()
        result = ai_service.assess_lead_quality(
            business_name=data.get("business_name", ""),
            phone_number=data.get("phone_number"),
            website=data.get("website"),
            enrichment_data=data.get("enrichment_data"),
            phone_verification=data.get("phone_verification")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality assessment failed: {str(e)}")


@router.post("/check-duplicates")
async def check_duplicates(
    data: Dict[str, Any] = Body(..., description="Lead data to check for duplicates"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Check if a lead is a duplicate and find all potential duplicates."""
    try:
        from backend.services.duplicate_detection import get_duplicate_detection_service
        duplicate_service = get_duplicate_detection_service()
        
        task_id = data.get("task_id")
        check_across_tasks = data.get("check_across_tasks", True)
        
        is_dup, reason, existing_lead = duplicate_service.is_duplicate(
            data,
            task_id=task_id,
            check_across_tasks=check_across_tasks
        )
        
        # Find all duplicates
        all_duplicates = duplicate_service.find_duplicates(
            data,
            task_id=task_id,
            check_across_tasks=check_across_tasks
        )
        
        return {
            "is_duplicate": is_dup,
            "reason": reason,
            "existing_lead": existing_lead,
            "all_duplicates": all_duplicates,
            "duplicate_count": len(all_duplicates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Duplicate check failed: {str(e)}")


@router.post("/enrich-batch")
async def enrich_batch(
    leads: List[Dict[str, Any]] = Body(..., description="List of leads to enrich"),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Enrich multiple leads in batch."""
    try:
        verifier = get_phone_verifier()
        enrichment_service = get_enrichment_service()
        ai_service = get_ai_enhancement_service()
        
        results = []
        for lead in leads:
            enriched_lead = {
                "original": lead,
                "phone_verification": None,
                "business_enrichment": None,
                "ai_enhancement": None
            }
            
            # Verify phone
            phone = lead.get("phone") or lead.get("phone_number")
            if phone:
                try:
                    enriched_lead["phone_verification"] = verifier.verify(phone)
                except Exception as e:
                    import logging
                    logging.debug(f"Error verifying phone {phone}: {e}")
            
            # Enrich business
            business_name = lead.get("business_name") or lead.get("display_name")
            if business_name:
                try:
                    enriched_lead["business_enrichment"] = enrichment_service.enrich_business(
                        business_name=business_name,
                        website=lead.get("website"),
                        location=lead.get("location")
                    )
                except Exception as e:
                    import logging
                    logging.debug(f"Error enriching business {business_name}: {e}")
            
            # AI enhancement
            if business_name:
                try:
                    enriched_lead["ai_enhancement"] = {
                        "business_description": ai_service.generate_business_description(
                            business_name=business_name,
                            industry=enriched_lead["business_enrichment"].get("industry") if enriched_lead["business_enrichment"] else None,
                            location=lead.get("location"),
                            website=lead.get("website"),
                            additional_info=enriched_lead["business_enrichment"]
                        ),
                        "quality_assessment": ai_service.assess_lead_quality(
                            business_name=business_name,
                            phone_number=phone,
                            website=lead.get("website"),
                            enrichment_data=enriched_lead["business_enrichment"],
                            phone_verification=enriched_lead["phone_verification"]
                        )
                    }
                except Exception as e:
                    import logging
                    logging.debug(f"Error with AI enhancement for {business_name}: {e}")
            
            results.append(enriched_lead)
        
        return {
            "enriched_count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch enrichment failed: {str(e)}")

