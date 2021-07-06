# metriql Looker Integration

Generates LookML model from your metriql datasets.
The idea is to leverage metriql datasets in your Looker setup without any additional modeling.

### Usage

The library is available in PyPI so you can install it via pip as follows:

```
pip install metriql-lookml
```

The library expects `stdin` for the metriql metadata and outputs a ZIP file to `stdout`. Here is an example:

```
curl http://metriql-server.com/api/v0/metadata | metriql-lookml --connection myproject > metriql.zip
```

You can use `--file` argument instead of reading the metadata from `stdin` as an alternative. 

The command outputs a zip file to `stdout` by default, if you pass `--out myfile.zip` argument, it will write to the specified file instead.

### How does it work?

1. Create a connection to metriql from Looker using its [Trino interface](https://docs.looker.com/setup-and-management/database-config/prestodb).

2. Run `metriql-lookml` passing the relevant `connection` argument for metriql.

You need to enable JDBC in your metriql server to be able to use metriql's Trino interface.

### Build from source

Requires [pipenv](https://pipenv.pypa.io/en/latest/) and python >=3.7

```
# From root folder
# Install
pipenv install --dev

# Run
pipenv run metriql2lookml
```
