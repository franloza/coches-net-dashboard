import setuptools

setuptools.setup(
    name="orchestration",
    packages=setuptools.find_packages(exclude=["orchestration_tests"]),
    install_requires=[
        "dagster==0.15.0",
        "dagit==0.15.0",
        "dagster-pandas==0.15.1",
        "duckdb==0.4.0",
        "pyarrow==8.0.0"
        "pytest",
    ],
)
