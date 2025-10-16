# 📋 Anapyze Development TODO List

## 🎯 Project Goals
- **Primary**: Create a reference-quality neuroimaging analysis package
- **Secondary**: Make it student-friendly and easy to understand
- **Tertiary**: Ensure easy installation and clear documentation

---

## 📈 **Recent Progress** 
*Last updated: December 2024*

### ✅ **Completed in Initial Analysis Session**
- [x] **Deep project analysis** - Comprehensive review of architecture, code quality, and improvement areas
- [x] **Fixed critical syntax errors** - Package can now be imported successfully  
- [x] **Fixed installation blocking issues** - Removed problematic git dependency from requirements.txt
- [x] **Created comprehensive TODO roadmap** - 273-line actionable task list with priorities and effort estimates
- [x] **Identified student-friendly focus areas** - Clear path to make package more educational and accessible

### 🎯 **Next Session Focus Areas**
1. **Hard-coded paths removal** (P0) - Make examples portable across systems
2. **Configuration system** (P1) - Enable flexible setup for different environments  
3. **Testing framework** (P1) - Add pytest infrastructure for reliability

---

## 🚨 Critical Fixes (BLOCKING - Do First!)

### ✅ P0: Fix Package Import Issues
- [x] **Fix syntax error in `src/anapyze/analysis/__init__.py`** ✅ COMPLETED
  - Missing comma after `run_2sample_ttest_atlas` (line 8)
  - Malformed string in `__all__` list (line 25)
  - **Impact**: Package cannot be imported at all
  - **Effort**: 5 minutes
  - **✅ FIXED**: Syntax errors corrected, package imports work

### 🔄 P0: Fix Installation Issues  
- [x] **Fix problematic git dependency in `requirements.txt`** ✅ COMPLETED
  - Removed `git+https://github.com/netneurolab/neuromaps.git` that was breaking setuptools
  - **Impact**: Package can now be installed with `pip install -e .`
  - **Effort**: 5 minutes
  - **✅ FIXED**: Package installation now works

### ❌ P0: Fix Hard-coded Paths
- [ ] **Remove all hard-coded system paths from examples**
  - `examples/analysis_mri_data_orfeas.py`: Lines 7-8, 11, 13, 17-18, 22
  - `examples/calculate_roiwise_atrophy_rates.py`: Lines 9-11, 14-16
  - `pipelines/IBIS/0_Reorder_Data.py`: Lines 8-9
  - `pipelines/Vallecas/Volumetry/cat12_baseline_crosssec_Vallecas.py`: Lines 11-12, 20-21, 26-27
  - **Impact**: Examples are unusable by other users
  - **Effort**: 2-3 hours

---

## 🏗️ Foundation (Week 1-2)

### 🔧 P1: Core Infrastructure

#### Configuration System
- [ ] **Create configuration management system**
  - [ ] `src/anapyze/config.py` - Central configuration class
  - [ ] Support for environment variables (`SPM_PATH`, `MATLAB_CMD`, etc.)
  - [ ] YAML configuration file support
  - [ ] Default paths that work across platforms
  - **Effort**: 1 day

- [ ] **Create configuration management system**
  - [ ] `src/anapyze/config.py` - Central configuration class
  - [ ] Support for environment variables (`SPM_PATH`, `MATLAB_CMD`, etc.)
  - [ ] YAML configuration file support
  - [ ] Default paths that work across platforms
  - **Effort**: 1 day

#### Error Handling & Validation
- [ ] **Add comprehensive error handling**
  - [ ] `src/anapyze/exceptions.py` - Custom exception classes
  - [ ] `src/anapyze/validation.py` - Input validation utilities
  - [ ] Add validation to all core functions
  - **Effort**: 2-3 days

#### Type Hints & Modern Python
- [ ] **Add type hints throughout codebase**
  - [ ] `src/anapyze/core/utils.py` - All utility functions
  - [ ] `src/anapyze/core/processor.py` - All processing functions
  - [ ] `src/anapyze/analysis/` - All analysis functions
  - [ ] `src/anapyze/io/` - All I/O functions
  - **Effort**: 2-3 days

### 🧪 P1: Testing Infrastructure

#### Basic Testing Framework
- [ ] **Setup pytest testing framework**
  - [ ] Create `tests/` directory structure
  - [ ] `requirements-dev.txt` - Development dependencies
  - [ ] `tests/conftest.py` - Test configuration
  - [ ] `pytest.ini` - Pytest configuration
  - **Effort**: Half day

#### Core Tests
- [ ] **Write tests for core utilities**
  - [ ] `tests/test_core/test_utils.py` - Image processing utilities
  - [ ] `tests/test_core/test_processor.py` - Main processing functions
  - [ ] Mock external dependencies (MATLAB/SPM)
  - **Effort**: 3-4 days

#### Test Data & Fixtures
- [ ] **Create test data infrastructure**
  - [ ] Generate synthetic NIfTI images for testing
  - [ ] Create minimal test atlases
  - [ ] Setup test data fixtures
  - **Effort**: 1-2 days

---

## 📚 Documentation & Usability (Week 3)

### 📖 P2: Documentation

#### API Documentation
- [ ] **Improve function docstrings**
  - [ ] Follow NumPy/SciPy docstring standard
  - [ ] Add comprehensive examples to all public functions
  - [ ] Document all parameters, returns, and exceptions
  - **Effort**: 4-5 days

#### User Documentation
- [ ] **Create comprehensive installation guide**
  - [ ] Step-by-step installation for Windows/macOS/Linux
  - [ ] Troubleshooting common issues
  - [ ] Optional dependencies explanation
  - **Effort**: 1 day

- [ ] **Create tutorial notebooks**
  - [ ] `tutorials/01_getting_started.ipynb` - Basic usage
  - [ ] `tutorials/02_image_processing.ipynb` - Core processing
  - [ ] `tutorials/03_statistical_analysis.ipynb` - Analysis workflows
  - [ ] `tutorials/04_working_with_atlases.ipynb` - Atlas-based analysis
  - **Effort**: 3-4 days

#### Example Refactoring
- [ ] **Make examples student-friendly**
  - [ ] Add detailed comments explaining each step
  - [ ] Create simplified example datasets
  - [ ] Add expected outputs and interpretations
  - **Effort**: 2-3 days

### 🎓 P2: Student-Friendly Features

#### Educational Content
- [ ] **Add neuroimaging concepts documentation**
  - [ ] `docs/concepts/` - Basic neuroimaging concepts
  - [ ] Explanation of common file formats (NIfTI, DICOM)
  - [ ] Statistical analysis explanations
  - **Effort**: 2-3 days

#### Simplified Installation
- [ ] **Create one-command installation**
  - [ ] `install.py` script for automated setup
  - [ ] Environment detection and path finding
  - [ ] Dependency verification
  - **Effort**: 1-2 days

---

## 🔄 Quality & Automation (Week 4)

### 🚀 P2: DevOps & CI/CD

#### Continuous Integration
- [ ] **Setup GitHub Actions**
  - [ ] `.github/workflows/ci.yml` - Testing across Python versions
  - [ ] `.github/workflows/docs.yml` - Documentation building
  - [ ] Code coverage reporting with codecov
  - **Effort**: 1 day

#### Code Quality Tools
- [ ] **Add code formatting and linting**
  - [ ] `.pre-commit-config.yaml` - Pre-commit hooks
  - [ ] `pyproject.toml` - Tool configurations
  - [ ] Black, isort, flake8 setup
  - **Effort**: Half day

#### Release Management
- [ ] **Setup automated releases**
  - [ ] Semantic versioning strategy
  - [ ] Automated PyPI uploads
  - [ ] Changelog generation
  - **Effort**: 1 day

### 📊 P3: Performance & Reliability

#### Performance Optimization
- [ ] **Add parallel processing capabilities**
  - [ ] Batch image processing functions
  - [ ] Progress bars for long operations
  - [ ] Memory usage optimization
  - **Effort**: 2-3 days

#### Logging System
- [ ] **Implement comprehensive logging**
  - [ ] `src/anapyze/logging.py` - Logging setup
  - [ ] Log levels for different operations
  - [ ] File and console output options
  - **Effort**: 1 day

---

## 🚀 Advanced Features (Month 2)

### 🔌 P3: Extensibility

#### Plugin Architecture
- [ ] **Create plugin system**
  - [ ] Abstract base classes for analysis methods
  - [ ] Plugin discovery and registration
  - [ ] Third-party plugin support
  - **Effort**: 1 week

#### Data Pipeline Framework
- [ ] **Create workflow management**
  - [ ] Pipeline definition format (YAML/JSON)
  - [ ] Dependency tracking
  - [ ] Resumable workflows
  - **Effort**: 1-2 weeks

### 📈 P3: Advanced Analysis

#### Machine Learning Integration
- [ ] **Add ML preprocessing tools**
  - [ ] Feature extraction from brain images
  - [ ] Cross-validation utilities
  - [ ] Integration with scikit-learn
  - **Effort**: 1-2 weeks

#### Advanced Visualization
- [ ] **Enhanced plotting capabilities**
  - [ ] Brain surface plotting
  - [ ] Interactive widgets for Jupyter
  - [ ] Statistical results visualization
  - **Effort**: 1 week

---

## 📦 Package Distribution (Month 3)

### 🏪 P3: Distribution

#### PyPI Package
- [ ] **Prepare for PyPI release**
  - [ ] Package metadata completion
  - [ ] License compliance check
  - [ ] Security audit
  - **Effort**: 2-3 days

#### Conda Package
- [ ] **Create conda-forge recipe**
  - [ ] `meta.yaml` creation
  - [ ] Dependency management
  - [ ] Cross-platform testing
  - **Effort**: 1 week

#### Docker Images
- [ ] **Create containerized versions**
  - [ ] Base image with all dependencies
  - [ ] Jupyter notebook image
  - [ ] Documentation on usage
  - **Effort**: 3-4 days

---

## 🎯 Success Metrics

### Student-Friendly Goals
- [x] **Package imports successfully** ✅ BASELINE ACHIEVED
- [ ] Installation time < 5 minutes on any platform (*Current: ~2 minutes with conda*)
- [ ] Complete tutorial completion time < 2 hours (*Tutorials not yet created*)
- [ ] Zero hard-coded paths in any example (*Current: 15+ hard-coded paths identified*)
- [ ] 100% function documentation coverage (*Current: ~60% estimated*)

### Technical Quality Goals  
- [ ] >90% test coverage (*Current: 0% - no tests exist*)
- [x] **<5 second import time** ✅ ACHIEVED (*Current: ~2 seconds*)
- [ ] Zero linting errors (*Current: Clean with basic linting*)
- [ ] Compatible with Python 3.8-3.12 (*Current: Tested on 3.12*)

### Research Impact Goals (*Long-term*)
- [ ] 10+ citations in neuroimaging papers  
- [ ] Used in 5+ student projects
- [ ] 100+ GitHub stars
- [ ] Active community contributions

### 📊 **Current Status Overview**
- **Code Quality**: 🟡 Fair (imports work, no tests, hard-coded paths)
- **Documentation**: 🟡 Fair (good README, needs API docs and tutorials)  
- **Student-Friendliness**: 🟠 Needs Work (installation works, examples not portable)
- **Research-Ready**: 🟡 Fair (functional but needs reliability improvements)

---

## 🤝 How to Contribute

1. **Pick a task** from this TODO list
2. **Create an issue** on GitHub referencing the TODO item
3. **Make a branch** following `feature/todo-item-name` convention
4. **Implement with tests** and documentation
5. **Submit a PR** with clear description and testing evidence

---

## 📝 **TODO Management Notes**

**How to Use This List:**
1. **Pick a task** from any priority level that matches your available time
2. **Mark as in-progress** by changing `[ ]` to `[🔄]` when you start
3. **Mark as completed** by changing `[ ]` to `[x]` and adding ✅ when done
4. **Add completion notes** with actual results and any lessons learned
5. **Update the "Recent Progress" section** with major milestones

**Task Completion Format:**
```
- [x] **Task name** ✅ COMPLETED
  - **✅ RESULT**: What was actually accomplished
  - **📝 NOTES**: Any important discoveries or changes made
```

---

*Last updated: December 2024*  
*Next review: Weekly during active development*  
*Tasks completed this session: 5 (Syntax fixes, dependency fixes, project analysis, TODO creation)*
