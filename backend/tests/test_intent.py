import unittest

from application.query_intent import QueryIntent, detect_query_intent


class TestQueryIntentClassification(unittest.TestCase):
    def test_detects_inventory_count_queries(self) -> None:
        queries = [
            "How many candidates do we have?",
            "What is the total number of CVs indexed?",
            "Count of candidates in database",
            "How many cvs are available?",
            "how many resumes in total",
        ]
        for query in queries:
            with self.subTest(query=query):
                self.assertEqual(
                    detect_query_intent(query),
                    QueryIntent.INVENTORY_COUNT,
                )

    def test_detects_inventory_list_queries(self) -> None:
        queries = [
            "List all candidates",
            "List all candidate names",
            "Show all CVs in the system",
            "All candidates please",
            "list every candidate",
            "names of all profiles",
        ]
        for query in queries:
            with self.subTest(query=query):
                self.assertEqual(
                    detect_query_intent(query),
                    QueryIntent.INVENTORY_LIST,
                )

    def test_detects_semantic_queries(self) -> None:
        queries = [
            "Who has experience with React and TypeScript?",
            "How many years of Python experience does Jane Doe have?",
            "Find senior backend engineers with Docker knowledge",
            "Tell me about candidate backgrounds in e-commerce",
            "",
            "   ",
        ]
        for query in queries:
            with self.subTest(query=query):
                self.assertEqual(
                    detect_query_intent(query),
                    QueryIntent.SEMANTIC,
                )


if __name__ == "__main__":
    unittest.main()
