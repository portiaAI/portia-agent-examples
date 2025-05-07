"""
Visualization Tool for creating concept maps.

This module provides a tool for creating concept map visualizations from relationships
between concepts. It uses matplotlib and networkx to generate visual representations
of concept relationships and saves them as image files.
"""

try:
    import matplotlib
    matplotlib.use('Agg')  # Use the Agg backend which doesn't require a GUI
    import matplotlib.pyplot as plt
    import networkx as nx
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("Warning: matplotlib or networkx not installed. Visualization tool will not be available.")

import os
from typing import List, Tuple
from pydantic import BaseModel, Field
from portia import Tool, ToolRunContext

class VisualizationSchema(BaseModel):
    """
    Input schema for the VisualizationTool.
    
    This schema defines the required and optional parameters for creating
    concept map visualizations.
    """
    
    relationships: List[List[str]] = Field(
        ...,
        description="List of relationships in format [source, target, relationship_type]"
    )
    title: str = Field(
        "Concept Map",
        description="Title for the concept map"
    )
    output_dir: str = Field(
        default="visualizations",
        description="Directory to save the visualization image"
    )

class VisualizationTool(Tool[str]):
    """
    Tool for creating visualizations of concepts and their relationships.
    
    This tool generates concept map visualizations from a list of relationships
    between concepts. It uses networkx for graph creation and matplotlib for
    visualization, saving the resulting image to a specified directory.
    """
    
    id: str = "visualization_tool"
    name: str = "Visualization Tool"
    description: str = """
    This tool creates concept map visualization image and saves it to the specified output directory.
    """
    args_schema: type[BaseModel] = VisualizationSchema
    output_schema: tuple[str, str] = ("str", "Path to the saved visualization image file")
    
    def run(self, ctx: ToolRunContext, 
            relationships: List[List[str]], 
            title: str,
            output_dir: str) -> str:
        """
        Run the Visualization Tool to create a concept map.
        
        Args:
            ctx: The tool run context
            relationships: List of relationships in format [source, target, relationship_type]
            title: Title for the visualization
            output_dir: Directory to save the visualization
            
        Returns:
            Path to the saved visualization file
        """
        if not VISUALIZATION_AVAILABLE:
            return "Error: Visualization libraries not available. Please install matplotlib and networkx with 'pip install matplotlib networkx'."
            
        if not relationships:
            return "Error: 'relationships' are required for concept maps"
        
        # Validate relationships format
        for rel in relationships:
            if len(rel) < 3:
                return f"Error: Each relationship must have 3 elements [source, target, relationship_type]. Found: {rel}"
        
        # Convert relationships to tuples
        formatted_relationships = [(rel[0], rel[1], rel[2]) for rel in relationships]
        
        # Extract concepts from relationships
        concepts = set()
        for source, target, _ in formatted_relationships:
            concepts.add(source)
            concepts.add(target)
        
        return self._create_concept_map(list(concepts), formatted_relationships, title, output_dir)
    
    def _create_concept_map(self, concepts: List[str], relationships: List[Tuple[str, str, str]], title: str, output_dir: str) -> str:
        """
        Create a network graph showing relationships between concepts using NetworkX.
        
        This method generates a directed graph visualization where:
        - Nodes represent concepts
        - Edges represent relationships between concepts
        - Edge labels show the type of relationship
        
        Args:
            concepts: List of concept strings to be represented as nodes
            relationships: List of (source, target, relationship_type) tuples
            title: Title for the visualization
            output_dir: Directory to save the visualization image
            
        Returns:
            Path to the saved visualization file or an error message
        """
        try:
            # Create a directed graph
            G = nx.DiGraph()
            
            # Add nodes from concepts list
            for concept in concepts:
                G.add_node(concept)
            
            # Add edges with relationship types as labels
            edge_labels = {}
            for source, target, rel_type in relationships:
                G.add_edge(source, target)
                edge_labels[(source, target)] = rel_type
            
            # Create the visualization with a larger figure size
            plt.figure(figsize=(24, 18))
            
            # Choose layout based on graph size
            if len(G.nodes) <= 10:
                pos = nx.circular_layout(G, scale=2.0)
            else:
                pos = nx.spring_layout(G, k=2.0, iterations=100, seed=42, scale=2.0)
            
            # Draw edges with visible arrows
            nx.draw_networkx_edges(
                G, 
                pos,
                width=2.0,
                edge_color='darkgray',
                alpha=1.0,  # Full opacity
                arrowsize=20,  # Even larger arrows
                arrowstyle='-|>',  # Arrow style that extends beyond nodes
                node_size=2000,  # This is key - tells edge drawing the node size to avoid
                min_source_margin=15,  # Start edges outside the node
                min_target_margin=25   # End edges outside the node
            )
            
            # Draw nodes
            nx.draw_networkx_nodes(
                G, 
                pos,
                node_color='lightblue',
                node_size=2000,  # Smaller fixed size nodes
                alpha=0.9,
                linewidths=2,
                edgecolors='blue'
            )
            
            # Draw node labels
            nx.draw_networkx_labels(
                G,
                pos,
                font_size=12,
                font_weight='bold',
                font_color='black'
            )
            
            # Draw edge labels
            nx.draw_networkx_edge_labels(
                G, 
                pos, 
                edge_labels=edge_labels, 
                font_size=10,
                font_color='darkblue',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8),
                rotate=False,
                label_pos=0.5
            )
            
            plt.title(title, fontsize=20)
            plt.axis('off')
            plt.tight_layout(pad=5.0)
            
            # Save the figure
            os.makedirs(output_dir, exist_ok=True)
            filename = f"{output_dir}/{title.replace(' ', '_')}.png"
            plt.savefig(filename, bbox_inches='tight', dpi=300)
            plt.close()
            
            print(f"Created concept map with {len(G.nodes)} nodes and {len(G.edges)} edges")
            return filename
        except Exception as e:
            print(f"Error creating concept map: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Failed to create concept map: {str(e)}"
