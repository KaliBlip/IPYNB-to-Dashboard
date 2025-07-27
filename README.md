# Jupyter Notebook Dashboard Generator

A Python tool to convert Jupyter Notebooks into beautiful, static HTML dashboards by extracting plots and markdown content.

## Core Functionality

- **Content Extraction:**
  - Parses Jupyter notebook (`.ipynb`) files (JSON format)
  - Extracts all plots (PNG, JPEG, SVG) from code cell outputs
  - Collects markdown cell content with basic formatting
  - Automatically detects dashboard title from the first H1 header

- **Dashboard Templates:**
  - **Default:** Professional layout with sections, styling, and organized content
  - **Minimal:** Clean, simple layout for basic dashboards
  - **Grid:** Modern card-based grid layout with hover effects

- **Key Features:**
  - Converts markdown to HTML (headers, bold, italic, code blocks)
  - Handles base64-encoded images and SVG plots
  - Responsive design for different screen sizes
  - Automatic content pairing between text and visualizations
  - No JavaScript required; all plots are embedded directly in the HTML

## Usage

### Basic usage
```bash
python notebook_dashboard.py my_analysis.ipynb
```

### Specify output file and template
```bash
python notebook_dashboard.py my_analysis.ipynb -o dashboard.html -t grid
```

### Use minimal template
```bash
python notebook_dashboard.py notebook.ipynb -t minimal -o simple_dashboard.html
```

## How It Works

1. **Parsing:** Reads the notebook JSON and identifies markdown cells and code cells with plot outputs
2. **Extraction:** Pulls out image data (PNG/JPEG as base64, SVG as text) and processes markdown content
3. **Generation:** Creates HTML with embedded images and styled content using the selected template
4. **Output:** Saves a self-contained HTML file that can be shared or hosted anywhere

The tool creates completely static dashboards—no JavaScript required—making them perfect for sharing via email, hosting on simple web servers, or embedding in other applications. All plots are embedded directly in the HTML file, so there are no external dependencies.

---

## License
MIT License
