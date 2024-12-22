import pytest
from pydantic import BaseModel
from template.utils.version import LocalMetadata


def test_basic_meta_init_state_ok():
    m = LocalMetadata.local_metadata()
    assert m.head != "head error"
    assert m.remote_head != "remote head error"
    assert m.btversion != "metadata exception"
    assert m.uid == 0
    assert m.coldkey == ""
    assert m.hotkey == ""
    assert isinstance(m.head, str)

    print(m.head)
    print(m.remote_head)
    print(m.btversion)


def test_local_version_matches_head():
    m = LocalMetadata.local_metadata()
    
    if(m.head != m.remote_head):
        print("WARNING Versions do not match - ensure on main branch and updated")

    assert m.head == m.remote_head


def test_version_check_expected_ok():
    m = LocalMetadata.local_metadata()
    match_result = m.version_match()
    if not match_result:
        assert m.head != m.remote_head
    else:
        assert m.head == m.remote_head
    