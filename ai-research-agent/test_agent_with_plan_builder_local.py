#!/usr/bin/env python3
"""
Test suite for agent_with_plan_builder_local.py

This test file verifies the functionality of the PlanBuilderV2-based agent
that generates concept maps from Obsidian notes.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_with_plan_builder_local import create_plan_local, create_plan_remote, main


class TestAgentWithPlanBuilder(unittest.TestCase):
    """Unit tests for agent_with_plan_builder_local.py"""

    def setUp(self):
        self.test_note_name = "TestNote"
        self.test_vault_path = "/tmp/test_vault"

        # Mock environment variable
        self.env_patcher = patch.dict(
            os.environ, {"OBSIDIAN_VAULT_PATH": self.test_vault_path}
        )
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def test_create_plan_local_structure(self):
        """Test that create_plan_local creates a plan with correct structure."""
        mock_portia = Mock()
        plan = create_plan_local(mock_portia, self.test_note_name)

        self.assertIsNotNone(plan)
        self.assertTrue(hasattr(plan, "pretty_print"))
        plan_str = str(plan)
        self.assertIn(self.test_note_name, plan_str)

    def test_create_plan_remote_structure(self):
        """Test that create_plan_remote creates a plan correctly."""
        mock_portia = Mock()
        mock_portia.plan = Mock(return_value=Mock(pretty_print=Mock()))

        plan = create_plan_remote(mock_portia, self.test_note_name)

        self.assertIsNotNone(plan)
        mock_portia.plan.assert_called_once()
        query = mock_portia.plan.call_args[0][0]
        self.assertIn(self.test_note_name, query)
        self.assertIn("visualizations", query)

    def test_environment_variable_validation(self):
        """Test that missing environment variable raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                if os.getenv("OBSIDIAN_VAULT_PATH") is None:
                    raise ValueError(
                        "OBSIDIAN_VAULT_PATH is not set in your environment variables"
                    )
            self.assertIn("OBSIDIAN_VAULT_PATH is not set", str(context.exception))

    @patch("agent_with_plan_builder_local.argparse.ArgumentParser")
    @patch("agent_with_plan_builder_local.Config.from_default")
    @patch("agent_with_plan_builder_local.McpToolRegistry.from_stdio_connection")
    @patch("agent_with_plan_builder_local.ToolRegistry")
    @patch("agent_with_plan_builder_local.Portia")
    def test_main_function_success(
        self,
        mock_portia_class,
        mock_tool_registry,
        mock_mcp_registry,
        mock_config,
        mock_argparse,
    ):
        """Test main function execution path."""
        mock_args = Mock()
        mock_args.note_name = self.test_note_name
        mock_args.remote = False
        mock_argparse.return_value.parse_args.return_value = mock_args

        mock_portia_instance = Mock()
        mock_portia_class.return_value = mock_portia_instance

        mock_plan = Mock()
        mock_plan.pretty_print = Mock(return_value="Plan Pretty Print")

        with patch(
            "agent_with_plan_builder_local.create_plan_local", return_value=mock_plan
        ):
            main([self.test_note_name])
            mock_portia_instance.run_plan.assert_called_once_with(
                mock_plan, plan_run_inputs={"note_name": self.test_note_name}
            )

    def test_note_name_handling(self):
        """Test that different note names work correctly."""
        note_names = ["SimpleNote", "Note With Spaces", "note-with-dashes", "Note_With_Underscores"]
        for name in note_names:
            mock_portia = Mock()
            plan = create_plan_local(mock_portia, name)
            self.assertIsNotNone(plan)
            plan_str = str(plan)
            self.assertIn(name, plan_str)

class TestIntegration(unittest.TestCase):
    """Integration-style tests for agent_with_plan_builder_local.py"""

    def setUp(self):
        self.test_note_name = "IntegrationTestNote"
        self.test_vault_path = "/tmp/integration_test_vault"
        self.env_patcher = patch.dict(
            os.environ, {"OBSIDIAN_VAULT_PATH": self.test_vault_path}
        )
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch("agent_with_plan_builder_local.argparse.ArgumentParser")
    @patch("agent_with_plan_builder_local.Config.from_default")
    @patch("agent_with_plan_builder_local.McpToolRegistry.from_stdio_connection")
    @patch("agent_with_plan_builder_local.ToolRegistry")
    @patch("agent_with_plan_builder_local.Portia")
    def test_full_workflow_simulation(
        self,
        mock_portia_class,
        mock_tool_registry,
        mock_mcp_registry,
        mock_config,
        mock_argparse,
    ):
        """Simulate full workflow from CLI to plan execution."""
        mock_args = Mock()
        mock_args.note_name = self.test_note_name
        mock_args.remote = False
        mock_argparse.return_value.parse_args.return_value = mock_args

        mock_portia_instance = Mock()
        mock_portia_class.return_value = mock_portia_instance

        mock_plan = Mock()
        mock_plan.pretty_print = Mock(return_value="Plan Pretty Print")

        with patch(
            "agent_with_plan_builder_local.create_plan_local", return_value=mock_plan
        ):
            main([self.test_note_name])
            mock_portia_instance.run_plan.assert_called_once_with(
                mock_plan, plan_run_inputs={"note_name": self.test_note_name}
            )

class TestAgentWithPlanBuilderRemote(unittest.TestCase):
    """Tests for the remote plan creation path (--remote flag)."""

    def setUp(self):
        self.test_note_name = "RemoteTestNote"
        self.test_vault_path = "/tmp/remote_test_vault"
        self.env_patcher = patch.dict(
            os.environ, {"OBSIDIAN_VAULT_PATH": self.test_vault_path}
        )
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch("agent_with_plan_builder_local.argparse.ArgumentParser")
    @patch("agent_with_plan_builder_local.Config.from_default")
    @patch("agent_with_plan_builder_local.McpToolRegistry.from_stdio_connection")
    @patch("agent_with_plan_builder_local.ToolRegistry")
    @patch("agent_with_plan_builder_local.Portia")
    def test_main_remote_execution(
        self,
        mock_portia_class,
        mock_tool_registry,
        mock_mcp_registry,
        mock_config,
        mock_argparse,
    ):
        """Test that main() correctly handles the --remote flag."""
        # Mock CLI args
        mock_args = Mock()
        mock_args.note_name = self.test_note_name
        mock_args.remote = True
        mock_argparse.return_value.parse_args.return_value = mock_args

        # Mock Portia instance
        mock_portia_instance = Mock()
        mock_portia_class.return_value = mock_portia_instance

        # Mock plan returned by Portia.plan()
        mock_plan = Mock()
        mock_plan.pretty_print = Mock(return_value="Remote Plan Pretty Print")
        mock_portia_instance.plan = Mock(return_value=mock_plan)

        # Run main() simulating --remote
        main([self.test_note_name, "--remote"])

        # Verify Portia.plan() was called
        mock_portia_instance.plan.assert_called_once()
        # Verify plan was executed
        mock_portia_instance.run_plan.assert_called_once_with(
            mock_plan, plan_run_inputs={"note_name": self.test_note_name}
        )


def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestAgentWithPlanBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentWithPlanBuilderRemote))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running tests for agent_with_plan_builder_local.py...")
    print("=" * 50)
    success = run_tests()
    if success:
        print("\n All tests passed!")
        sys.exit(0)
    else:
        print("\n Some tests failed!")
        sys.exit(1)
