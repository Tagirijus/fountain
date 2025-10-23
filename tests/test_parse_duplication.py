"""
Tests for the parse duplication bug fix.

This module tests that the parse() method correctly clears elements and metadata
before parsing, preventing duplication when parse() is called multiple times.
"""

import pytest
from fountain import fountain


def test_multiple_parse_calls_no_duplication():
    """Test that calling parse() multiple times doesn't duplicate elements."""
    test_script = '''Title: Test Script

INT. ROOM - DAY

JOHN
Hello world.

Action text.
'''

    f = fountain.Fountain(test_script)
    initial_count = len(f.elements)

    # Call parse multiple times
    f.parse()
    second_count = len(f.elements)

    f.parse()
    third_count = len(f.elements)

    # All counts should be the same
    assert (
        initial_count == second_count == third_count
    ), f"Elements duplicated: {initial_count} -> {second_count} -> {third_count}"


def test_metadata_cleared_on_reparse():
    """Test that metadata is cleared when parse() is called again."""
    f = fountain.Fountain('Title: First\nAuthor: John\n\nSome text.')

    assert f.metadata.get('title', [''])[0] == 'First'
    assert f.metadata.get('author', [''])[0] == 'John'

    # Change contents and re-parse
    f.contents = 'Title: Second\nAuthor: Jane\n\nOther text.'
    f.parse()

    assert f.metadata.get('title', [''])[0] == 'Second'
    assert f.metadata.get('author', [''])[0] == 'Jane'


def test_elements_cleared_on_reparse():
    """Test that elements are cleared when parse() is called again."""
    f = fountain.Fountain('Title: Test\n\nAction 1.')
    first_element_count = len(f.elements)
    first_text = f.elements[0].element_text if f.elements else ''

    # Change to content with more elements
    f.contents = 'Title: Test\n\nAction 2.\n\nAction 3.\n\nAction 4.'
    f.parse()
    second_element_count = len(f.elements)

    assert second_element_count == 5, f"Expected 5 elements, got {second_element_count}"
    assert (
        first_element_count == 1
    ), f"Expected 1 element initially, got {first_element_count}"
    assert f.elements[0].element_text == 'Action 2.', "Content not updated correctly"


def test_empty_content_handling():
    """Test that empty content is handled without errors."""
    # Create with empty string
    f = fountain.Fountain('')
    assert len(f.elements) == 0
    assert len(f.metadata) == 0

    # Parse again should not cause errors
    f.parse()
    assert len(f.elements) == 0
    assert len(f.metadata) == 0


def test_multiple_parses_with_empty_content():
    """Test multiple parse calls with empty content."""
    f = fountain.Fountain('')

    for _ in range(5):
        f.parse()
        assert len(f.elements) == 0, "Empty content should have 0 elements"
        assert len(f.metadata) == 0, "Empty content should have 0 metadata"


def test_whitespace_only_content():
    """Test that whitespace-only content is treated as empty."""
    f = fountain.Fountain('   \n\n   \t\t\n   ')
    assert len(f.elements) == 0

    f.parse()
    assert len(f.elements) == 0


def test_metadata_only_no_duplication():
    """Test metadata-only content doesn't duplicate on reparse."""
    f = fountain.Fountain('Title: Test\nAuthor: Me')

    initial_metadata_count = len(f.metadata)
    f.parse()
    second_metadata_count = len(f.metadata)

    assert initial_metadata_count == second_metadata_count
    assert len(f.elements) == 0


def test_body_only_no_duplication():
    """Test body-only content doesn't duplicate on reparse."""
    f = fountain.Fountain('Just some action text.')

    initial_count = len(f.elements)
    f.parse()
    second_count = len(f.elements)
    f.parse()
    third_count = len(f.elements)

    assert initial_count == second_count == third_count == 1


def test_complex_script_stability():
    """Test that a complex script remains stable across multiple parses."""
    complex_script = '''Title: Complex Test
Author: Test Author

INT. ROOM - DAY

JOHN enters.

JOHN
Hello there.

MARY (O.S.)
Who's there?

More action here.

EXT. STREET - NIGHT

Different scene.
'''

    f = fountain.Fountain(complex_script)

    # Store initial state
    initial_element_count = len(f.elements)
    initial_metadata_count = len(f.metadata)
    initial_element_types = [el.element_type for el in f.elements]

    # Parse multiple times
    for _ in range(3):
        f.parse()
        assert (
            len(f.elements) == initial_element_count
        ), "Element count changed after reparse"
        assert (
            len(f.metadata) == initial_metadata_count
        ), "Metadata count changed after reparse"
        assert [
            el.element_type for el in f.elements
        ] == initial_element_types, "Element types changed after reparse"


def test_parse_consistency():
    """Test that parse produces consistent results each time."""
    script = '''Title: Test

INT. ROOM - DAY

JOHN
Dialogue here.

Action.
'''

    f = fountain.Fountain(script)

    # Get initial parse results
    initial_elements = [
        (el.element_type, el.element_text, el.original_line) for el in f.elements
    ]

    # Parse again and compare
    f.parse()
    reparsed_elements = [
        (el.element_type, el.element_text, el.original_line) for el in f.elements
    ]

    assert initial_elements == reparsed_elements, "Parse results are not consistent"


@pytest.mark.parametrize('parse_count', [2, 3, 5, 10])
def test_multiple_parse_counts(parse_count):
    """Test various numbers of parse() calls to ensure stability."""
    script = 'Title: Test\n\nINT. ROOM - DAY\n\nAction text.'
    f = fountain.Fountain(script)

    expected_count = len(f.elements)

    for _ in range(parse_count):
        f.parse()
        assert (
            len(f.elements) == expected_count
        ), f"Elements changed after parse (expected {expected_count}, got {len(f.elements)})"


def test_content_replacement_workflow():
    """Test a realistic workflow of replacing content and re-parsing."""
    # Parse first script
    f = fountain.Fountain('Title: First\n\nFirst action.')
    assert f.metadata['title'][0] == 'First'
    assert len(f.elements) == 1
    assert f.elements[0].element_text == 'First action.'

    # Replace with second script
    f.contents = 'Title: Second\n\nSecond action.\n\nMore action.'
    f.parse()
    assert f.metadata['title'][0] == 'Second'
    assert len(f.elements) == 3
    assert f.elements[0].element_text == 'Second action.'

    # Replace with third script (minimal)
    f.contents = 'Just text.'
    f.parse()
    assert len(f.metadata) == 0
    assert len(f.elements) == 1
    assert f.elements[0].element_text == 'Just text.'
