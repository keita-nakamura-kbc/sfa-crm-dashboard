# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modern, dark-themed SFA/CRM Analytics Dashboard built with Dash (Python web framework). The application processes Excel data to visualize sales funnel analysis and revenue metrics with an optimized Full HD (1920x1080) interface.

## Architecture

### Core Application Structure
- **main.py**: Entry point with Dash app initialization, global callbacks, and tab management
- **config.py**: All configuration, colors, layouts, data mappings, and Excel structure definitions
- **data_manager.py**: Excel data processing, caching, and data transformation logic

### Modular Components
- **components/**: Reusable UI components (cards, charts, header)
- **layouts/**: Tab-specific layouts (tab1_funnel.py, tab2_revenue.py)  
- **callbacks/**: Tab-specific callback handlers for interactivity
- **assets/**: CSS files (style.css for global styles, tab1-specific.css for Tab1)

### Data Flow
1. Excel files uploaded via header component
2. DataManager processes Excel sheets using EXCEL_STRUCTURE config
3. Data stored in dcc.Store components for client-side caching
4. Tab-specific callbacks update visualizations based on user interactions

## Common Commands

### Development
```bash
# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run application (development mode with auto-reload)
python main.py

# Access dashboard
# http://localhost:8050
```

### Testing & Linting (Optional - tools commented in requirements.txt)
```bash
# Uncomment development dependencies in requirements.txt then:
pip install pytest black flake8

# Run linting
flake8 . --exclude=venv

# Format code
black . --exclude=venv

# Run tests (when created)
pytest
```

### Building Standalone Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --add-data "assets:assets" --add-data "components:components" --add-data "layouts:layouts" --add-data "callbacks:callbacks" --hidden-import dash_bootstrap_components main.py

# Executable will be in dist/ directory
```

### Dependencies
- Dash 2.18.2 for web framework
- Plotly 5.24.1 for charts/visualizations  
- Pandas 2.2.0 for data processing
- openpyxl 3.1.2 for Excel file handling
- Dash Bootstrap Components 1.6.0 for UI components

## Key Technical Details

### Data Source
- Expected Excel file: '25年PDCA' sheet with specific structure defined in config.py
- EXCEL_STRUCTURE maps row/column ranges for different data sections (sales, acquisition, unit_price, retention, indicators)
- DataManager handles file upload, parsing, and validation

### UI Theme System
- All styling defined in DARK_COLORS dict in config.py
- Custom CSS injected via app.index_string in main.py
- Plotly charts use PLOTLY_TEMPLATE for consistent dark theme
- CSS custom properties in assets/style.css for UI tokens (spacing, colors, etc.)

### Component Architecture
- Components are pure functions returning Dash HTML/DCC elements
- Layouts compose components for each tab
- Callbacks handle all user interactions and data updates

### Data Processing
- STAGE_MAPPING and INTEGRATED_STAGES in config.py define funnel stage aggregations
- Helper functions in data_manager.py for cleaning and formatting data
- Client-side data caching using dcc.Store components
- CV rate calculation: Uses actual achievement rate (actual/plan×100) not fixed baseline
- Plan value synchronization: Card displays use last valid month's plan value to match sparklines

### Layout System (Important for Tab2)
- Tab2 sections maintain 30:45:25 ratio (Row1:Row2:Row3)
- Use `flex: 0 0 X%` (not `flex: 0 1 X%`) to prevent flex-shrink issues
- Hierarchical minHeight constraints: container > rows > individual sections
- Strategic `!important` usage for layout stability

## Development Patterns

### Adding New Components
1. Create function in appropriate components/ file
2. Import and use in relevant layout file
3. Follow existing dark theme styling patterns

### Adding New Callbacks
1. Add to appropriate callbacks/ file
2. Register in main.py via register_tabX_callbacks()
3. Use dcc.Store for state management between callbacks

### Customization
- Modify DARK_COLORS in config.py for theme changes
- Update LAYOUT dict for responsive adjustments
- Extend EXCEL_STRUCTURE for new data source formats

### Error Handling
- Use try/except blocks in callbacks to handle data processing errors
- Return empty charts/components when data is unavailable
- Log errors using Python's logging module

### Code Quality Practices
- No unused imports or commented-out code
- .gitignore file prevents Python cache files and development artifacts
- Clean project structure with only essential files
- Consistent Japanese text encoding in tooltips (avoid f-string + double curly braces)

## Important Notes

### Application Startup
- The app runs on port 8050 by default with debug=True in development
- Sample data file 'pdca_2025.xlsx' is included for testing
- The app expects Excel files with a '25年PDCA' sheet name

### Data Store Components
- 'data-store': Main processed data storage
- 'filtered-channels': Channel filter state
- 'filtered-plans': Plan filter state
- 'last-data-month': Tracks most recent data month
- 'channel-filter-tab2': Tab2-specific channel filter
- 'plan-filter-tab2': Tab2-specific plan filter

### Japanese Language Support
- All UI text is in Japanese
- Date formats follow Japanese conventions (e.g., '2025年1月')
- Currency displays as ¥ (Japanese Yen)

### Performance Considerations
- Large Excel files may take time to process
- Data caching reduces repeated calculations
- Component callbacks are optimized to minimize re-renders

### Project Structure Best Practices
- Keep configuration centralized in config.py
- Maintain separation between UI components and business logic
- Use descriptive variable names matching the Japanese business context
- Follow existing code style and patterns

### Chart Tooltip Formatting
- Revenue (売上高) charts: Display tooltips as ¥xxx format
- Acquisition (獲得件数) charts: Display tooltips as xxx format (no currency symbol)
- Uses conditional `value_type` parameter: 'currency' for revenue, 'count' for acquisition
- All hover templates use consistent formatting across chart types

### Missing Infrastructure  
- No automated tests yet - pytest structure ready
- No CI/CD configuration

## Decisions and Clarifications

- User-facing text: "達成率" → "計画比" for all display text
- Internal code: Achievement rate calculation logic remains unchanged
- Terminology: "予算"、"計画値"、"予算値" → "計画" に統一
- Funnel chart: Display only actual values in boxes (not percentages)