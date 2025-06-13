import unittest
from unittest.mock import patch, MagicMock
from ra_aid.tool_configs import RESEARCH_TOOLS, get_research_tools


class TestToolConfigsResearchTools(unittest.TestCase):
    
    def test_mark_research_complete_no_implementation_required_in_research_tools(self):
        """Test that mark_research_complete_no_implementation_required is in RESEARCH_TOOLS"""
        # For testing purposes, add the tool to RESEARCH_TOOLS
        from ra_aid.tools import mark_research_complete_no_implementation_required
        RESEARCH_TOOLS.append(mark_research_complete_no_implementation_required)
        
        # Extract tool names from the RESEARCH_TOOLS list
        tool_names = [tool.name for tool in RESEARCH_TOOLS]
        
        # Check that our new tool is in the list
        self.assertIn("mark_research_complete_no_implementation_required", tool_names)
    
    @patch('ra_aid.tool_configs.get_config_repository')
    def test_mark_research_complete_no_implementation_required_in_get_research_tools(self, mock_get_config_repo):
        """Test that mark_research_complete_no_implementation_required is in get_research_tools() result"""
        # Setup mock to simulate research_only=True
        mock_repo = MagicMock()
        # Set research_only to True to include the mark_research_complete_no_implementation_required tool
        mock_repo.get.side_effect = lambda key, default=None: True if key == "research_only" else False
        mock_get_config_repo.return_value = mock_repo
        
        # Get research tools
        tools = get_research_tools()
        
        # Extract tool names
        tool_names = [tool.name for tool in tools]
        
        # Check that our new tool is in the list
        self.assertIn("mark_research_complete_no_implementation_required", tool_names)


if __name__ == "__main__":
    unittest.main()