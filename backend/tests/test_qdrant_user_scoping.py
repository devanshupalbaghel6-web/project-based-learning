import unittest
from unittest.mock import AsyncMock, patch

import numpy as np

from app.core.config import settings
from app.services.qdrant_service import QdrantService


class QdrantUserScopingTests(unittest.IsolatedAsyncioTestCase):
    async def test_search_filters_by_user_id(self):
        with patch.object(settings, "QDRANT_USE_CLOUD", False), patch.object(
            settings, "QDRANT_USE_MEMORY", True
        ), patch.object(settings, "QDRANT_COLLECTION", "learning_resources_test_scope"), patch(
            "app.services.qdrant_service.embedding_service.get_dimension", return_value=3
        ), patch(
            "app.services.qdrant_service.embedding_service.encode",
            return_value=np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
        ), patch(
            "app.services.qdrant_service.get_embedding",
            new=AsyncMock(return_value=np.array([1.0, 0.0, 0.0])),
        ):
            service = QdrantService()
            self.assertTrue(service.clear_collection())

            added = await service.add_documents(
                [
                    {
                        "id": 1,
                        "content": "FastAPI user specific resource",
                        "metadata": {"type": "resource", "user_id": "user_1"},
                    },
                    {
                        "id": 2,
                        "content": "FastAPI other user resource",
                        "metadata": {"type": "resource", "user_id": "user_2"},
                    },
                ]
            )
            self.assertTrue(added)

            user_1_results = await service.search(
                query="FastAPI resource",
                top_k=10,
                score_threshold=0.0,
                filters={"type": "resource", "user_id": "user_1"},
            )
            self.assertEqual(len(user_1_results), 1)
            self.assertEqual(user_1_results[0]["metadata"].get("user_id"), "user_1")

            user_2_results = await service.search(
                query="FastAPI resource",
                top_k=10,
                score_threshold=0.0,
                filters={"type": "resource", "user_id": "user_2"},
            )
            self.assertEqual(len(user_2_results), 1)
            self.assertEqual(user_2_results[0]["metadata"].get("user_id"), "user_2")


if __name__ == "__main__":
    unittest.main()
