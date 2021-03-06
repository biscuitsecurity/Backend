from tests._test_data import *
import aiounittest
from dotenv import load_dotenv
load_dotenv()
from backend.storage import ethereum

icd = ethereum.IncidentsContract()


class TestWeb3(aiounittest.AsyncTestCase):

    def test_init_contract(self):
        icd.add_incident(incident1, [{'name': 'test', 'content': attachb}])
        icd.add_incident(incident2, [])
        comment1_ref = icd.add_comment(incident1b, incident1b, comment1b, [('testattachment', attachb)], incident2b, 2)
        icd.add_comment(comment1_ref, incident1b, comment2b, [], incident2b, 2)
        icd.add_comment(incident2b, incident2b, comment1b, [], incident2b, 2)

    def test_add_incident(self):
        res = icd.add_incident(incident1, [{'name': 'test', 'content': attachb}])
        self.assertEqual(len(res), 32)

    def test_get_incidents(self):
        incidents = icd.get_incidents()
        self.assertGreater(len(incidents), 0)

    async def test_get_incident(self):
        res = await icd.get_incident(incident1b)
        self.assertEqual(len(res), 7)

    def test_vote_incident(self):
        res = icd.vote_incident(incident1b, 1)
        self.assertEqual(len(res), 32)

    def test_remove_incident(self):
        res = icd.remove_incident(incident1b)
        self.assertEqual(len(res), 32)

    async def test_get_comment(self):
        res = await icd.get_comment(comment1b, 0)
        self.assertEqual(len(res), 7)

    def test_add_comment(self):
        res = icd.add_comment(comment1b, incident1b, comment1b, [('testattachment', attachb)], incident2b, 2)
        self.assertEqual(len(res), 66)


if __name__ == '__main__':
    aiounittest.main()
