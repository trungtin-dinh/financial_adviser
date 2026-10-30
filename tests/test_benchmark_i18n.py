from financial_adviser.benchmark_i18n import TXT, b


def test_all_display_languages_share_compatible_keys():
    assert set(TXT) == {'fr','en','vi'}
    keys=set(TXT['fr'])
    assert all(set(group)==keys for group in TXT.values())
    assert all(b(lang,key) for lang in TXT for key in TXT[lang] if '{' not in TXT[lang][key])


def test_no_language_fallback():
    import pytest
    with pytest.raises(KeyError):b('vi','nonexistent')
    with pytest.raises(KeyError):b('de','title')
