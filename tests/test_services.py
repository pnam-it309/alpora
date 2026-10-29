from dataclasses import dataclass
import unittest
from poly_shell.core.service import BaseService, ServiceRegistry
from poly_shell.contracts.base import BaseDTO


@dataclass
class MockDTO(BaseDTO):
    active: bool = True


class MockService(BaseService):
    def health_check(self) -> bool:
        return True

    def get_state(self) -> MockDTO:
        return MockDTO(active=self.is_running)


class TestServiceCore(unittest.TestCase):
    def setUp(self):
        self.registry = ServiceRegistry()

    def test_service_lifecycle_and_registry(self):
        svc = MockService("mock")
        self.assertFalse(svc.is_running)

        svc.start()
        self.assertTrue(svc.is_running)

        self.registry.register(svc)
        retrieved = self.registry.get("mock")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "mock")

        report = self.registry.health_report()
        self.assertTrue(report.get("mock"))

        state = retrieved.get_state()
        self.assertTrue(state.active)

        self.registry.shutdown_all()
        self.assertEqual(len(self.registry.all()), 0)


if __name__ == "__main__":
    unittest.main()
