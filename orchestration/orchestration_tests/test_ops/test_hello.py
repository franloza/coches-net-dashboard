from orchestration.ops.hello import hello


def test_hello():
    """
    This is an example test for a Dagster op.

    For hints on how to test your Dagster ops, see our documentation tutorial on Testing:
    https://docs.dagster.io/concepts/testing
    """

    assert hello() == "Hello, Dagster!"
