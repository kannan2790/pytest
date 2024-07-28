import requests
import json
import jsonpath
import random
import pytest
import logging

base_url = "http://127.0.0.1:6543"


@pytest.fixture()
def session():
    ses = requests.session()
    print("resetting")
    ses.post(url=base_url + "/reset", json={})
    return ses


class TestPost:

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.session = session
        self.get = TestGet()

    def post_helper(self):
        a = generate_quote()
        response = requests.post(url=base_url + "/quotes", json=json.loads(a))
        print(response.text)
        return response

    # def test_post_single_quote_allparameters(self):
    #     a = generate_quote()
    #     response = self.session.post(url=base_url + "/quotes", json=json.loads(a))
    #     print("Test status code is ", response.status_code)
    #     assert response.status_code == 201
    #     self.get.get_helper()
    #
    # def test_post_empty_text_field(self):
    #     response = self.session.post(url=base_url + "/quotes", json={})
    #     assert response.status_code == 400
    #     print("Test status code is ", response.status_code)
    #     self.get.get_helper()
    #
    #
    # def test_post_invalid_text_field(self):
    #     response = self.session.post(url=base_url + "/quotes", json={"text":123})
    #     print("Test status code is ", response.status_code)
    #     assert response.status_code == 400
    #     self.get.get_helper()
    #
    # def test_post_multiple_quotes(self, i =0):
    #     while i < 15:
    #         a = generate_quote()
    #         response = requests.post(url=base_url + "/quotes", json=json.loads(a))
    #         data = response.json()
    #         assert response.status_code == 201
    #         assert data["ok"] is True
    #         self.get.get_helper()
    #         i += 1

class TestGet:
    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.session = session
        self.post = TestPost()

    def get_helper(self, value=None):
        print ("inside")
        if value is not None:
            response = requests.get(url=base_url + "/quotes" + f"/{value}")

        else:
            response = requests.get(url=base_url + "/quotes")
        print(response.text)
        return response

    # def test_get_with_id(self):
    #     response = self.post.post_helper()
    #     post_response = response.json()
    #     id = post_response["data"]["id"]
    #     quote = post_response["data"]["text"]
    #     assert response.status_code == 201
    #     response_get = self.get_helper(id)
    #     data = response_get.json()
    #     assert response_get.status_code == 200
    #     assert data["data"]["id"] == id
    #     assert data["data"]["text"] == quote
    #
    # def test_get_with_invalid_id(self):
    #     response_get = self.get_helper(6)
    #     assert response_get.status_code == 404

class TestDelete:
    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.session = session
        self.post = TestPost()
        self.get = TestGet()
    def delete_helper(self, value):
        response = requests.delete(url=base_url +"/quotes"+ f"/{value}")
        return response
    def test_delete_a_quote(self):
        actual = self.session.get(url=base_url+"/quotes")
        json_a = actual.json()
        actual_count = len(json_a["data"])
        print(actual_count)
        self.post.post_helper()
        delete_response = self.delete_helper(4)
        assert delete_response.status_code ==200
        response = self.get.get_helper()
        response_a = response.json()
        after_delete = len(response_a["data"])
        assert after_delete is actual_count


def generate_quote():
    response = requests.get("https://zenquotes.io/api/random")
    res = response.json()
    quote = res[0]['q']
    data = {
        "text": quote
    }
    json_data = json.dumps(data)
    return (json_data)
