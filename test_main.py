import uuid

from fastapi.testclient import TestClient

from main import app, Task
from utils import *
client = TestClient(app)


def mock_task(client_, json_original={}):
    response = client_.post(
        '/task',
        json=json_original
    )

    assert response.status_code == 200
    response_json = response.json()
    assert is_valid_uuid(response_json) == True
    return response_json


def delete_mock(id_list):
    for id in id_list:
        client.delete(f'task/{id}')


'''
/task - GET
'''


def test_read_tasks_with_empty_tasks():
    response = client.get('/task')
    assert response.status_code == 200
    assert response.json() == {}


def test_read_tasks_with_empty_tasks_completed_cases_0():
    response = client.get('/task?completed=false')
    assert response.status_code == 200
    assert response.json() == {}


def test_read_tasks_with_empty_tasks_completed_cases_1():
    response = client.get('/task?completed=true')
    assert response.status_code == 200
    assert response.json() == {}


def test_read_tasks_with_empty_tasks_completed_cases_2():
    response = client.get('/task?completed=3123')
    assert response.status_code == 422


def test_read_tasks_with_mock_task():
    mock_uuid = mock_task(client)
    response = client.get('/task')
    assert response.status_code == 200
    assert response.json() == {
        mock_uuid: {
            'completed': False,
            'description': 'no description'
        }
    }
    delete_mock([mock_uuid])



def test_read_tasks_with_multiples_mocks_task():
    mock_uuid_list = []
    for i in range(0, 5):
        mock_uuid_list.append(mock_task(client))

    response_mock = {}
    for id in mock_uuid_list:
        response_mock[id] = {
            'completed': False,
            'description': 'no description'
        }

    response = client.get('/task')
    assert response.status_code == 200
    response_json = response.json()
    print(f'\nresponse_json_key: {len(response_json.keys())}')
    print(f'\nmock_uuid_list: {len(mock_uuid_list)}')
    assert response_json == response_mock
    delete_mock(mock_uuid_list)


'''
/task - POST :
'''


def test_post_task_without_item():
    response = client.post('/task/')

    assert response.status_code == 307


def test_post_task_with_empty_item():
    response_uuid = mock_task(
        client,
        {}
    )

    delete_mock([response_uuid])


def test_post_task_with_item_with_description():
    response_uuid = mock_task(
        client,
        {'description': 'new description'}
    )
    delete_mock([response_uuid])


def test_post_task_with_item_with_completed_false():
    response_uuid = mock_task(
        client,
        {'completed': False}
    )

    delete_mock([response_uuid])


def test_post_task_with_item_with_completed_true():
    response_uuid = mock_task(
        client,
        {'completed': True}
    )
    delete_mock([response_uuid])



def test_post_task_with_item_with_description_completed_true():
    response_uuid = mock_task(
        client,
        {'description': 'new description', 'completed': True}
    )

    delete_mock([response_uuid])



def test_post_task_with_item_with_description_completed_false():
    response_uuid = mock_task(
        client,
        {'description': 'new description', 'completed': False}
    )

    delete_mock([response_uuid])


def test_create_task_0():
    response = client.post(
        '/task',
        json={'crazy-key': 'new description', 'completed': False}
    )

    assert response.status_code == 422


'''
/task/{uuid_} - GET :
'''


def test_get_task_by_nonexisting_id():
    response = client.get(
        '/task/{}'.format(create_random_uuid())
    )

    assert response.status_code == 404


def test_get_existing_id():
    json_ = {'description': 'GET 1/2 done', 'completed': False}

    uuid_ = mock_task(client, json_)

    response_get = client.get('/task/{}'.format(uuid_))

    assert response_get.status_code == 200


'''
/task/{uuid_} - PUT:
'''


def test_put_nonexisting_uuid():
    response = client.put(
        'task/{}'.format(create_random_uuid()),
        json={'description': 'Alter first', 'completed': True},
    )

    assert response.status_code == 404


def test_put_existing_uuid():
    json_ = {'description': 'PUT 1/2 done', 'completed': False}

    uuid_ = mock_task(client, json_)

    json__ = {'description': 'PUT 2/2 done', 'completed': False}

    response_put = client.put(
        '/task/{}'.format(uuid_),
        json=json__
    )

    assert response_put.status_code == 200
    assert response_put.json() == json__
    delete_mock(uuid_)


def test_put_nonexisting_info():
    json_ = {'description': 'PUT 1/2 done', 'completed': False}

    uuid_ = mock_task(client, json_)

    json__ = {'description': 'PUT 2/2 done', 'completed': False,
              'trapKey': 'This is not supposed to exist'}

    response_put = client.put(
        '/task/{}'.format(uuid_),
        json=json__
    )

    assert response_put.status_code == 422
    delete_mock(uuid_)


'''
/task/{uuid_} - DELETE:
'''


def test_delete_task_existing():
    json_ = {'description': 'PUT 1/2 done', 'completed': False}

    uuid_ = mock_task(client, json_)

    response_delete = client.delete('task/{}'.format(uuid_))

    assert response_delete.status_code == 200


def test_task_delete_non_existing():
    response = client.delete('task/{}'.format(create_random_uuid()))

    assert response.status_code == 404
