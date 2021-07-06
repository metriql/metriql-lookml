import argparse
import json
import pathlib
import os
import shutil
import sys
import tempfile
from typing import List

__version__ = "0.1"

from .generator import lookml_view_from_metriql_model, lookml_model_from_metriql_models
from .models import MetriqlModel


def load_metriql_models(datasets: List[MetriqlModel]):
    return [MetriqlModel(**raw_model) for raw_model in datasets]


def generate_lookml_views(out_directory: str, models: List[MetriqlModel]):
    lookml_views = [
        lookml_view_from_metriql_model(model, models) for model in models
    ]

    pathlib.Path(os.path.join(out_directory, "views")).mkdir(
        parents=True, exist_ok=True
    )

    for view in lookml_views:
        with open(os.path.join(out_directory, "views", view.filename), "w") as f:
            f.write(view.contents)


def generate_lookml_models(out_directory: str, models: List[MetriqlModel], connection: str):
    lookml_models_file = lookml_model_from_metriql_models(
        models, connection
    )

    with open(os.path.join(out_directory, lookml_models_file.filename), "w") as f:
        f.write(lookml_models_file.contents)


def main(args: list = None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--connection", help="Connection name in your Looker setup", type=str, default="metriql")
    argparser.add_argument("--file", help="source of the metadata file. if not set, the source is stdin")
    argparser.add_argument("--out", help="Output directory")

    args = argparser.parse_args(args=args)

    if args.file is not None:
        source = open(args.file).read()
    else:
        source = sys.stdin.readline()
    raw_datasets = json.loads(source)

    temp_dir = None
    if args.out is None:
        temp_dir = tempfile.TemporaryDirectory(suffix="metriql2looker")
        out_directory = os.path.join(temp_dir.name, 'lookml')
        os.mkdir(out_directory)
    else:
        out_directory = args.out

    try:
        datasets = load_metriql_models(raw_datasets)
        generate_lookml_views(out_directory, datasets)
        generate_lookml_models(out_directory, datasets, args.connection)

        if args.out is None:
            zip_file = shutil.make_archive(out_directory, 'zip', root_dir=out_directory)
            sys.stdout.buffer.write(open(zip_file, 'rb').read())
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()
