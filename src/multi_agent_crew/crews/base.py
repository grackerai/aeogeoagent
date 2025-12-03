"""Base crew class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from crewai import Crew, Process

from ..core.observability import get_observability


class BaseCrew(ABC):
    """Abstract base class for crews."""
    
    def __init__(self):
        self.obs = get_observability()
    
    @abstractmethod
    def create(self) -> Crew:
        """Create the CrewAI Crew instance."""
        pass
    
    def run(self, inputs: Dict[str, Any]) -> Any:
        """Run the crew with observability."""
        crew_name = self.__class__.__name__
        
        with self.obs.trace(f"crew_run_{crew_name}", crew=crew_name):
            self.obs.log("INFO", f"Starting crew {crew_name}")
            
            try:
                crew = self.create()
                result = crew.kickoff(inputs=inputs)
                
                self.obs.record_metric("crew_run_success", 1, {"crew": crew_name})
                self.obs.log("INFO", f"Crew {crew_name} finished successfully")
                return result
                
            except Exception as e:
                self.obs.record_metric("crew_run_error", 1, {"crew": crew_name})
                self.obs.log("ERROR", f"Crew {crew_name} failed: {str(e)}")
                raise
