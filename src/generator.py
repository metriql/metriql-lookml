import lkml
from typing import List
from models import MetriqlModel, LookViewFile, LookModelFile, Measure


def lookml_view_from_metriql_model(model: MetriqlModel):
    lookml = {
        "view": {
            "name": model.name,
            "sql_table_name": f"{model.target.value.database}.{model.target.value.db_schema}.{model.target.value.table}",
            "measures": lookml_measures_from_model(model),
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


def lookml_measures_from_model(model: MetriqlModel):
    return [
        lookml_measure(measure)
        for measure in model.measures
        if measure.type == "column"
    ]


def lookml_measure(measure: Measure):
    column = measure.value.column if measure.value.column else "*"
    measures = {
        "name": measure.name,
        "type": measure.value.aggregation,
        "sql": f"${{TABLE}}.{column}",
        "description": measure.description
        or f"{measure.value.aggregation.capitalize()} of {column}",
    }

    return measures
