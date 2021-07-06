import lkml
from typing import List
from .models import MetriqlModel, LookViewFile, LookModelFile, Measure, Dimension

LOOKER_DTYPE_MAP = {
    "integer": "number",
    "decimal": "number",
    "double": "number",
    "long": "number",
    "boolean": "yesno",
    "string": "string",
    "timestamp": "date",
    "time": "string",
    "date": "date",
    "approximateUnique": "count_distinct",
}

looker_scalar_types = ["number", "yesno", "string"]


def lookml_view_from_metriql_model(model: MetriqlModel, models: List[MetriqlModel]):
    lookml = {
        "view": {
            "name": model.name,
            "sql_table_name": f"{model.target.value.database}.{model.target.value.db_schema}.{model.target.value.table}",
            "measures": lookml_measures_from_model(model, models),
            "dimensions": lookml_dimensions_from_model(model, models),
        }
    }

    contents = lkml.dump(lookml)
    filename = f"{model.name}.view"
    return LookViewFile(filename=filename, contents=contents)


def lookml_model_from_metriql_models(models: List[MetriqlModel], connection: str):
    explore = []
    for model in models:
        explore_model_data = {"name": model.name}
        if model.description:
            explore_model_data["description"] = model.description
        explore.append(explore_model_data)

    lookml = {
        "connection": connection,
        "include": "/views/*",
        "explore": explore,
    }

    contents = lkml.dump(lookml)
    filename = f"{connection}.model"
    return LookModelFile(filename=filename, contents=contents)


def lookml_measures_from_model(model: MetriqlModel, models: List[MetriqlModel]):
    lookml_measures = [lookml_measure(measure, None) for measure in model.measures]

    for relation in model.relations:
        relation_model = next(filter(lambda d: d.name == relation.modelName, models))

        for measure in relation_model.measures:
            lookml_measures.append(lookml_measure(measure, relation.name))

    return lookml_measures


def lookml_measure(measure: Measure, prefix: str):
    name = ("{}.".format(prefix) if prefix else "") + measure.name
    measure_type = measure.value.aggregation

    column = measure.value.column
    measure_sql = ""
    if column:
        measure_sql = f"${{TABLE}}.{column}"

    if measure.type == "dimension":
        measure_sql = f"${{{measure.value.dimension}}}"

    if measure.type == "sql":
        measure_type = column if column else measure.fieldType
        measure_sql = measure.value.sql

    measures = {
        "name": name,
        "type": LOOKER_DTYPE_MAP[measure_type]
        if measure_type in LOOKER_DTYPE_MAP
        else measure_type,
    }

    if measure_sql:
        measures["sql"] = measure_sql
    if measure.description:
        measures["description"] = measure.description
    if measure.label:
        measures["label"] = measure.label

    if measure.reportOptions and measure.reportOptions.looker:
        looker = measure.reportOptions.looker
        for key in looker:
            measures[key] = str(looker[key])

    return measures


def lookml_dimensions_from_model(model: MetriqlModel, models: List[MetriqlModel]):
    lookml_dimensions = [
        dimension_data
        for dimension in model.dimensions
        for dimension_data in lookml_dimension(dimension, None)
    ]

    for relation in model.relations:
        relation_model = next(filter(lambda d: d.name == relation.modelName, models))

        for dimension in relation_model.dimensions:
            lookml_dimensions.extend(lookml_dimension(dimension, relation.name))

    return list(filter(None, lookml_dimensions))


def lookml_dimension(dimension: Dimension, prefix: str):
    dimension_type = (
        LOOKER_DTYPE_MAP[dimension.fieldType]
        if dimension.fieldType in LOOKER_DTYPE_MAP
        else dimension.fieldType
    )

    if not dimension_type in looker_scalar_types:
        return lookml_dimension_group(dimension, prefix)

    name = ("{}.".format(prefix) if prefix else "") + dimension.name

    dimension_sql = ""
    if dimension.type == "column":
        column = dimension.value.column
        dimension_sql = f"${{TABLE}}.{column}"

    if dimension.type == "sql":
        dimension_sql = dimension.value.sql

    dimension_data = {
        "name": name,
        "type": LOOKER_DTYPE_MAP[dimension_type]
        if dimension_type in LOOKER_DTYPE_MAP
        else dimension_type,
    }

    if dimension_sql:
        dimension_data["sql"] = dimension_sql
    if dimension.description:
        dimension_data["description"] = dimension.description
    if dimension.label:
        dimension_data["label"] = dimension.label

    if dimension.reportOptions and dimension.reportOptions.looker:
        looker = dimension.reportOptions.looker
        for key in looker:
            dimension_data[key] = str(looker[key])

    return [dimension_data]


def lookml_dimension_group(dimension: Dimension, prefix: str):
    """dimension: created_at__day {
      label: Day
      sql: ${TABLE}.created_at::day ;;
      group_label: "Created At"
    }
    """
    postOperations = dimension.postOperations
    if postOperations:
        return [
            {
                "name": ("{}.".format(prefix) if prefix else "")
                        + f"{dimension.name}__{postOperation}",
                "sql": f"${{TABLE}}.{dimension.value.column}::{postOperation}",
                "label": postOperation,
                "group_label": dimension.value.column,
            }
            for postOperation in postOperations
        ]

    return []
