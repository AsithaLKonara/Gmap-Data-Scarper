
import csv
import os
import sys
import json
from datetime import datetime

# Force SQLite for this script
os.environ['DATABASE_URL'] = 'sqlite:///./leadtap.db'

# Add backend to sys.path to import modules
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from models import SocialMediaLeads, LeadSources, LeadCollections

def import_leads():
    csv_file = "sri_lanka_ict_students_final.csv"
    if not os.path.exists(csv_file):
        print(f"❌ File {csv_file} not found.")
        return

    db = SessionLocal()
    try:
        # 1. Ensure Lead Source exists
        source_name = "LinkedIn Student Search"
        source = db.query(LeadSources).filter(LeadSources.name == source_name).first()
        if not source:
            source = LeadSources(
                name=source_name,
                type="social",
                config=json.dumps({"platform": "linkedin", "target": "students"})
            )
            db.add(source)
            db.commit()
            db.refresh(source)
            print(f"✅ Created Lead Source: {source_name}")

        # 2. Ensure Lead Collection exists
        collection_name = "ICT Students SL (Automated)"
        collection = db.query(LeadCollections).filter(LeadCollections.name == collection_name).first()
        if not collection:
            collection = LeadCollections(
                name=collection_name,
                user_id=1,  # Default user
                source_id=source.id,
                description="Leads collected via automated X-Ray search on LinkedIn",
                config=json.dumps({"type": "automated_script"})
            )
            db.add(collection)
            db.commit()
            db.refresh(collection)
            print(f"✅ Created Lead Collection: {collection_name}")

        # 3. Import Leads
        print(f"🚀 Importing leads from {csv_file}...")
        count = 0
        duplicates = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Check for duplicate by profile link
                profile_url = row.get("Profile Link")
                existing = db.query(SocialMediaLeads).filter(SocialMediaLeads.profile_url == profile_url).first()
                if existing:
                    duplicates += 1
                    continue

                lead = SocialMediaLeads(
                    user_id=1,
                    platform="linkedin",
                    display_name=row.get("Name"),
                    email=row.get("Email") if row.get("Email") != "N/A" else None,
                    phone=row.get("Phone") if row.get("Phone") != "N/A" else None,
                    bio=row.get("Snippet"),
                    profile_url=profile_url,
                    collection_id=collection_id if 'collection_id' in locals() else collection.id,
                    status="new",
                    tags=json.dumps([row.get("Query")]),
                    notes=f"Source Query: {row.get('Query')}"
                )
                db.add(lead)
                count += 1
                
                # Commit in batches
                if count % 50 == 0:
                    db.commit()
                    print(f"  Processed {count} leads...")

        db.commit()
        print(f"✅ Final Result: {count} new leads imported, {duplicates} duplicates skipped.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during import: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_leads()
