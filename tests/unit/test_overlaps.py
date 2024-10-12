import pytest

from src.cli.main_external_csv import overlaps


@pytest.mark.parametrize(
    "loc1, loc2, expected",
    [
        # Exact overlap
        ((100, 110), (100, 110), True),
        # Partial overlap
        ((100, 110), (105, 115), True),
        ((105, 115), (100, 110), True),
        # Full encapsulation
        ((100, 110), (95, 115), True),
        ((95, 115), (100, 110), True),
        # No overlap
        ((100, 110), (111, 120), False),
        ((111, 120), (100, 110), False),
        # Adjacent ranges (not considered overlap)
        ((100, 110), (110, 120), False),
        ((110, 120), (100, 110), False),
        # Single point range overlap
        ((100, 100), (100, 100), True),
        ((100, 100), (99, 101), True),
        ((99, 101), (100, 100), True),
        # Single point range no overlap
        ((100, 100), (101, 101), False),
        ((101, 101), (100, 100), False),
    ],
)
def test_overlaps(loc1, loc2, expected):
    assert overlaps(loc1, loc2) == expected


if __name__ == "__main__":
    pytest.main()
