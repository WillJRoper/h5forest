"""Tests for h5forest.progress module."""

from unittest.mock import Mock, patch

import pytest

from h5forest.progress import ProgressBar


class TestProgressBar:
    """Test the ProgressBar class."""

    def test_progress_bar_init(self):
        """Test ProgressBar initialization."""
        with patch("h5forest.h5_forest.H5Forest") as mock_forest_class, patch(
            "h5forest.progress.get_window_size"
        ) as mock_get_window_size:
            mock_forest = Mock()
            mock_forest_class.return_value = mock_forest
            mock_get_window_size.return_value = (24, 80)

            pb = ProgressBar(total=100, description="test")

            assert pb.total_steps == 100
            assert pb.current_step == 0
            assert pb.description == "test"

    def test_progress_bar_update(self):
        """Test ProgressBar update method."""
        with patch("h5forest.h5_forest.H5Forest") as mock_forest_class, patch(
            "h5forest.progress.get_window_size"
        ) as mock_get_window_size:
            mock_forest = Mock()
            mock_forest_class.return_value = mock_forest
            mock_get_window_size.return_value = (24, 80)

            pb = ProgressBar(total=100)
            pb.update_progress(25)

            assert pb.current_step == 25
            # Should update text area
            assert hasattr(pb, "text_area")

    def test_progress_bar_advance(self):
        """Test ProgressBar advance method."""
        with patch("h5forest.h5_forest.H5Forest") as mock_forest_class, patch(
            "h5forest.progress.get_window_size"
        ) as mock_get_window_size:
            mock_forest = Mock()
            mock_forest_class.return_value = mock_forest
            mock_get_window_size.return_value = (24, 80)

            pb = ProgressBar(total=100)
            pb.advance(step=25)

            assert pb.current_step == 25

    def test_progress_bar_context_manager(self):
        """Test ProgressBar as context manager."""
        with patch("h5forest.h5_forest.H5Forest") as mock_forest_class, patch(
            "h5forest.progress.get_window_size"
        ) as mock_get_window_size:
            mock_forest = Mock()
            mock_forest_class.return_value = mock_forest
            mock_get_window_size.return_value = (24, 80)

            with ProgressBar(total=100) as pb:
                pb.advance(50)
                assert pb.current_step == 50

    def test_progress_bar_with_zero_total(self):
        """Test ProgressBar with zero total (edge case)."""
        with patch("h5forest.h5_forest.H5Forest") as mock_forest_class, patch(
            "h5forest.progress.get_window_size"
        ) as mock_get_window_size:
            mock_forest = Mock()
            mock_forest_class.return_value = mock_forest
            mock_get_window_size.return_value = (24, 80)

            pb = ProgressBar(total=0)

            # Zero total causes division by zero, so we expect an exception
            with pytest.raises(ZeroDivisionError):
                pb.update_progress(0)

            assert pb.current_step == 0

    def test_progress_bar_description(self):
        """Test ProgressBar with description."""
        with patch("h5forest.h5_forest.H5Forest") as mock_forest_class, patch(
            "h5forest.progress.get_window_size"
        ) as mock_get_window_size:
            mock_forest = Mock()
            mock_forest_class.return_value = mock_forest
            mock_get_window_size.return_value = (24, 80)

            pb = ProgressBar(total=100, description="Processing")

            assert pb.description == "Processing"
            assert pb.total_steps == 100
