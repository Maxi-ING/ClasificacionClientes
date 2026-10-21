from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_navigation_and_filters():
    """Los informes publicados permiten abrir el resumen sin descargar el dataset."""
    app = AppTest.from_file(str(ROOT / "app/dashboard.py"), default_timeout=30).run()
    assert not app.exception
    assert len(app.metric) == 4
    for page in ["Segmentos", "Método", "Clientes", "Resumen"]:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception
        if page == "Clientes" and app.multiselect:
            app.multiselect[0].set_value([]).run()
            assert not app.exception
            assert app.metric[0].value == "0"
        if page == "Segmentos":
            app.selectbox[0].select_index(1).run()
            assert not app.exception
            assert "S02" in app.subheader[0].value
