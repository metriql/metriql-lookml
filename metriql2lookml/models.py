from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field


# Looker file types
class LookViewFile(BaseModel):
    filename: str
    contents: str


class LookModelFile(BaseModel):
    filename: str
    contents: str


class TargetValue(BaseModel):
    database: str
    db_schema: str = Field(None, alias="schema")
    table: str


class Target(BaseModel):
    type: str
    value: TargetValue


class Mappings(BaseModel):
    userId: Optional[str] = None
    eventTimestamp: Optional[str] = None


class RelationValue(BaseModel):
    sourceColumn: str
    targetColumn: str


class Relation(BaseModel):
    name: str
    label: str
    description: Any
    relationType: str
    joinType: str
    modelName: str
    type: str
    value: RelationValue
    hidden: Any


class DimensionValue(BaseModel):
    column: Optional[str] = None
    dimension: Optional[str] = None
    sql: Optional[str] = None


class ReportOption(BaseModel):
    looker: dict


class Dimension(BaseModel):
    name: str
    type: str
    value: DimensionValue
    description: str
    label: Any
    category: Any
    primary: Any
    pivot: Any
    suggestions: Any
    postOperations: Optional[List[str]]
    fieldType: str
    reportOptions: Optional[ReportOption]
    hidden: Any
    drills: Any


class MeasureValue(BaseModel):
    aggregation: Optional[str]
    column: Optional[str] = None
    dimension: Optional[str] = None
    sql: Optional[str] = None


class Measure(BaseModel):
    name: str
    label: Any
    description: Optional[str]
    category: Any
    type: str
    value: MeasureValue
    filters: Any
    reportOptions: Optional[ReportOption]
    fieldType: str
    hidden: Any
    drills: Any


class MaterializeValue(BaseModel):
    measures: List[str]
    dimensions: List[str]
    filters: Any


class Materialize(BaseModel):
    name: str
    reportType: str
    value: MaterializeValue


class MetriqlModel(BaseModel):
    name: str
    hidden: bool
    target: Target
    label: str
    description: str
    category: Any
    mappings: Mappings
    relations: List[Relation]
    dimensions: List[Dimension]
    measures: List[Measure]
    materializes: List[Materialize]
    alwaysFilters: Any
    id: int
    recipeId: int
    recipePath: str
