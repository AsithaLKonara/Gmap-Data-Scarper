"""Data aggregation service for daily/weekly/monthly summaries."""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import os
import csv
from pathlib import Path


class DataAggregationService:
    """Aggregates data for daily/weekly/monthly summaries and comparisons."""
    
    def __init__(self):
        """Initialize data aggregation service."""
        self.output_dir = Path(os.path.expanduser("~/Documents/social_leads"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_daily_summary(
        self,
        date: Optional[datetime] = None,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Get daily summary for a date or range of days.
        
        Args:
            date: Specific date (None = today)
            days_back: Number of days to include (if date is None)
        
        Returns:
            Dict with daily summary statistics
        """
        if date is None:
            # Get last N days
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back - 1)
        else:
            start_date = date.date()
            end_date = start_date
        
        daily_stats = defaultdict(lambda: {
            "leads": 0,
            "phones": 0,
            "platforms": defaultdict(int),
            "categories": defaultdict(int)
        })
        
        csv_files = list(self.output_dir.glob("*.csv"))
        
        for csv_file in csv_files:
            try:
                with open(csv_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        extracted_at = row.get("extracted_at") or row.get("Extracted At", "")
                        if extracted_at and extracted_at != "N/A":
                            try:
                                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                                    try:
                                        record_date = datetime.strptime(extracted_at.split(".")[0], fmt).date()
                                        if start_date <= record_date <= end_date:
                                            date_key = record_date.strftime("%Y-%m-%d")
                                            daily_stats[date_key]["leads"] += 1
                                            
                                            phone = row.get("Phone") or row.get("phone", "")
                                            if phone and phone != "N/A":
                                                daily_stats[date_key]["phones"] += 1
                                            
                                            platform = row.get("Platform", "unknown")
                                            daily_stats[date_key]["platforms"][platform] += 1
                                            
                                            category = row.get("Category") or row.get("business_type", "unknown")
                                            daily_stats[date_key]["categories"][category] += 1
                                        break
                                    except ValueError:
                                        continue
                            except Exception as e:
                                import logging
                                logging.debug(f"Error processing CSV row for daily aggregation: {e}")
            except Exception:
                continue
        
        # Convert to list format
        summary = []
        for date_key in sorted(daily_stats.keys()):
            stats = daily_stats[date_key]
            summary.append({
                "date": date_key,
                "leads": stats["leads"],
                "phones": stats["phones"],
                "phone_rate": round((stats["phones"] / stats["leads"] * 100) if stats["leads"] > 0 else 0, 2),
                "platforms": dict(stats["platforms"]),
                "categories": dict(stats["categories"])
            })
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "daily_summary": summary,
            "total_leads": sum(s["leads"] for s in summary),
            "total_phones": sum(s["phones"] for s in summary)
        }
    
    def get_weekly_summary(
        self,
        weeks_back: int = 4
    ) -> Dict[str, Any]:
        """
        Get weekly summary for last N weeks.
        
        Args:
            weeks_back: Number of weeks to include
        
        Returns:
            Dict with weekly summary statistics
        """
        weekly_stats = defaultdict(lambda: {
            "leads": 0,
            "phones": 0,
            "platforms": defaultdict(int),
            "categories": defaultdict(int),
            "days": []
        })
        
        csv_files = list(self.output_dir.glob("*.csv"))
        
        for csv_file in csv_files:
            try:
                with open(csv_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        extracted_at = row.get("extracted_at") or row.get("Extracted At", "")
                        if extracted_at and extracted_at != "N/A":
                            try:
                                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                                    try:
                                        record_date = datetime.strptime(extracted_at.split(".")[0], fmt)
                                        
                                        # Calculate week (ISO week)
                                        year, week, _ = record_date.isocalendar()
                                        week_key = f"{year}-W{week:02d}"
                                        
                                        # Check if within range
                                        cutoff_date = datetime.now() - timedelta(weeks=weeks_back)
                                        if record_date >= cutoff_date:
                                            weekly_stats[week_key]["leads"] += 1
                                            
                                            phone = row.get("Phone") or row.get("phone", "")
                                            if phone and phone != "N/A":
                                                weekly_stats[week_key]["phones"] += 1
                                            
                                            platform = row.get("Platform", "unknown")
                                            weekly_stats[week_key]["platforms"][platform] += 1
                                            
                                            category = row.get("Category") or row.get("business_type", "unknown")
                                            weekly_stats[week_key]["categories"][category] += 1
                                            
                                            date_str = record_date.strftime("%Y-%m-%d")
                                            if date_str not in weekly_stats[week_key]["days"]:
                                                weekly_stats[week_key]["days"].append(date_str)
                                        break
                                    except ValueError:
                                        continue
                            except Exception as e:
                                import logging
                                logging.debug(f"Error processing CSV row for weekly aggregation: {e}")
            except Exception:
                continue
        
        # Convert to list format
        summary = []
        for week_key in sorted(weekly_stats.keys()):
            stats = weekly_stats[week_key]
            summary.append({
                "week": week_key,
                "leads": stats["leads"],
                "phones": stats["phones"],
                "phone_rate": round((stats["phones"] / stats["leads"] * 100) if stats["leads"] > 0 else 0, 2),
                "platforms": dict(stats["platforms"]),
                "categories": dict(stats["categories"]),
                "days": len(stats["days"])
            })
        
        return {
            "weeks_back": weeks_back,
            "weekly_summary": summary,
            "total_leads": sum(s["leads"] for s in summary),
            "total_phones": sum(s["phones"] for s in summary)
        }
    
    def get_monthly_summary(
        self,
        months_back: int = 6
    ) -> Dict[str, Any]:
        """
        Get monthly summary for last N months.
        
        Args:
            months_back: Number of months to include
        
        Returns:
            Dict with monthly summary statistics
        """
        monthly_stats = defaultdict(lambda: {
            "leads": 0,
            "phones": 0,
            "platforms": defaultdict(int),
            "categories": defaultdict(int)
        })
        
        csv_files = list(self.output_dir.glob("*.csv"))
        
        for csv_file in csv_files:
            try:
                with open(csv_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        extracted_at = row.get("extracted_at") or row.get("Extracted At", "")
                        if extracted_at and extracted_at != "N/A":
                            try:
                                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                                    try:
                                        record_date = datetime.strptime(extracted_at.split(".")[0], fmt)
                                        
                                        month_key = record_date.strftime("%Y-%m")
                                        
                                        # Check if within range
                                        cutoff_date = datetime.now() - timedelta(days=months_back * 30)
                                        if record_date >= cutoff_date:
                                            monthly_stats[month_key]["leads"] += 1
                                            
                                            phone = row.get("Phone") or row.get("phone", "")
                                            if phone and phone != "N/A":
                                                monthly_stats[month_key]["phones"] += 1
                                            
                                            platform = row.get("Platform", "unknown")
                                            monthly_stats[month_key]["platforms"][platform] += 1
                                            
                                            category = row.get("Category") or row.get("business_type", "unknown")
                                            monthly_stats[month_key]["categories"][category] += 1
                                        break
                                    except ValueError:
                                        continue
                            except Exception as e:
                                import logging
                                logging.debug(f"Error processing CSV row for monthly aggregation: {e}")
            except Exception:
                continue
        
        # Convert to list format
        summary = []
        for month_key in sorted(monthly_stats.keys()):
            stats = monthly_stats[month_key]
            summary.append({
                "month": month_key,
                "leads": stats["leads"],
                "phones": stats["phones"],
                "phone_rate": round((stats["phones"] / stats["leads"] * 100) if stats["leads"] > 0 else 0, 2),
                "platforms": dict(stats["platforms"]),
                "categories": dict(stats["categories"])
            })
        
        return {
            "months_back": months_back,
            "monthly_summary": summary,
            "total_leads": sum(s["leads"] for s in summary),
            "total_phones": sum(s["phones"] for s in summary)
        }
    
    def compare_periods(
        self,
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime
    ) -> Dict[str, Any]:
        """
        Compare two time periods.
        
        Args:
            period1_start: Start of first period
            period1_end: End of first period
            period2_start: Start of second period
            period2_end: End of second period
        
        Returns:
            Dict with comparison statistics
        """
        def get_period_stats(start: datetime, end: datetime) -> Dict[str, Any]:
            stats = {
                "leads": 0,
                "phones": 0,
                "platforms": defaultdict(int),
                "categories": defaultdict(int)
            }
            
            csv_files = list(self.output_dir.glob("*.csv"))
            
            for csv_file in csv_files:
                try:
                    with open(csv_file, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            extracted_at = row.get("extracted_at") or row.get("Extracted At", "")
                            if extracted_at and extracted_at != "N/A":
                                try:
                                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                                        try:
                                            record_date = datetime.strptime(extracted_at.split(".")[0], fmt)
                                            if start <= record_date <= end:
                                                stats["leads"] += 1
                                                
                                                phone = row.get("Phone") or row.get("phone", "")
                                                if phone and phone != "N/A":
                                                    stats["phones"] += 1
                                                
                                                platform = row.get("Platform", "unknown")
                                                stats["platforms"][platform] += 1
                                                
                                                category = row.get("Category") or row.get("business_type", "unknown")
                                                stats["categories"][category] += 1
                                            break
                                        except ValueError:
                                            continue
                                except Exception as e:
                                    import logging
                                    logging.debug(f"Error processing CSV row for period comparison: {e}")
                except Exception:
                    continue
            
            return {
                "leads": stats["leads"],
                "phones": stats["phones"],
                "phone_rate": round((stats["phones"] / stats["leads"] * 100) if stats["leads"] > 0 else 0, 2),
                "platforms": dict(stats["platforms"]),
                "categories": dict(stats["categories"])
            }
        
        period1_stats = get_period_stats(period1_start, period1_end)
        period2_stats = get_period_stats(period2_start, period2_end)
        
        # Calculate changes
        leads_change = period2_stats["leads"] - period1_stats["leads"]
        leads_change_pct = round((leads_change / period1_stats["leads"] * 100) if period1_stats["leads"] > 0 else 0, 2)
        
        phones_change = period2_stats["phones"] - period1_stats["phones"]
        phones_change_pct = round((phones_change / period1_stats["phones"] * 100) if period1_stats["phones"] > 0 else 0, 2)
        
        return {
            "period1": {
                "start": period1_start.isoformat(),
                "end": period1_end.isoformat(),
                "stats": period1_stats
            },
            "period2": {
                "start": period2_start.isoformat(),
                "end": period2_end.isoformat(),
                "stats": period2_stats
            },
            "comparison": {
                "leads_change": leads_change,
                "leads_change_percent": leads_change_pct,
                "phones_change": phones_change,
                "phones_change_percent": phones_change_pct
            }
        }


# Global instance
_data_aggregation_service = None

def get_data_aggregation_service() -> DataAggregationService:
    """Get or create global data aggregation service instance."""
    global _data_aggregation_service
    if _data_aggregation_service is None:
        _data_aggregation_service = DataAggregationService()
    return _data_aggregation_service

