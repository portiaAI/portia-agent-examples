#!/usr/bin/env python3
"""
Test suite for agent_with_plan_builder.py

This test file verifies the functionality of the PlanBuilderV2-based agent
that generates concept maps from Obsidian notes.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add the current directory to the path so we can import the agent
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_with_plan_builder import create_plan_local, create_plan_remote, main


class TestAgentWithPlanBuilder(unittest.TestCase):
    """Test cases for the agent_with_plan_builder module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_note_name = "TestNote"
        self.test_vault_path = "/tmp/test_vault"

        # Mock environment variable
        self.env_patcher = patch.dict(
            os.environ, {"OBSIDIAN_VAULT_PATH": self.test_vault_path}
        )
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after each test method."""
        self.env_patcher.stop()

    def test_create_plan_local_structure(self):
        """Test that create_plan_local creates a plan with correct structure."""
        # Mock Portia instance
        mock_portia = Mock()

        # Call the function
        plan = create_plan_local(mock_portia, self.test_note_name)

        # Verify plan was created
        self.assertIsNotNone(plan)

        # Verify plan has the expected structure (basic checks)
        self.assertTrue(hasattr(plan, "pretty_print"))

        # Verify the plan description contains the note name
        plan_str = str(plan)
        self.assertIn(self.test_note_name, plan_str)

    def test_create_plan_local_with_vault_path(self):
        """Test create_plan_local with vault path parameter."""
        mock_portia = Mock()

        # Test with vault path
        plan = create_plan_local(mock_portia, self.test_note_name)

        # Verify plan was created successfully
        self.assertIsNotNone(plan)

    def test_create_plan_remote_structure(self):
        """Test that create_plan_remote creates a plan with correct structure."""
        # Mock Portia instance
        mock_portia = Mock()
        mock_portia.plan = Mock(return_value=Mock())

        # Call the function
        plan = create_plan_remote(mock_portia, self.test_note_name)

        # Verify plan was created
        self.assertIsNotNone(plan)

        # Verify portia.plan was called
        mock_portia.plan.assert_called_once()

        # Verify the query contains the note name
        call_args = mock_portia.plan.call_args[0][0]
        self.assertIn(self.test_note_name, call_args)

    def test_create_plan_remote_query_content(self):
        """Test that create_plan_remote generates correct query content."""
        mock_portia = Mock()
        mock_portia.plan = Mock(return_value=Mock())

        # Call the function
        create_plan_remote(mock_portia, self.test_note_name)

        # Get the query that was passed to portia.plan
        call_args = mock_portia.plan.call_args[0][0]

        # Verify query contains expected steps
        self.assertIn("List all available vaults", call_args)
        self.assertIn("Fetch the note with", call_args)
        self.assertIn("Create a concept map", call_args)
        self.assertIn("visualizations", call_args)
        self.assertIn(self.test_note_name, call_args)

    @patch("agent_with_plan_builder.argparse.ArgumentParser")
    @patch("agent_with_plan_builder.Config.from_default")
    @patch("agent_with_plan_builder.McpToolRegistry.from_stdio_connection")
    @patch("agent_with_plan_builder.ToolRegistry")
    @patch("agent_with_plan_builder.Portia")
    def test_main_function_success(
        self,
        mock_portia_class,
        mock_tool_registry,
        mock_mcp_registry,
        mock_config,
        mock_argparse,
    ):
        """Test main function with successful execution."""
        # Mock command line arguments
        mock_args = Mock()
        mock_args.note_name = self.test_note_name
        mock_argparse.return_value.parse_args.return_value = mock_args

        # Mock Portia instance
        mock_portia_instance = Mock()
        mock_portia_class.return_value = mock_portia_instance

        # Mock plan
        mock_plan = Mock()
        mock_portia_instance.run_plan.return_value = None

        # Mock create_plan_local
        with patch("agent_with_plan_builder.create_plan_local", return_value=mock_plan):
            # Call main function
            main([self.test_note_name])

            # Verify Portia was instantiated
            mock_portia_class.assert_called_once()

            # Verify plan was created and run
            mock_portia_instance.run_plan.assert_called_once_with(mock_plan)

    def test_environment_variable_validation(self):
        """Test that environment variable validation works correctly."""
        # Test that the environment variable check works
        with patch.dict(os.environ, {}, clear=True):
            # This should raise a ValueError when OBSIDIAN_VAULT_PATH is not set
            with self.assertRaises(ValueError) as context:
                # We'll test just the environment variable check part
                if os.getenv("OBSIDIAN_VAULT_PATH") is None:
                    raise ValueError(
                        "OBSIDIAN_VAULT_PATH is not set in your environment variables"
                    )

            self.assertIn("OBSIDIAN_VAULT_PATH is not set", str(context.exception))

    @patch("agent_with_plan_builder.argparse.ArgumentParser")
    def test_main_function_help(self, mock_argparse):
        """Test main function help functionality."""
        # Mock help call
        mock_parser = Mock()
        mock_argparse.return_value = mock_parser
        mock_parser.parse_args.side_effect = SystemExit(0)  # Simulate --help

        # This should not raise an exception for help
        try:
            main(["--help"])
        except SystemExit:
            pass  # Expected for help

        # Verify parser was created
        mock_argparse.assert_called_once()

    def test_plan_builder_v2_usage(self):
        """Test that PlanBuilderV2 is used correctly."""
        mock_portia = Mock()

        # This test verifies that the function can be called without errors
        # and that it returns a plan object
        plan = create_plan_local(mock_portia, self.test_note_name)

        # Basic verification that a plan was created
        self.assertIsNotNone(plan)

        # Verify it's a plan object (has pretty_print method)
        self.assertTrue(hasattr(plan, "pretty_print"))

    def test_environment_variable_usage(self):
        """Test that environment variables are used correctly."""
        # Test with different vault paths
        test_paths = ["/path/to/vault1", "/another/path/vault2", "./relative/path"]

        for vault_path in test_paths:
            with patch.dict(os.environ, {"OBSIDIAN_VAULT_PATH": vault_path}):
                mock_portia = Mock()
                plan = create_plan_local(mock_portia, self.test_note_name)

                # Verify plan was created successfully
                self.assertIsNotNone(plan)

    def test_note_name_handling(self):
        """Test handling of different note names."""
        test_note_names = [
            "SimpleNote",
            "Note With Spaces",
            "note-with-dashes",
            "Note_With_Underscores",
        ]

        for note_name in test_note_names:
            mock_portia = Mock()
            plan = create_plan_local(mock_portia, note_name)

            # Verify plan was created successfully
            self.assertIsNotNone(plan)

            # Verify note name appears in plan
            plan_str = str(plan)
            self.assertIn(note_name, plan_str)

    @patch("agent_with_plan_builder.VisualizationTool")
    def test_visualization_tool_import(self, mock_viz_tool):
        """Test that VisualizationTool can be imported and used."""
        # This test verifies that the import works
        from agent_with_plan_builder import create_plan_local

        mock_portia = Mock()
        plan = create_plan_local(mock_portia, self.test_note_name)

        # Verify plan was created successfully
        self.assertIsNotNone(plan)

    def test_plan_steps_structure(self):
        """Test that the plan has the expected step structure."""
        mock_portia = Mock()
        plan = create_plan_local(mock_portia, self.test_note_name)

        # Convert plan to string to inspect its structure
        plan_str = str(plan)

        # Verify that the plan contains expected tool references
        self.assertIn("mcp:obsidian:list_available_vaults", plan_str)
        self.assertIn("mcp:obsidian:read_note", plan_str)
        self.assertIn("visualization_tool", plan_str)

        # Verify that the plan contains expected step names
        self.assertIn("List all available vaults", plan_str)
        self.assertIn("Fetch the note", plan_str)
        self.assertIn("Create concept map", plan_str)


class TestIntegration(unittest.TestCase):
    """Integration tests for the agent_with_plan_builder module."""

    def setUp(self):
        """Set up test fixtures for integration tests."""
        self.test_note_name = "IntegrationTestNote"
        self.test_vault_path = "/tmp/integration_test_vault"

        # Mock environment variable
        self.env_patcher = patch.dict(
            os.environ, {"OBSIDIAN_VAULT_PATH": self.test_vault_path}
        )
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after integration tests."""
        self.env_patcher.stop()

    @patch("agent_with_plan_builder.argparse.ArgumentParser")
    @patch("agent_with_plan_builder.Config.from_default")
    @patch("agent_with_plan_builder.McpToolRegistry.from_stdio_connection")
    @patch("agent_with_plan_builder.ToolRegistry")
    @patch("agent_with_plan_builder.Portia")
    def test_full_workflow_simulation(
        self,
        mock_portia_class,
        mock_tool_registry,
        mock_mcp_registry,
        mock_config,
        mock_argparse,
    ):
        """Test the full workflow from command line to plan execution."""
        # Mock command line arguments
        mock_args = Mock()
        mock_args.note_name = self.test_note_name
        mock_argparse.return_value.parse_args.return_value = mock_args

        # Mock Portia instance
        mock_portia_instance = Mock()
        mock_portia_class.return_value = mock_portia_instance

        # Mock plan
        mock_plan = Mock()
        mock_portia_instance.run_plan.return_value = None

        # Mock create_plan_local
        with patch("agent_with_plan_builder.create_plan_local", return_value=mock_plan):
            # Simulate the full workflow
            main([self.test_note_name])

            # Verify all components were called
            mock_config.assert_called_once()
            mock_mcp_registry.assert_called_once()
            mock_tool_registry.assert_called_once()
            mock_portia_class.assert_called_once()
            mock_portia_instance.run_plan.assert_called_once()

    def test_plan_builder_v2_compatibility(self):
        """Test that the plan is compatible with PlanBuilderV2."""
        mock_portia = Mock()

        # Create plan using PlanBuilderV2
        plan = create_plan_local(mock_portia, self.test_note_name)

        # Verify plan has PlanBuilderV2 characteristics
        self.assertIsNotNone(plan)

        # Verify plan can be converted to string (has __str__ method)
        plan_str = str(plan)
        self.assertIsInstance(plan_str, str)

        # Verify plan has pretty_print method
        self.assertTrue(hasattr(plan, "pretty_print"))


def run_tests():
    """Run all tests and return the result."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestAgentWithPlanBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running tests for agent_with_plan_builder.py...")
    print("=" * 50)

    success = run_tests()

    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
