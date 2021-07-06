import argparse
import json
import pathlib
import os
import shutil
import sys
import tempfile
from typing import List

from .generator import lookml_view_from_metriql_model, lookml_model_from_metriql_models
from .models import MetriqlModel


def load_metriql_models(file):
    if file is not None:
        source = open(file).read()
    else:
        source = sys.stdin.readline()
    datasets = json.loads(source)
    return [MetriqlModel(**raw_model) for raw_model in datasets]


def generate_lookml_views(out_directory, models: List[MetriqlModel]):
    lookml_views = [
        lookml_view_from_metriql_model(model, models) for model in models
    ]

    pathlib.Path(os.path.join(out_directory, "views")).mkdir(
        parents=True, exist_ok=True
    )

    for view in lookml_views:
        with open(os.path.join(out_directory, "views", view.filename), "w") as f:
            f.write(view.contents)


def generate_lookml_models(out_directory, models: List[MetriqlModel], project_name: str):
    lookml_models_file = lookml_model_from_metriql_models(
        models, project_name
    )

    with open(os.path.join(out_directory, lookml_models_file.filename), "w") as f:
        f.write(lookml_models_file.contents)


def main(args: list = None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--project_name", help="Model name", type=str, default="metriql"
    )

    argparser.add_argument("--file", help="source of the metadata file. if not set, the source is stdin")
    argparser.add_argument("--out", help="Output directory")

    args = argparser.parse_args(args=args)

    temp_dir = None
    if args.out is None:
        temp_dir = tempfile.TemporaryDirectory(suffix="metriql2looker")
        out_directory = os.path.join(temp_dir.name, 'lookml')
        os.mkdir(out_directory)
    else:
        out_directory = args.out

    try:
        datasets = load_metriql_models(args.file)
        generate_lookml_views(out_directory, datasets)
        generate_lookml_models(out_directory, datasets, args.project_name)

        if args.out is None:
            zip_file = shutil.make_archive(os.path.join(temp_dir.name, args.project_name), 'zip', out_directory)
            with open(zip_file, 'r') as fin:
                sys.stdout.reconfigure(encoding='utf-8')
                shutil.copyfileobj(fin, sys.stdout)
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()



