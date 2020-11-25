"""
Client tests
"""
# pylint: disable=protected-access,unused-argument
import pytest
from sfrbox import Client, ClientError, username_password


def test_compute_hash():
    """Check that the hash computation match the example given in the documentation"""
    result = Client._compute_hash('43f6168e635b9a90774cc4d3212d5703c11c9302', 'admin')
    assert result == '7aa3e8b3ed7dfd7796800b4c4c67a0c56c5e4a66502155c17a7bcef5ae945ffa'


def test_api_url(client):
    """Check that the api url is properly computed"""
    assert client.api_url == 'http://192.168.1.1/api/1.0'


def test_get_single_result(client, mock_get_request):
    """Test that a method returning a single result returns a properly formatted dict"""
    mock_get_request('?method=lan.getInfo', 'lan.getInfo.xml')

    result = client.lan.get_info()
    assert result == {
        'ip_addr': '192.168.1.1',
        'netmask': '255.255.255.0',
        'dhcp_active': 'on',
        'dhcp_start': '192.168.1.20',
        'dhcp_end': '192.168.1.100',
        'dhcp_lease': 86400
    }


def test_get_empty_list_result(client, mock_get_request):
    """Test that a method returning a list can return an empty list"""
    mock_get_request('?method=lan.getDnsHostList', 'lan.getDnsHostList_empty.xml')
    result = client.lan.get_dns_host_list()
    assert result == []


def test_get_single_item_list_result(client, mock_get_request):
    """Test that a method returning a list can return an empty list"""
    mock_get_request('?method=lan.getDnsHostList', 'lan.getDnsHostList_1item.xml')
    result = client.lan.get_dns_host_list()
    assert result == [
        {
            'ip': '192.168.1.10',
            'name': 'host1.lan'
        }
    ]


def test_get_two_items_list_result(client, mock_get_request):
    """Test that a method returning a list can return an empty list"""
    mock_get_request('?method=lan.getDnsHostList', 'lan.getDnsHostList_2items.xml')
    result = client.lan.get_dns_host_list()
    assert result == [
        {
            'ip': '192.168.1.10',
            'name': 'host1.lan'
        },
        {
            'ip': '192.168.1.11',
            'name': 'host2.lan'
        }
    ]


def test_login_success(client, mock_get_request):
    """Check that we can login if the username/password are correct"""
    mock_get_request('?method=auth.getToken', 'auth.getToken.xml')
    check_mock = mock_get_request('?method=auth.checkToken', 'auth.checkToken_ok.xml')

    client.login(username_password('admin', 'password'))
    assert client._token == 'fe5be7az1v9cb45zeogger8b4re145g3'

    # check that the hash value sent to the API is correct
    hash_value = check_mock.last_request.qs['hash'][0]
    assert hash_value == (
        '2df1e5ddeba2c14262e594c62effd0ecf80ff09a02d223c381487e4a5851302f'
        '0a4d44947b410abbec4ab1da8b6de783d10f8284fcf528ae7c91c4b8ffd91fc5'
    )


def test_login_failure(client, mock_get_request):
    """Check that we cannot login if the username/password are incorrect"""
    mock_get_request('?method=auth.getToken', 'auth.getToken.xml')
    mock_get_request('?method=auth.checkToken', 'auth.checkToken_fail.xml')

    with pytest.raises(ClientError) as error:
        client.login(username_password('admin', 'password'))

    assert client._token is None
    assert error.value.code == 204
    assert str(error.value) == 'Invalid login and/or password'
