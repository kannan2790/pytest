import requests
import json
import pytest

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

    def post_helper(self, value=None):
        """
        Helper function to post a single or multiple random quotes.
        If 'value' is provided, it posts that many quotes.
        """
        if value is None:
            a = generate_quote()
            response = requests.post(url=base_url + "/quotes", json=json.loads(a))
            print(response.text)
            return response
        else:
            i = 0
            while i < value:
                a = generate_quote()
                requests.post(url=base_url + "/quotes", json=json.loads(a))
                i+=1

    def test_post_single_quote_allparameters(self):
        """
        Test posting a single quote and verifying the response status code and data.
        """
        a = generate_quote()
        b = json.loads(a)
        post_quote = b['text']
        response = self.session.post(url=base_url + "/quotes", json=json.loads(a))
        print("Test status code is ", response.status_code)
        assert response.status_code == 201
        response_json = response.json()
        assert_a = self.get.search_inside_get("4",response_json)
        assert_b = self.get.search_inside_get(post_quote,response_json)
        assert assert_a is True
        assert assert_b is True


    def test_post_empty_text_field(self):
        """
        Test posting an empty JSON object and expect a 400 status code.
        """
        response = self.session.post(url=base_url + "/quotes", json={})
        assert response.status_code == 400
        print("Test status code is ", response.status_code)
        self.get.get_helper()


    def test_post_invalid_text_field(self):
        """
        Test posting an invlid JSON object and expect a 400 status code.
        """
        response = self.session.post(url=base_url + "/quotes", json={"text":123})
        print("Test status code is ", response.status_code)
        assert response.status_code == 400
        self.get.get_helper()

    def test_post_multiple_quotes(self, i =0):
        """
        Test posting multiple JSON objects and expect a 201 status code. System breaks when i send more than 15
        """
        while i < 10:
            a = generate_quote()
            response = requests.post(url=base_url + "/quotes", json=json.loads(a))
            data = response.json()
            assert response.status_code == 201
            assert data["ok"] is True
            self.get.get_helper()
            i += 1

class TestGet:
    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.session = session
        self.post = TestPost()
    def get_helper(self, value=None, ):
        """
        Helper function to get all quotes or a specific quote by ID.
        """
        if value is not None:
            response = requests.get(url=base_url + "/quotes" + f"/{value}")

        else:
            response = requests.get(url=base_url + "/quotes")
        print(response.text)
        return response


    def search_inside_get(self, string, data):
        """
        Helper function to search for any specific text recursively.
        """
        if isinstance(data, dict):
            return any(self.search_inside_get(string, v) for v in data.values())
        elif isinstance(data, list):
            return any(self.search_inside_get(string, item) for item in data)
        else:
            return string == str(data)


    def test_get_with_id(self):
        """
        Test retrieving a specific quote by ID
        """
        response = self.post.post_helper()
        post_response = response.json()
        id = post_response["data"]["id"]
        quote = post_response["data"]["text"]
        assert response.status_code == 201
        response_get = self.get_helper(id)
        data = response_get.json()
        assert response_get.status_code == 200
        assert data["data"]["id"] == id
        assert data["data"]["text"] == quote

    def test_get_with_invalid_id(self):
        """
        Test retrieving a specific quote by invalid ID
        """
        response_get = self.get_helper(6)
        assert response_get.status_code == 404

    def test_get_sorted_by_id_and_duplicates(self):
        """
        Test if get is sorted by id and has no duplicates
        """

        self.post.post_helper(3)
        res = self.get_helper()
        res_json = res.json()
        ids = [item['id'] for item in res_json['data']]
        is_sorted = ids == sorted(ids)
        is_dup = len(ids) != len(set(ids))
        assert is_sorted is True
        assert is_dup is False

class TestDelete:
    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.session = session
        self.post = TestPost()
        self.get = TestGet()
    def delete_helper(self, value):
        """
            helper to delete a quote
        """
        response = requests.delete(url=base_url +"/quotes"+ f"/{value}")
        return response

    def test_delete_a_quote(self):
        """
        Test deleting a quote and verify that it no longer exists.
        """
        # get the previous state of the system
        actual = self.session.get(url=base_url+"/quotes")
        json_a = actual.json()
        actual_count = len(json_a["data"])
        #make a post to add new quote
        post = self.post.post_helper()
        post_response = post.json()
        # extract the quote to compare
        post_quote = post_response["data"]["text"]
        # send the delete request
        delete_response = self.delete_helper(4)
        assert delete_response.status_code ==200
        # get the current state of the system, the len should be same as previous state
        response = self.get.get_helper()
        response_a = response.json()
        after_delete = len(response_a["data"])
        #asser the count is same before and after
        assert after_delete is actual_count
        x = self.get.search_inside_get(post_quote, response_a)
        #assert that the quote is deleted
        assert x is False

    def test_subsequent_deletes(self):
        """
        Test subsequenet delete leads to 404 error
        """
        delete_response = self.delete_helper(4)
        assert delete_response.status_code ==404

def generate_quote():
    response = requests.get("https://zenquotes.io/api/random")
    res = response.json()
    quote = res[0]['q']
    data = {
        "text": quote
    }
    json_data = json.dumps(data)
    return (json_data)
