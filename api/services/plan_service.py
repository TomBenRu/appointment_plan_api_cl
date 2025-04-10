"""
Service für Pläne mit integrierter Fehlerbehandlung.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date

from pony.orm import db_session, select, count, ObjectNotFound

from api.models import schemas
from database.models import Plan as DBPlan
from database.models import PlanPeriod as DBPlanPeriod
from api.exceptions.plan import (
    PlanNotFoundException, PlanInUseException, 
    DuplicatePlanException, PlanValidationException,
    PlanPeriodNotFoundException, PlanPeriodOverlapException
)


class PlanService:
    @staticmethod
    @db_session
    def get_all_plans() -> List[schemas.PlanDetail]:
        """
        Liefert eine Liste aller Pläne.
        
        Returns:
            Liste aller Pläne.
        """
        # Alle Pläne aus der Datenbank laden und nach Planperiode gruppieren
        all_plans = DBPlan.select().order_by(lambda p: p.plan_period.start_date)
        return [schemas.PlanDetail.model_validate(p) for p in all_plans]
    
    @staticmethod
    @db_session
    def get_plans_by_period(plan_period_id: UUID) -> List[schemas.PlanDetail]:
        """
        Liefert eine Liste aller Pläne für eine bestimmte Planungsperiode.
        
        Args:
            plan_period_id: Die UUID der Planungsperiode.
            
        Returns:
            Liste der Pläne in dieser Periode.
            
        Raises:
            PlanPeriodNotFoundException: Wenn die Planungsperiode nicht gefunden wurde.
        """
        # Prüfe, ob die Planperiode existiert
        period = DBPlanPeriod.get(id=plan_period_id)
        if not period:
            raise PlanPeriodNotFoundException(period_id=plan_period_id)
            
        plans = DBPlan.select(lambda p: p.plan_period.id == plan_period_id).order_by(lambda p: p.name)
        return [schemas.PlanDetail.model_validate(p) for p in plans]
    
    @staticmethod
    @db_session
    def get_plan_detail(plan_id: UUID) -> schemas.PlanDetail:
        """
        Liefert Details zu einem bestimmten Plan.
        
        Args:
            plan_id: Die UUID des Plans.
            
        Returns:
            Details zum Plan.
            
        Raises:
            PlanNotFoundException: Wenn der Plan nicht gefunden wurde.
        """
        try:
            plan = DBPlan.get(id=plan_id)
            if not plan:
                raise PlanNotFoundException(plan_id=plan_id)
            
            plan_detail = schemas.PlanDetail.model_validate(plan)
            # Sortiere die Termine nach Datum und Startzeit
            plan_detail.appointments.sort(key=lambda a: (a.date, a.start_time))
            
            return plan_detail
        except ObjectNotFound:
            raise PlanNotFoundException(plan_id=plan_id)
    
    @staticmethod
    @db_session
    def create_plan(plan_data: schemas.Plan) -> schemas.PlanDetail:
        """
        Erstellt einen neuen Plan.
        
        Args:
            plan_data: Die Daten für den neuen Plan.
            
        Returns:
            Der erstellte Plan.
            
        Raises:
            PlanValidationException: Wenn die Validierung fehlschlägt.
            PlanPeriodNotFoundException: Wenn die angegebene Planperiode nicht existiert.
            DuplicatePlanException: Wenn bereits ein Plan mit diesem Namen in der Periode existiert.
        """
        # Validierung
        validation_errors = {}
        if not plan_data.name or len(plan_data.name.strip()) == 0:
            validation_errors["name"] = "Der Name darf nicht leer sein."
            
        if validation_errors:
            raise PlanValidationException(errors=validation_errors)
            
        # Prüfe, ob die Planperiode existiert
        period = DBPlanPeriod.get(id=plan_data.plan_period_id)
        if not period:
            raise PlanPeriodNotFoundException(period_id=plan_data.plan_period_id)
            
        # Prüfe, ob bereits ein Plan mit diesem Namen in der Periode existiert
        existing = DBPlan.select(
            lambda p: p.name == plan_data.name and p.plan_period.id == plan_data.plan_period_id
        ).first()
        
        if existing:
            raise DuplicatePlanException(
                name=plan_data.name,
                period_id=plan_data.plan_period_id,
                existing_id=existing.id
            )
        
        # Plan erstellen
        plan = DBPlan(
            name=plan_data.name,
            notes=plan_data.notes,
            plan_period=period
        )
        
        return schemas.PlanDetail.model_validate(plan)
    
    @staticmethod
    @db_session
    def update_plan(plan_id: UUID, plan_data: schemas.Plan) -> schemas.PlanDetail:
        """
        Aktualisiert einen bestehenden Plan.
        
        Args:
            plan_id: Die UUID des zu aktualisierenden Plans.
            plan_data: Die neuen Daten für den Plan.
            
        Returns:
            Der aktualisierte Plan.
            
        Raises:
            PlanNotFoundException: Wenn der Plan nicht gefunden wurde.
            PlanValidationException: Wenn die Validierung fehlschlägt.
            PlanPeriodNotFoundException: Wenn die angegebene Planperiode nicht existiert.
            DuplicatePlanException: Wenn bereits ein anderer Plan mit diesem Namen in der Periode existiert.
        """
        # Validierung
        validation_errors = {}
        if not plan_data.name or len(plan_data.name.strip()) == 0:
            validation_errors["name"] = "Der Name darf nicht leer sein."
            
        if validation_errors:
            raise PlanValidationException(errors=validation_errors)
            
        try:
            plan = DBPlan.get(id=plan_id)
            if not plan:
                raise PlanNotFoundException(plan_id=plan_id)
                
            # Prüfe, ob die Planperiode existiert
            period = DBPlanPeriod.get(id=plan_data.plan_period_id)
            if not period:
                raise PlanPeriodNotFoundException(period_id=plan_data.plan_period_id)
                
            # Prüfe, ob bereits ein anderer Plan mit diesem Namen in der Periode existiert
            existing = DBPlan.select(
                lambda p: p.id != plan_id and
                          p.name == plan_data.name and 
                          p.plan_period.id == plan_data.plan_period_id
            ).first()
            
            if existing:
                raise DuplicatePlanException(
                    name=plan_data.name,
                    period_id=plan_data.plan_period_id,
                    existing_id=existing.id
                )
            
            # Plan aktualisieren
            plan.name = plan_data.name
            plan.notes = plan_data.notes
            plan.plan_period = period
            
            plan_detail = schemas.PlanDetail.model_validate(plan)
            # Sortiere die Termine nach Datum und Startzeit
            plan_detail.appointments.sort(key=lambda a: (a.date, a.start_time))
            
            return plan_detail
        except ObjectNotFound:
            raise PlanNotFoundException(plan_id=plan_id)
    
    @staticmethod
    @db_session
    def delete_plan(plan_id: UUID) -> bool:
        """
        Löscht einen Plan.
        
        Args:
            plan_id: Die UUID des zu löschenden Plans.
            
        Returns:
            True, wenn der Plan erfolgreich gelöscht wurde.
            
        Raises:
            PlanNotFoundException: Wenn der Plan nicht gefunden wurde.
            PlanInUseException: Wenn der Plan noch verwendet wird.
        """
        try:
            plan = DBPlan.get(id=plan_id)
            if not plan:
                raise PlanNotFoundException(plan_id=plan_id)
                
            # Prüfe, ob der Plan noch verwendet wird
            appointment_count = len(plan.appointments)
            if appointment_count > 0:
                raise PlanInUseException(
                    plan_id=plan_id,
                    reference_count=appointment_count
                )
            
            # Plan löschen
            plan.delete()
            return True
        except ObjectNotFound:
            raise PlanNotFoundException(plan_id=plan_id)
    
    @staticmethod
    @db_session
    def get_all_plan_periods() -> List[schemas.PlanPeriod]:
        """
        Liefert eine Liste aller Planungsperioden.
        
        Returns:
            Liste aller Planungsperioden.
        """
        plan_periods = DBPlanPeriod.select().order_by(lambda pp: pp.start_date)
        return [schemas.PlanPeriod.model_validate(pp) for pp in plan_periods]
    
    @staticmethod
    @db_session
    def get_plan_period(plan_period_id: UUID) -> schemas.PlanPeriod:
        """
        Liefert Details zu einer bestimmten Planungsperiode.
        
        Args:
            plan_period_id: Die UUID der Planungsperiode.
            
        Returns:
            Details zur Planungsperiode.
            
        Raises:
            PlanPeriodNotFoundException: Wenn die Planungsperiode nicht gefunden wurde.
        """
        try:
            plan_period = DBPlanPeriod.get(id=plan_period_id)
            if not plan_period:
                raise PlanPeriodNotFoundException(period_id=plan_period_id)
            
            return schemas.PlanPeriod.model_validate(plan_period)
        except ObjectNotFound:
            raise PlanPeriodNotFoundException(period_id=plan_period_id)
    
    @staticmethod
    @db_session
    def create_plan_period(period_data: schemas.PlanPeriod) -> schemas.PlanPeriod:
        """
        Erstellt eine neue Planungsperiode.
        
        Args:
            period_data: Die Daten für die neue Planungsperiode.
            
        Returns:
            Die erstellte Planungsperiode.
            
        Raises:
            PlanValidationException: Wenn die Validierung fehlschlägt.
            PlanPeriodOverlapException: Wenn sich die Periode mit einer existierenden überschneidet.
        """
        # Validierung
        validation_errors = {}
        if not period_data.name or len(period_data.name.strip()) == 0:
            validation_errors["name"] = "Der Name darf nicht leer sein."
        if period_data.start_date > period_data.end_date:
            validation_errors["date_range"] = "Das Startdatum muss vor dem Enddatum liegen."
            
        if validation_errors:
            raise PlanValidationException(errors=validation_errors)
            
        # Prüfe auf Überschneidungen mit existierenden Perioden
        overlapping = DBPlanPeriod.select(
            lambda pp: (pp.start_date <= period_data.end_date and 
                        pp.end_date >= period_data.start_date)
        ).first()
        
        if overlapping:
            raise PlanPeriodOverlapException(
                name=period_data.name,
                start_date=str(period_data.start_date),
                end_date=str(period_data.end_date),
                existing_period_id=overlapping.id
            )
        
        # Planperiode erstellen
        period = DBPlanPeriod(
            name=period_data.name,
            start_date=period_data.start_date,
            end_date=period_data.end_date
        )
        
        return schemas.PlanPeriod.model_validate(period)
    
    @staticmethod
    @db_session
    def search_plans(search_term: str, limit: int = 20) -> List[schemas.PlanDetail]:
        """
        Durchsucht Pläne nach dem angegebenen Suchbegriff.
        
        Args:
            search_term: Der Suchbegriff.
            limit: Maximale Anzahl der Ergebnisse (Standard: 20).
            
        Returns:
            Liste der passenden Pläne.
        """
        if not search_term or len(search_term.strip()) < 2:
            return []
            
        search_term_lower = search_term.lower()
        
        plans = DBPlan.select(
            lambda p: search_term_lower in p.name.lower() or
                     (p.notes and search_term_lower in p.notes.lower()) or
                     search_term_lower in p.plan_period.name.lower()
        ).order_by(lambda p: p.plan_period.start_date)[:limit]
        
        return [schemas.PlanDetail.model_validate(p) for p in plans]
