import re
from datetime import datetime


# Validation of user_full_name field
def validate_user_full_name(user_full_name):
    # Delete all characters that are not letters
    user_full_name = re.sub(r'[^a-zA-Z\s]', '', user_full_name)
    # Separate first and last name by any whitespace characters
    name, surname = user_full_name.strip().split(maxsplit=1)
    return name, surname


# Validation of fields with a strict set of values
def validate_field_value(field, value, allowed_values):
    if value not in allowed_values:
        raise ValueError("error: not allowed value {} for field {}!".format(value, field))

def valid_acc(data):
    type_values = ["credit", "debit"]
    status_values = ["gold", "silver", "platinum"]
    for i in data:
        validate_field_value("type", i["type"], type_values)
        validate_field_value("status", i["status"], status_values)
    return True

def validate_account_number(account_number):
    # Replacing special characters with dashes
    account_number = re.sub(r'[#%_?&]', '-', account_number)

    # Character count check
    if len(account_number) < 18:
        raise ValueError("error: too little")
    if len(account_number) > 18:
        raise ValueError("error: many chars")

    # Checking the format
    if not account_number.startswith("ID--"):
        raise ValueError("error: wrong format")

    # Checking for the right pattern
    if not re.match(r'ID--[a-zA-Z]{1,3}-\d+-', account_number):
        raise ValueError("an error: broken ID")

    return account_number


# Function for checking and adding transaction time
def add_transaction_time(transaction_time):
    if not transaction_time:
        transaction_time = datetime.now()
    return transaction_time
