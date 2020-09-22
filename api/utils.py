import uuid


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

def create_random_uuid():
  return str(uuid.uuid4())
