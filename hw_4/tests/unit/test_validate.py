from unittest.mock import MagicMock, patch, call
import pytest

def test_validate_user_full_name():
    from validate import validate_user_full_name
    user_full_name = 'John1!! Doe'
    actual = validate_user_full_name(user_full_name)
    expected = ('John', 'Doe')
    assert actual == expected

@pytest.mark.parametrize(
    "field, value, allowed_values, strict, expected",
    [
        ("test_field", "a", ["a", "b", "c"], True, True),
        ("test_field", "d", ["a", "b", "c"], True, pytest.raises(ValueError)),
        ("test_field", "a", ["a", "b", "c"], False, True),
        ("test_field", "d", ["a", "b", "c"], False, False),
    ]
)
def test_validate_field_value(field, value, allowed_values, strict, expected):
    from validate import validate_field_value
    if isinstance(expected, bool):
        assert validate_field_value(field, value, allowed_values, strict) == expected
    else:
        with expected:
            validate_field_value(field, value, allowed_values, strict)

@patch('validate.validate_field_value')
def test_valid_acc(mock_f_1):
    from validate import valid_acc
    data = [{"type": "credit", "status": "gold"},
            {"type": "debit", "status": "platinum"},
            {"type": "aaa", "status": "bbb"}]
    valid_acc(data)
    actual_call = {'validate_field_value': mock_f_1.call_count}
    expected_call = {'validate_field_value': 6}
    assert actual_call == expected_call


@pytest.mark.parametrize("account_number, expected", [
    ("ID--ABC-123444556-", "ID--ABC-123444556-"),
    ("ID--AC-1234445586-", "ID--AC-1234445586-"),
])
def test_valid_account_number(account_number, expected):
    from validate import validate_account_number
    actual = validate_account_number(account_number)
    assert actual == expected


@pytest.mark.parametrize("account_number, expected_exception, expected_message", [
    ("ID--A-1234-", ValueError, "error: too little"),
    ("ID--ABC-12345678901234-", ValueError, "error: many chars"),
    ("XX--ABC-123444556-", ValueError, "error: wrong format"),
    ("ID--123-123456-", ValueError, "error: too little"),
])
def test_invalid_account_number(account_number, expected_exception, expected_message):
    from validate import validate_account_number
    with pytest.raises(expected_exception) as excinfo:
        validate_account_number(account_number)
    assert str(excinfo.value) == expected_message

@pytest.mark.parametrize("transact_time, expected", [(None, "time"), ("ttt", "ttt")])
def test_add_transaction_time(transact_time, expected):
    with patch('validate.datetime') as mock_datetime:
        mock_datetime.now.return_value = "time"
        from validate import add_transaction_time
        actual = add_transaction_time(transact_time)
        assert actual == expected

@pytest.mark.parametrize("sender_amount, sent_amount, sender_currency, receiver_currency, expected", [
    (100, 50, 'USD', 'USD', False),
    (50, 100, 'USD', 'USD', ValueError),
    (100, 50, 'USD', 'EUR', True),
])
def test_valid_currency_amount(sender_amount, sent_amount, sender_currency, receiver_currency, expected):
    from validate import valid_currency_amount
    if expected == ValueError:
        with pytest.raises(ValueError):
            valid_currency_amount(sender_amount, sent_amount, sender_currency, receiver_currency)
    else:
        actual = valid_currency_amount(sender_amount, sent_amount, sender_currency, receiver_currency)
        assert actual == expected

@patch('validate.validate_field_value', return_value= True)
@patch('validate.validate_user_full_name', return_value= ("John", "Doe"))
def test_username_validate(mock_f_1,mock_f_2):
    from validate import username_validate
    data = [
        {"user_name": "John1!! Doe"},
        {"user_name": "Jane Smith"}
    ]
    actual = username_validate(data)
    expected = [{"name": "John", "surname": "Doe"},
                {"name": "John", "surname": "Doe"}
                ]
    actual_call = {'validate_field_value': mock_f_1.call_count,
                   'validate_user_full_name': mock_f_2.call_count}
    expected_call = {'validate_field_value': 4,
                     'validate_user_full_name': 1}

    assert actual == expected
    assert actual_call == expected_call
