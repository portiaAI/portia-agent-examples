import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Add the parent directory to the path to import the visualization module
sys.path.append(str(Path(__file__).parent.parent))
from tools.visualization_tool import VisualizationTool, VISUALIZATION_AVAILABLE

class TestVisualizationTool(unittest.TestCase):
    def setUp(self):
        # Skip all tests if visualization is not available
        if not VISUALIZATION_AVAILABLE:
            self.skipTest("Visualization libraries not available")
            
        # Create a test output directory
        self.test_output_dir = "test_visualizations"
        os.makedirs(self.test_output_dir, exist_ok=True)
        self.visualization_tool = VisualizationTool()
        
        # Create a mock context instead of trying to instantiate ToolRunContext
        self.ctx = MagicMock()
    
    def tearDown(self):
        # Uncomment the following lines if you want to clean up after tests
        # import shutil
        # if os.path.exists(self.test_output_dir):
        #     shutil.rmtree(self.test_output_dir)
        pass
    
    def test_simple_concept_map(self):
        """Test creating a simple concept map."""
        # Define a minimal test case
        relationships = [
            ["A", "B", "connects to"],
            ["B", "C", "relates to"],
            ["C", "A", "influences"]
        ]
        
        # Run the tool
        result = self.visualization_tool.run(
            ctx=self.ctx,
            relationships=relationships,
            title="Simple_Test",
            output_dir=self.test_output_dir
        )
        
        print(f"Simple concept map result: {result}")
        self.assertTrue(os.path.exists(result), "Concept map file should exist")
        self.assertTrue(result.endswith(".png"), "Result should be a PNG file")
        
        # Check file size to ensure it's a valid image
        file_size = os.path.getsize(result)
        self.assertGreater(file_size, 1000, "File size should be greater than 1KB")
    
    def test_coffee_concept_map(self):
        """Test creating a concept map about coffee brewing methods."""
        
        # Define relationships
        relationships = [
            ["Coffee Beans", "French Press", "used in"],
            ["Coffee Beans", "Pour Over", "used in"],
            ["Coffee Beans", "Espresso", "used in"],
            ["Coffee Beans", "Cold Brew", "used in"],
            ["Coffee Beans", "AeroPress", "used in"],
            ["Water Quality", "Taste", "affects"],
            ["Grind Size", "French Press", "coarse for"],
            ["Grind Size", "Pour Over", "medium for"],
            ["Grind Size", "Espresso", "fine for"],
            ["Grind Size", "Cold Brew", "coarse for"],
            ["Brewing Time", "French Press", "4 minutes for"],
            ["Brewing Time", "Cold Brew", "12-24 hours for"],
            ["French Press", "Full-bodied Coffee", "produces"],
            ["Pour Over", "Clean Flavors", "produces"],
            ["Espresso", "Concentrated Coffee", "produces"],
            ["Cold Brew", "Low Acidity Coffee", "produces"],
            ["AeroPress", "Versatile Coffee", "produces"]
        ]
        
        # Run the tool
        result = self.visualization_tool.run(
            ctx=self.ctx,
            relationships=relationships,
            title="Coffee_Brewing_Methods",
            output_dir=self.test_output_dir
        )
        
        print(f"Coffee concept map result: {result}")
        self.assertTrue(os.path.exists(result), "Concept map file should exist")
        self.assertTrue(result.endswith(".png"), "Result should be a PNG file")

if __name__ == "__main__":
    unittest.main() 