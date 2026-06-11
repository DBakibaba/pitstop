from distance import haversine

def test_same_location():
    result=haversine(
        43.7001,
        -79.4163,
        43.7001,
        -79.4163
    )

    assert result ==0 

def test_toronto_to_ottawa():
    result = haversine(
        43.6532,
        -79.3832,
        45.4215,
        -75.6972
    )

    assert 350 < result < 400