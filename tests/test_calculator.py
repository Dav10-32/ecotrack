import pytest

from ecotrack.calculator import analyze, apply_bottled_water, normalize


def test_ejemplo_del_enunciado():
    r = analyze("Hoy comí carne y viajé 20km en bus")
    assert {i.key for i in r.items} == {"res", "bus"}
    assert r.total_kg == pytest.approx(6.5 + 20 * 0.089, abs=0.01)
    assert r.unrecognized == []


def test_pollo_no_se_cuenta_como_res():
    r = analyze("Comí carne de pollo")
    assert [i.key for i in r.items] == ["pollo"]


def test_cantidades_en_numero_y_palabra():
    assert analyze("comí 2 hamburguesas").total_kg == pytest.approx(13.0)
    assert analyze("comí dos hamburguesas").total_kg == pytest.approx(13.0)


def test_distancia_en_otra_clausula():
    r = analyze("Viajé en bus, 20 km")
    assert r.total_kg == pytest.approx(1.78, abs=0.01)


def test_decimales_con_coma():
    assert analyze("fui 1,5 km en moto").total_kg == pytest.approx(1.5 * 0.113, abs=0.01)


def test_bici_y_caminar_son_cero():
    r = analyze("Fui en bici al trabajo")
    assert r.total_kg == 0
    assert r.items[0].key == "bici"


def test_electricidad():
    assert analyze("gasté 10 kWh").total_kg == pytest.approx(1.26, abs=0.01)


def test_tildes_y_mayusculas():
    assert normalize("Comí CARNE en Avión") == "comi carne en avion"
    assert analyze("VIAJÉ 100 KILÓMETROS EN AVIÓN").total_kg == pytest.approx(25.5, abs=0.1)


def test_texto_vacio_o_sin_actividades():
    assert analyze("").total_kg == 0
    r = analyze("hola, qué tal")
    assert r.items == [] and r.unrecognized


def test_transporte_sin_distancia_se_reporta():
    r = analyze("viajé en bus")
    assert r.items == []
    assert any("distancia" in u.lower() for u in r.unrecognized)


def test_sugerencia_menciona_mayor_impacto():
    assert "pollo" in analyze("comí carne").suggestion().lower()
    assert "bus" in analyze("fui 30 km en carro").suggestion().lower()


def test_agua_embotellada_suma_al_total():
    r = analyze("comí pollo")
    apply_bottled_water(r, 2)
    assert any(i.key == "agua_embotellada" for i in r.items)
    assert r.total_kg == pytest.approx(1.7 + 2 * 0.25, abs=0.01)
    apply_bottled_water(r, 0)  # no debe añadir ítem
    assert sum(1 for i in r.items if i.key == "agua_embotellada") == 1
