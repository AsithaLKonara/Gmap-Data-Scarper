"""Service for managing search templates."""
from typing import List, Dict, Any, Optional
import yaml
import os
from pathlib import Path


class TemplateService:
    """Service for loading and managing search templates."""
    
    def __init__(self, templates_file: Optional[str] = None):
        """
        Initialize template service.
        
        Args:
            templates_file: Path to templates YAML file. If None, uses default.
        """
        if templates_file is None:
            templates_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "backend",
                "data",
                "search_templates.yaml"
            )
        self.templates_file = Path(templates_file)
        self._templates = None
    
    def load_templates(self) -> List[Dict[str, Any]]:
        """
        Load templates from YAML file.
        
        Returns:
            List of template dictionaries
        """
        if self._templates is not None:
            return self._templates
        
        if not self.templates_file.exists():
            print(f"[TEMPLATE] Templates file not found: {self.templates_file}")
            return []
        
        try:
            with open(self.templates_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self._templates = data.get("templates", [])
                return self._templates
        except Exception as e:
            print(f"[TEMPLATE] Error loading templates: {e}")
            return []
    
    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific template by name.
        
        Args:
            name: Template name
            
        Returns:
            Template dictionary or None
        """
        templates = self.load_templates()
        for template in templates:
            if template.get("name") == name:
                return template
        return None
    
    def apply_template(
        self,
        template_name: str,
        variables: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Apply a template with variable substitution.
        
        Args:
            template_name: Name of the template
            variables: Dictionary of variables to substitute (e.g., {"location": "Toronto", "field": "ICT"})
            
        Returns:
            Applied template configuration or None
        """
        template = self.get_template(template_name)
        if not template:
            return None
        
        # Deep copy template
        import copy
        applied = copy.deepcopy(template)
        
        # Substitute variables in queries
        if "queries" in applied:
            applied["queries"] = [
                query.format(**variables) if "{" in query else query
                for query in applied["queries"]
            ]
        
        # Substitute variables in filters
        if "filters" in applied:
            filters = applied["filters"]
            for key, value in filters.items():
                if isinstance(value, str) and "{" in value:
                    filters[key] = value.format(**variables)
                elif isinstance(value, list):
                    filters[key] = [
                        v.format(**variables) if isinstance(v, str) and "{" in v else v
                        for v in value
                    ]
        
        return applied
    
    def list_templates(self) -> List[Dict[str, str]]:
        """
        List all available templates with name and description.
        
        Returns:
            List of template summaries
        """
        templates = self.load_templates()
        return [
            {
                "name": t.get("name", ""),
                "description": t.get("description", ""),
                "lead_objective": t.get("lead_objective")
            }
            for t in templates
        ]


# Global instance
template_service = TemplateService()

