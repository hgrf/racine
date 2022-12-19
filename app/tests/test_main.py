import os

from .. import create_app

def test_instantiate_app():
    """Test that the app can be instantiated."""
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    assert app is not None