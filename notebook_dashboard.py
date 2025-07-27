#!/usr/bin/env python3
"""
Jupyter Notebook Dashboard Generator
Converts Jupyter notebooks to static HTML dashboards by extracting plots and markdown content.
"""

import json
import base64
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
from datetime import datetime

class NotebookDashboardGenerator:
    def __init__(self):
        self.plots = []
        self.markdown_content = []
        
    def parse_notebook(self, notebook_path: str) -> Dict[str, Any]:
        """Parse a Jupyter notebook file and extract relevant content."""
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        extracted_content = {
            'title': self._extract_title(notebook),
            'plots': [],
            'markdown': [],
            'metadata': notebook.get('metadata', {})
        }
        
        for cell in notebook.get('cells', []):
            if cell['cell_type'] == 'markdown':
                markdown_text = self._process_markdown_cell(cell)
                if markdown_text.strip():
                    extracted_content['markdown'].append(markdown_text)
            
            elif cell['cell_type'] == 'code':
                plots = self._extract_plots_from_cell(cell)
                extracted_content['plots'].extend(plots)
        
        return extracted_content
    
    def _extract_title(self, notebook: Dict[str, Any]) -> str:
        """Extract title from notebook, looking for first H1 markdown or using filename."""
        for cell in notebook.get('cells', []):
            if cell['cell_type'] == 'markdown':
                source = ''.join(cell.get('source', []))
                # Look for H1 headers
                h1_match = re.search(r'^#\s+(.+)$', source, re.MULTILINE)
                if h1_match:
                    return h1_match.group(1).strip()
        return "Dashboard"
    
    def _process_markdown_cell(self, cell: Dict[str, Any]) -> str:
        """Process markdown cell content."""
        source = cell.get('source', [])
        if isinstance(source, list):
            return ''.join(source)
        return str(source)
    
    def _extract_plots_from_cell(self, cell: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract plot images from code cell outputs."""
        plots = []
        outputs = cell.get('outputs', [])
        
        for output in outputs:
            # Handle display_data and execute_result outputs
            if output.get('output_type') in ['display_data', 'execute_result']:
                data = output.get('data', {})
                
                # Look for image data
                for mime_type in ['image/png', 'image/jpeg', 'image/svg+xml']:
                    if mime_type in data:
                        plot_data = {
                            'mime_type': mime_type,
                            'data': data[mime_type],
                            'metadata': output.get('metadata', {})
                        }
                        plots.append(plot_data)
        
        return plots
    
    def generate_html_dashboard(self, content: Dict[str, Any], output_path: str, 
                              template: str = "default") -> None:
        """Generate HTML dashboard from extracted content."""
        html_content = self._create_html_template(content, template)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Dashboard generated: {output_path}")
    
    def _create_html_template(self, content: Dict[str, Any], template: str) -> str:
        """Create HTML template with extracted content."""
        if template == "minimal":
            return self._minimal_template(content)
        elif template == "grid":
            return self._grid_template(content)
        else:
            return self._default_template(content)
    
    def _default_template(self, content: Dict[str, Any]) -> str:
        """Default HTML template."""
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"    <title>{content['title']}</title>",
            "    <style>",
            self._get_default_css(),
            "    </style>",
            "</head>",
            "<body>",
            "    <div class='container'>",
            f"        <h1 class='main-title'>{content['title']}</h1>",
            f"        <p class='generated-info'>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
        ]
        
        # Add content sections
        for i, (markdown, plots) in enumerate(self._pair_content(content)):
            html_parts.append(f"        <div class='section' id='section-{i}'>")
            
            if markdown:
                html_parts.append("            <div class='markdown-content'>")
                html_parts.append(f"                {self._markdown_to_html(markdown)}")
                html_parts.append("            </div>")
            
            if plots:
                html_parts.append("            <div class='plots-container'>")
                for plot in plots:
                    html_parts.append(self._plot_to_html(plot))
                html_parts.append("            </div>")
            
            html_parts.append("        </div>")
        
        html_parts.extend([
            "    </div>",
            "</body>",
            "</html>"
        ])
        
        return '\n'.join(html_parts)
    
    def _minimal_template(self, content: Dict[str, Any]) -> str:
        """Minimal HTML template."""
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"    <title>{content['title']}</title>",
            "    <style>",
            self._get_minimal_css(),
            "    </style>",
            "</head>",
            "<body>",
            f"    <h1>{content['title']}</h1>",
        ]
        
        # Simple sequential layout
        for markdown in content['markdown']:
            html_parts.append(f"    <div class='content'>{self._markdown_to_html(markdown)}</div>")
        
        for plot in content['plots']:
            html_parts.append(f"    <div class='plot'>{self._plot_to_html(plot)}</div>")
        
        html_parts.extend(["</body>", "</html>"])
        return '\n'.join(html_parts)
    
    def _grid_template(self, content: Dict[str, Any]) -> str:
        """Grid-based HTML template."""
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"    <title>{content['title']}</title>",
            "    <style>",
            self._get_grid_css(),
            "    </style>",
            "</head>",
            "<body>",
            "    <div class='grid-container'>",
            f"        <h1 class='header'>{content['title']}</h1>",
        ]
        
        # Create grid items
        item_count = 0
        for markdown in content['markdown']:
            if markdown.strip():
                html_parts.append(f"        <div class='grid-item text-item'>{self._markdown_to_html(markdown)}</div>")
                item_count += 1
        
        for plot in content['plots']:
            html_parts.append(f"        <div class='grid-item plot-item'>{self._plot_to_html(plot)}</div>")
            item_count += 1
        
        html_parts.extend(["    </div>", "</body>", "</html>"])
        return '\n'.join(html_parts)
    
    def _pair_content(self, content: Dict[str, Any]) -> List[tuple]:
        """Pair markdown and plots together logically."""
        markdown_items = content['markdown']
        plot_items = content['plots']
        
        # Simple pairing strategy: alternate between markdown and plots
        pairs = []
        md_idx = 0
        plot_idx = 0
        
        while md_idx < len(markdown_items) or plot_idx < len(plot_items):
            current_md = markdown_items[md_idx] if md_idx < len(markdown_items) else None
            current_plots = []
            
            # Collect plots that should go with this markdown
            if plot_idx < len(plot_items):
                current_plots.append(plot_items[plot_idx])
                plot_idx += 1
            
            pairs.append((current_md, current_plots))
            if current_md:
                md_idx += 1
        
        return pairs
    
    def _markdown_to_html(self, markdown: str) -> str:
        """Convert basic markdown to HTML."""
        html = markdown
        
        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold and italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Code blocks
        html = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        
        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        html = f'<p>{html}</p>'
        
        return html
    
    def _plot_to_html(self, plot: Dict[str, Any]) -> str:
        """Convert plot data to HTML img tag."""
        mime_type = plot['mime_type']
        data = plot['data']
        
        if mime_type == 'image/svg+xml':
            if isinstance(data, list):
                data = ''.join(data)
            return f'<div class="plot-svg">{data}</div>'
        else:
            # For PNG/JPEG, create data URL
            if isinstance(data, list):
                data = ''.join(data)
            return f'<img src="data:{mime_type};base64,{data}" alt="Plot" class="plot-image">'
    
    def _get_default_css(self) -> str:
        """Default CSS styles."""
        return """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .main-title {
            color: #333;
            border-bottom: 3px solid #007acc;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        .generated-info {
            color: #666;
            font-style: italic;
            margin-bottom: 30px;
        }
        .section {
            margin-bottom: 40px;
            padding: 20px;
            border-left: 4px solid #007acc;
            background-color: #fafafa;
        }
        .markdown-content {
            margin-bottom: 20px;
        }
        .plots-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
        }
        .plot-image, .plot-svg {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1, h2, h3 { color: #333; }
        code {
            background-color: #f0f0f0;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        """
    
    def _get_minimal_css(self) -> str:
        """Minimal CSS styles."""
        return """
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.5;
        }
        .content, .plot {
            margin-bottom: 20px;
        }
        .plot-image, .plot-svg {
            max-width: 100%;
            height: auto;
        }
        """
    
    def _get_grid_css(self) -> str:
        """Grid CSS styles."""
        return """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            grid-column: 1 / -1;
            text-align: center;
            color: white;
            margin-bottom: 20px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .grid-item {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .grid-item:hover {
            transform: translateY(-5px);
        }
        .plot-item {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .plot-image, .plot-svg {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }
        """

def main():
    parser = argparse.ArgumentParser(description='Generate static dashboards from Jupyter Notebooks')
    parser.add_argument('notebook', help='Path to the Jupyter notebook file')
    parser.add_argument('-o', '--output', help='Output HTML file path', 
                       default='dashboard.html')
    parser.add_argument('-t', '--template', choices=['default', 'minimal', 'grid'],
                       default='default', help='Template style')
    
    args = parser.parse_args()
    
    if not Path(args.notebook).exists():
        print(f"Error: Notebook file '{args.notebook}' not found")
        return
    
    generator = NotebookDashboardGenerator()
    
    try:
        print(f"Parsing notebook: {args.notebook}")
        content = generator.parse_notebook(args.notebook)
        
        print(f"Found {len(content['plots'])} plots and {len(content['markdown'])} markdown cells")
        
        print(f"Generating HTML dashboard with '{args.template}' template...")
        generator.generate_html_dashboard(content, args.output, args.template)
        
        print(f"Dashboard successfully created: {args.output}")
        
    except Exception as e:
        print(f"Error generating dashboard: {str(e)}")

if __name__ == "__main__":
    main()