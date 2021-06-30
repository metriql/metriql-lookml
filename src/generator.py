import lkml
from typing import List
from models import MetriqlModel, LookViewFile, LookModelFile, Measure

LOOKER_DTYPE_MAP = {
        'integer':     'number',
        'decimal':   'number',
        'double':     'number',
        'long':   'number',
        'boolean':   'yesno',
        'string':    'string',
        'timestamp': 'date',
        'time':  'date',
        'date':      'date'
    }

def lookml_view_from_metriql_model(model: MetriqlModel, models: List[MetriqlModel]):

    lookml = {
        "view": {
            "name": model.name,
            "sql_table_name": f"{model.target.value.database}.{model.target.value.db_schema}.{model.target.value.table}",
            "measures": lookml_measures_from_model(model, models),
        }
    }
    contents = lkml.dump(lookml)
    filename = f"{model.name}.view"
    return LookViewFile(filename=filename, contents=contents)

def lookml_model_from_metriql_models(models: List[MetriqlModel], project_name: str):

    explore = []
    for model in models:
        explore_model_data = {"name": model.name}
        if model.description:
            explore_model_data["description"] = model.description
        explore.append(explore_model_data)

    lookml = {
        "connection": project_name,
        "include": "/views/*",
        "explore": explore,
    }

    contents = lkml.dump(lookml)
    filename = f"{project_name}.model"
    return LookModelFile(filename=filename, contents=contents)

def lookml_measures_from_model(model: MetriqlModel, models: List[MetriqlModel]):

    lookml_measures = []
    for relation in model.relations:
        relation_model = next(filter(lambda d: d.name == relation.modelName, models))

        for measure in relation_model.measures:
            lookml_measures.append(lookml_measure(measure, relation.name))

    lookml_measures.extend([
        lookml_measure(measure, None)
        for measure in model.measures
    ])
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
        measure_type = column if column else LOOKER_DTYPE_MAP[measure.fieldType]
        measure_sql = measure.value.sql

    measures = {
        "name": name,
        "type": measure_type,
    }
    if measure_sql:
        measures["sql"] = measure_sql
    if measure.description:
        measures["description"] = measure.description
    elif column:
         measures["description"] = f"{measure_type} of {column}"

    return measures
