import unittest

from application.query_intent import QueryIntent, detect_query_intent


class QueryIntentDetectionTests(unittest.TestCase):
    def test_detects_candidate_count_queries(self) -> None:
        queries = [
            "How many candidates do we have?",
            "What is the total number of CVs indexed?",
            "Count of candidates in the system",
            "How many CVs are indexed?",
        ]
        for query in queries:
            with self.subTest(query=query):
                self.assertEqual(detect_query_intent(query), QueryIntent.INVENTORY_COUNT)

    def test_detects_candidate_list_queries(self) -> None:
        queries = [
            "List all candidates",
            "List all candidate names",
            "Show all CVs in the database",
            "All candidates please",
        ]
        for query in queries:
            with self.subTest(query=query):
                self.assertEqual(detect_query_intent(query), QueryIntent.INVENTORY_LIST)

    def test_preserves_semantic_skill_queries(self) -> None:
        queries = [
            "Who has experience with React and Python?",
            "How many years of Python does Jane Doe have?",
            "Find candidates with Kubernetes experience",
        ]
        for query in queries:
            with self.subTest(query=query):
                self.assertEqual(detect_query_intent(query), QueryIntent.SEMANTIC)


if __name__ == "__main__":
    unittest.main()
