import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

def test_imports():
    print("Testing imports...")
    try:
        import anapyze
        print(f"Successfully imported anapyze version {anapyze.__version__ if hasattr(anapyze, '__version__') else 'unknown'}")
        
        from anapyze.config import config
        print(f"Config loaded. SPM Path: {config.spm_path}")
        
        from anapyze.core import processor
        print("Successfully imported anapyze.core.processor")
        
        from anapyze.io import spm
        print("Successfully imported anapyze.io.spm")
        
        from anapyze.analysis import two_samples
        print("Successfully imported anapyze.analysis.two_samples")
        
        # Check pipelines
        # Note: pipelines might not be a package if it doesn't have __init__.py, but we moved it to src/anapyze/pipelines
        # Let's check if we can import it if it has __init__.py
        try:
            from anapyze import pipelines
            print("Successfully imported anapyze.pipelines")
            import anapyze.pipelines.Vallecas
            print("Successfully imported anapyze.pipelines.Vallecas")
            import anapyze.pipelines.IBIS
            print("Successfully imported anapyze.pipelines.IBIS")
        except ImportError as e:
            print(f"Could not import pipeline submodules: {e}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Import failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_imports()
