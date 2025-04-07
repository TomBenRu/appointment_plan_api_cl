from typing import List, Optional, Dict, Any
from uuid import UUID

from pony.orm import db_session, select

from api.models import schemas
from database.models import Plan as DBPlan
from database.models import PlanPeriod as DBPlanPeriod


class PlanService:
    @staticmethod
    @db_session
    def get_all_plans() -> List[schemas.PlanDetail]:
        """
        Liefert eine Liste aller Pläne.
        """
        # Alle Pläne aus der Datenbank laden und nach Planperiode gruppieren
        all_plans = DBPlan.select().order_by(lambda p: p.plan_period.start_date)
        return [schemas.PlanDetail.model_validate(p) for p in all_plans]
    
    @staticmethod
    @db_session
    def get_plans_by_period(plan_period_id: UUID) -> List[schemas.PlanDetail]:
        """
        Liefert eine Liste aller Pläne für eine bestimmte Planungsperiode.
        """
        plans = DBPlan.select(lambda p: p.plan_period.id == plan_period_id).order_by(lambda p: p.name)
        return [schemas.PlanDetail.model_validate(p) for p in plans]
    
    @staticmethod
    @db_session
    def get_plan_detail(plan_id: UUID) -> Optional[schemas.PlanDetail]:
        """
        Liefert Details zu einem bestimmten Plan oder None, wenn nicht gefunden.
        """
        plan = DBPlan.get(id=plan_id)
        if not plan:
            return None
        
        plan_detail = schemas.PlanDetail.model_validate(plan)
        # Sortiere die Termine nach Datum und Startzeit
        plan_detail.appointments.sort(key=lambda a: (a.date, a.start_time))
        
        return plan_detail
    
    @staticmethod
    @db_session
    def get_all_plan_periods() -> List[schemas.PlanPeriod]:
        """
        Liefert eine Liste aller Planungsperioden.
        """
        plan_periods = DBPlanPeriod.select().order_by(lambda pp: pp.start_date)
        return [schemas.PlanPeriod.model_validate(pp) for pp in plan_periods]
    
    @staticmethod
    @db_session
    def get_plan_period(plan_period_id: UUID) -> Optional[schemas.PlanPeriod]:
        """
        Liefert Details zu einer bestimmten Planungsperiode oder None, wenn nicht gefunden.
        """
        plan_period = DBPlanPeriod.get(id=plan_period_id)
        if not plan_period:
            return None
        
        return schemas.PlanPeriod.model_validate(plan_period)
    
    @staticmethod
    @db_session
    def search_plans(search_term: str, limit: int = 20) -> List[schemas.PlanDetail]:
        """
        Durchsucht Pläne nach dem angegebenen Suchbegriff.
        """
        search_term_lower = search_term.lower()
        
        plans = DBPlan.select(
            lambda p: search_term_lower in p.name.lower() or
                     (p.notes and search_term_lower in p.notes.lower()) or
                     search_term_lower in p.plan_period.name.lower()
        ).order_by(lambda p: p.plan_period.start_date)[:limit]
        
        return [schemas.PlanDetail.model_validate(p) for p in plans]
