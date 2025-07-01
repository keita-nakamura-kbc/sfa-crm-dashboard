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
  - **cards.py**: KPI cards, performance cards, trend items with optimized sparklines
  - **charts.py**: Chart creation functions with consistent styling
  - **header.py**: Header component with logo integration
- **layouts/**: Tab-specific layouts (tab1_funnel.py, tab2_revenue.py)  
- **callbacks/**: Tab-specific callback handlers for interactivity
  - **tab1_callbacks.py**: Funnel analysis logic without period concepts
  - **tab2_callbacks.py**: Revenue/acquisition analysis with period switching
- **assets/**: CSS files and static resources
  - **style.css**: Global styles with CSS custom properties
  - **tab1-specific.css**: Tab1 specialized styles
  - **w_logo.webp**: Service logo image

### Data Flow
1. Excel files uploaded via header component (supports 'w_logo.webp' branding)
2. DataManager processes Excel sheets using EXCEL_STRUCTURE config
3. Data stored in dcc.Store components for client-side caching
4. Tab-specific callbacks update visualizations using calculate_kpi_values() for consistency
5. Filtering optimization prevents double application across the pipeline

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

#### Windows EXE Creation
For Windows distribution, use the provided Windows-specific files:

```bash
# Method 1: Use automated batch script (Windows only)
build_exe.bat

# Method 2: Use PyInstaller spec file (Windows only)
pyinstaller build_windows.spec

# Method 3: Manual command (Windows only)
pyinstaller --onefile --windowed --add-data "assets;assets" --add-data "components;components" --add-data "layouts;layouts" --add-data "callbacks;callbacks" --add-data "images;images" --add-data "pdca_2025.xlsx;." --hidden-import dash_bootstrap_components --name "SFA-CRM-Dashboard" main.py
```

#### Cross-Platform Build (macOS/Linux)
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable (creates platform-specific binary)
pyinstaller --onefile --add-data "assets:assets" --add-data "components:components" --add-data "layouts:layouts" --add-data "callbacks:callbacks" --hidden-import dash_bootstrap_components main.py

# Executable will be in dist/ directory
```

**Important Notes**:
- Windows .exe files must be built on Windows systems
- `build_windows_guide.md` contains comprehensive Windows build instructions
- `build_exe.bat` provides automated Windows build process
- `build_windows.spec` contains optimized Windows configuration

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
- **CRITICAL**: Use calculate_kpi_values() for all KPI calculations to ensure consistency
- **CRITICAL**: Avoid double filtering - either pre-filter data OR let calculate_kpi_values() handle filtering, never both
- CV rate calculation: Uses actual achievement rate (actual/plan×100) not fixed baseline
- Plan value synchronization: Card displays use last valid month's plan value to match sparklines

### Performance Optimizations (Recent Improvements)
- **Sparkline Enhancement**: Width increased to 100px-120px, line thickness 3px, marker size 5px
- **KPI Card Sorting**: 0%/N/A achievement rates placed at bottom using custom sort logic
- **Achievement Rate Synchronization**: Global last month ensures consistent line lengths across stages
- **Filtering Optimization**: Single-pass filtering prevents redundant data processing
- **Color Coding**: Performance-based heatmap colors for plan ratios in CV rate cards

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
4. **IMPORTANT**: Match sparkline styling (width: 100px-120px, line thickness: 3px)

### Adding New Callbacks
1. Add to appropriate callbacks/ file
2. Register in main.py via register_tabX_callbacks()
3. Use dcc.Store for state management between callbacks
4. **CRITICAL**: Always use calculate_kpi_values() for data calculations
5. **CRITICAL**: Avoid double filtering patterns - see "Common Pitfalls" section

### Data Calculation Standards
- Use calculate_kpi_values(data, section, month, data_type, period_type, channel_filter, plan_filter)
- For composition charts: Use same logic as acquisition cards for consistency
- For sparklines: Use get_monthly_trend_data() with appropriate filters
- Achievement rate sorting: 0% and N/A values go to bottom

### Customization
- Modify DARK_COLORS in config.py for theme changes
- Update LAYOUT dict for responsive adjustments  
- Extend EXCEL_STRUCTURE for new data source formats
- Section titles: Use dash format "構成 - 種別" instead of parentheses

### Error Handling
- Use try/except blocks in callbacks to handle data processing errors
- Return empty charts/components when data is unavailable
- Log errors using Python's logging module

### Code Quality Practices
- No unused imports or commented-out code
- .gitignore file prevents Python cache files and development artifacts
- Clean project structure with only essential files
- Consistent Japanese text encoding in tooltips (avoid f-string + double curly braces)

## Common Pitfalls & Solutions

### Double Filtering Issues
**Problem**: Data gets filtered twice, causing incorrect values
**Example**: Pre-filtering data then passing to calculate_kpi_values() which filters again
**Solution**: Either filter data manually OR use calculate_kpi_values(), never both

```python
# WRONG - Double filtering
filtered_df = apply_filters(df, channel_filter, plan_filter)
actual_val, budget_val = calculate_kpi_values(data, 'acquisition', month, 'actual', 'single', channel_filter, plan_filter)

# RIGHT - Single filtering via calculate_kpi_values
actual_val, budget_val = calculate_kpi_values(data, 'acquisition', month, 'actual', 'single', channel_filter, plan_filter)
```

### Achievement Rate Line Length Issues
**Problem**: Different stages show achievement rate lines ending at different months
**Cause**: Each stage filtering individually, stages with no early data appear to end early
**Solution**: Use global last month for all stages to ensure consistency

```python
# Get global last month first
global_last_month = get_last_data_month(all_filtered_data, month_cols)
# Use this for all stages instead of stage-specific last months
```

### Tab1 vs Tab2 Period Concepts
**Critical Understanding**: 
- **Tab1 (Funnel)**: No cumulative/single month concept - always display raw data
- **Tab2 (Revenue/Acquisition)**: Has period switching between cumulative and single month
- Tab1 composite chart should NOT respond to period toggle buttons

### Flex Layout Issues (Tab2)
**Problem**: Layout sections shrinking unexpectedly
**Solution**: Use `flex: 0 0 X%` not `flex: 0 1 X%` to prevent shrinking
**Pattern**: 30:45:25 ratio for Tab2 rows (Row1:Row2:Row3)

### KPI Card Sorting Edge Cases
**Problem**: 0% and N/A achievement rates appearing randomly in sort order
**Solution**: Custom sort key that places these values at bottom
```python
def sort_key(item):
    rate = item.get('achievement_rate', 0)
    if rate == 0 or pd.isna(rate):
        return (1, 0)  # Bottom priority
    return (0, -rate)  # Normal sorting
```

## Important Notes

### Application Startup
- The app runs on port 8050 by default with debug=True in development
- Sample data file 'pdca_2025.xlsx' is automatically loaded on startup
- The app expects Excel files with a '25年PDCA' sheet name
- `load_sample_data_on_startup()` function handles automatic data loading in both development and production

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

## Recent Architecture Improvements

### Data Calculation Standardization
- **calculate_kpi_values()**: Unified function for all KPI calculations across dashboard
- **Consistent Filtering**: Single-pass filtering eliminates redundant operations
- **Performance Colors**: get_performance_color() provides consistent heatmap coloring
- **Global Month Synchronization**: Ensures achievement rate lines have consistent lengths

### UI/UX Enhancements  
- **Enhanced Sparklines**: 100px-120px width, 3px line thickness, 5px markers for better visibility
- **Improved Sorting**: KPI cards place 0%/N/A achievement rates at bottom for better UX
- **Logo Integration**: Header supports service logo (w_logo.webp) replacing text branding
- **Color-Coded Performance**: Plan ratios in CV rate cards use performance-based colors
- **Section Title Format**: Standardized to "構成 - 種別" dash format

### Layout Optimizations
- **Tab2 Reorganization**: Composition charts moved below corresponding acquisition cards
- **Height Consistency**: Composition charts match retention/unit price section heights (40% flex)
- **Flex Layout Stability**: Fixed shrinking issues with `flex: 0 0 X%` patterns

## Critical Patterns & Standards

### Data Processing Pipeline
1. **Single Source of Truth**: calculate_kpi_values() for all KPI calculations
2. **Filter Once**: Avoid double filtering - let calculate_kpi_values() handle filters
3. **Global Synchronization**: Use global last month for achievement rate line consistency
4. **Composition Chart Parity**: Use same calculation logic as corresponding KPI cards

### Tab-Specific Logic
- **Tab1**: No period concepts, always raw data display, achievement lines synchronized globally
- **Tab2**: Period switching (cumulative/single), composition charts below acquisition cards
- **Cross-Tab Consistency**: Shared functions ensure consistent calculations across tabs

### Performance Optimizations  
- **Client-Side Caching**: dcc.Store components minimize server round-trips
- **Single-Pass Filtering**: Eliminates redundant apply_filters() calls
- **Optimized Rendering**: Minimal re-renders through strategic callback design

## Decisions and Clarifications

- **User-facing text**: "達成率" → "計画比" for all display text
- **Internal code**: Achievement rate calculation logic remains unchanged  
- **Terminology**: "予算"、"計画値"、"予算値" → "計画" に統一したい
- **Section titles**: "構成（種別）" → "構成 - 種別" format standardization
- **Funnel chart**: Display only actual values in boxes (not percentages)
- **Layout hierarchy**: Composition charts positioned below corresponding acquisition cards
- **Performance colors**: Apply heatmap coloring to plan ratios in CV rate trend cards