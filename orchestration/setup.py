import setuptools

setuptools.setup(
    name="orchestration",
    packages=setuptools.find_packages(),
    install_requires=[
        "dagster==0.15",
        "dagster-pandas==0.15",
        "dagster-dbt==0.15",
        "dbt-duckdb"
    ],
)
