from unittest.mock import Mock, patch


from org_info.org_structured_info.gsoc_org_page import (
    get_org_details_gsoc_page,
)


def test_returns_matching_organizations():
    fake_response = Mock()

    fake_response.json.return_value = {
        "organizations": [
            {
                "name": "Eclipse Foundation",
                "technologies": ["java", "python"],
                "topics": ["open source"],
            },
            {
                "name": "VideoLAN",
                "technologies": ["c", "c++"],
                "topics": ["video"],
            },
        ]
    }

    fake_response.raise_for_status.return_value = None

    with patch(
        "org_info.org_structured_info.gsoc_org_page.requests.get",
        return_value=fake_response,
    ):
        result = get_org_details_gsoc_page(
            ["Eclipse Foundation"]
        )

    assert "Eclipse Foundation" in result
    assert "VideoLAN" not in result

    assert result["Eclipse Foundation"]["technologies"] == [
        "java",
        "python",
    ]


def test_returns_multiple_matching_organizations():
    fake_response = Mock()

    fake_response.json.return_value = {
        "organizations": [
            {"name": "FOSSASIA", "technologies": ["python"]},
            {"name": "Metaflow", "technologies": ["python"]},
            {"name": "VideoLAN", "technologies": ["c", "c++"]},
        ]
    }

    fake_response.raise_for_status.return_value = None

    with patch(
        "org_info.org_structured_info.gsoc_org_page.requests.get",
        return_value=fake_response,
    ):
        result = get_org_details_gsoc_page(
            ["FOSSASIA", "Metaflow"]
        )

    assert len(result) == 2
    assert "FOSSASIA" in result
    assert "Metaflow" in result
    assert "VideoLAN" not in result


def test_returns_empty_dict_when_no_match():
    fake_response = Mock()

    fake_response.json.return_value = {
        "organizations": [
            {
                "name": "VideoLAN",
                "technologies": ["c", "c++"],
            }
        ]
    }

    fake_response.raise_for_status.return_value = None

    with patch(
        "org_info.org_structured_info.gsoc_org_page.requests.get",
        return_value=fake_response,
    ):
        result = get_org_details_gsoc_page(
            ["FOSSASIA"]
        )

    assert result == {}


def test_raise_for_status_is_called():
    fake_response = Mock()

    fake_response.json.return_value = {
        "organizations": []
    }

    with patch(
        "org_info.org_structured_info.gsoc_org_page.requests.get",
        return_value=fake_response,
    ):
        get_org_details_gsoc_page(["FOSSASIA"])

    fake_response.raise_for_status.assert_called_once()