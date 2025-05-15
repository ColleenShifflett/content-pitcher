# Content Pitcher - Content and Queries Analyzer

A Streamlit application that helps content marketers analyze their existing content against search queries to identify keyword optimization opportunities.

![Content Pitcher](https://raw.githubusercontent.com/username/content-pitcher/main/screenshot.png)

## Features

- **Content & Query Analysis**: Upload your existing content and search query data to find optimization opportunities
- **Smart Matching Algorithm**: Analyzes both content text and URL structure to find the best matches for queries
- **Detailed Recommendations**: Suggests whether to add keywords to existing content or create new content
- **Interactive Visualizations**: Includes charts and graphs to help understand your content gap analysis
- **Filtering Options**: Refine analysis results by relevance score and match quality

## Getting Started

### Prerequisites

- Python 3.11+
- Required Python packages (see `requirements.txt`)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/username/content-pitcher.git
   cd content-pitcher
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run contentpitchermvp.py
   ```

4. Open your browser and navigate to http://localhost:8501

### Using with GitHub Codespaces

This project is configured to work with GitHub Codespaces. When you create a codespace for this repository, it will:

1. Set up a Python 3.11 environment
2. Install all required dependencies
3. Start the Streamlit server automatically
4. Forward port 8501 for the web interface

## Usage Guide

1. **Prepare your CSV files**:
   - **Content CSV**: Must contain columns `Content` (page content) and `URL` (page URL)
   - **Queries CSV**: Must contain columns `queries` (search terms) and `avgpos` (average position)

2. **Upload both files** in the application interface

3. **Analyze the results** across three tabs:
   - **Analysis Results**: Table with all recommendations
   - **Visualizations**: Interactive charts showing the data distribution
   - **Summary**: Overview statistics and top recommended URLs

4. **Filter results** using the sidebar controls:
   - Set minimum relevance score threshold
   - Select specific match quality categories

5. **Download the recommendations** as a CSV file for implementation

## How It Works

The application uses a content matching algorithm that:
1. Tokenizes both content and queries into meaningful words
2. Analyzes content text for keyword presence
3. Analyzes URL structure for keyword relevance (with higher weighting)
4. Calculates overall relevance scores
5. Makes recommendations based on match quality
6. Visualizes the results for easy interpretation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Created by Colleen Shifflett
- Built with Streamlit, Pandas, and Altair
