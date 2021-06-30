import argparse
import json
import lkml
import pathlib
import os
import logging
from typing import List

import models
import generator

SAMPLE_FILE = "./example/sample.json"
LOOKML_OUTPUT_DIR = "./lookml"

logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(levelname)-6s %(message)s",
    datefmt="%H:%M:%S",
)


def load_metriql_models():
    with open(SAMPLE_FILE) as f:
        raw_data = json.load(f)
    typed_metriql_models = [models.MetriqlModel(**raw_model) for raw_model in raw_data]

    return typed_metriql_models


def generate_lookml_views(models: List[models.MetriqlModel]):
    lookml_views = [
        generator.lookml_view_from_metriql_model(model, models) for model in models
    ]

    pathlib.Path(os.path.join(LOOKML_OUTPUT_DIR, "views")).mkdir(
        parents=True, exist_ok=True
    )

    for view in lookml_views:
        with open(os.path.join(LOOKML_OUTPUT_DIR, "views", view.filename), "w") as f:
            f.write(view.contents)

    logging.info(
        f'Generated {len(lookml_views)} lookml views in {os.path.join(LOOKML_OUTPUT_DIR, "views")}'
    )


def generate_lookml_models(models: List[models.MetriqlModel], project_name: str):

    lookml_models_file = generator.lookml_model_from_metriql_models(
        models, project_name
    )

    with open(os.path.join(LOOKML_OUTPUT_DIR, lookml_models_file.filename), "w") as f:
        f.write(lookml_models_file.contents)

    logging.info(
        f"Generated {lookml_models_file.filename} lookml models in {LOOKML_OUTPUT_DIR}"
    )


if __name__ == "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--project_name", help="Model name", type=str, default="explorer"
    )

    args = argparser.parse_args()

    typed_metriql_models = load_metriql_models()
    generate_lookml_views(typed_metriql_models)
    generate_lookml_models(typed_metriql_models, args.project_name)
    logging.info("Success")
