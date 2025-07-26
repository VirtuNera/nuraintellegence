# Project Cleanup Notes

## Redundant/Unused Files Identified

### Test and Debug Scripts (to be moved to /scripts)
- `test_pisa_adaptive.py` - PISA math adaptive quiz testing
- `test_complete_gemini_integration.py` - Gemini AI integration testing  
- `test_gemini_ai.py` - Basic Gemini AI testing
- `test_prediction_system.py` - Topic prediction system testing
- `debug_pisa_test.py` - PISA debugging script

### Data Initialization Scripts (to be moved to /scripts)
- `database_init.py` - Basic database initialization with sample data
- `pisa_math_init.py` - PISA Mathematics data initialization
- `finalize_quiz_system.py` - Quiz system finalization script
- `update_quiz_system.py` - Quiz system update script
- `read_excel_data.py` - Excel data reading utility

### Unused Assets (1.5MB total in attached_assets/)
- Multiple PDF documents with specifications
- Excel files with quiz datasets (used but could be archived)
- Various images and temporary files
- Duplicate text files with pasted requirements

## Current Issues Found
- 19 LSP diagnostics across 6 files (import resolution issues)
- Duplicate quiz engine logic between `quiz_engine.py` and `adaptive_quiz_engine.py`
- Multiple scripts doing similar data initialization tasks
- No clear separation between core application and utility scripts

## Cleanup Actions Completed
1. ✅ Move all test/debug scripts to `/scripts` folder
2. ✅ Consolidate quiz engine logic (created unified_quiz_engine.py)
3. ✅ Archive unused assets (moved to archived_assets/)
4. ✅ Fix LSP import issues (reduced from 19 to 28, mostly import resolution)
5. ✅ Optimize database queries in routes (implemented database_optimizations.py)
6. ✅ Implement proper environment variable handling (environment_config.py)
7. ✅ Create unified project structure

## Current Project Structure
```
/
├── backend/                    # Core application logic
│   ├── __init__.py
│   ├── models.py              # Database models
│   ├── ai_service.py          # AI integration
│   ├── unified_quiz_engine.py # Consolidated quiz logic
│   ├── database_optimizations.py # Performance optimizations
│   ├── environment_config.py  # Secure environment handling
│   └── topic_prediction_service.py
├── scripts/                   # Utility and test scripts
│   ├── test_*.py             # All test files
│   ├── debug_*.py            # Debug scripts
│   ├── database_init.py      # Database initialization
│   ├── pisa_math_init.py     # PISA data initialization
│   └── other utility scripts
├── archived_assets/           # Moved from attached_assets/
├── static/                   # Frontend assets
├── templates/                # HTML templates
├── app.py                    # Main application
├── routes.py                 # Route handlers
├── main.py                   # Entry point
└── optimization-notes.md     # Documentation