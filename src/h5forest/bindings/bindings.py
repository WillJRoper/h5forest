"""A module containing the keybindings for the basic UI.

This module contains the keybindings for the basic UI. These keybindings are
always active and are not dependent on any leader key. The functions in this
module should not be called directly, but are intended to be used by the main
application.
"""

from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Label

from h5forest.bindings.dataset_funcs import (
    close_values,
    mean,
    minimum_maximum,
    show_values,
    show_values_in_range,
    std,
)
from h5forest.bindings.normal_funcs import (
    copy_key,
    dataset_leader_mode,
    exit_app,
    exit_leader_mode,
    goto_leader_mode,
    hist_leader_mode,
    plotting_leader_mode,
    restore_tree_to_initial,
    window_leader_mode,
)
from h5forest.bindings.search_funcs import (
    accept_search_results,
    exit_search_mode,
    search_leader_mode,
)
from h5forest.bindings.tree_funcs import (
    collapse_attributes,
    expand_attributes,
    expand_collapse_node,
    move_down,
    move_down_ten,
    move_left,
    move_right,
    move_up,
    move_up_ten,
)
from h5forest.bindings.utils import translate_key_label


class H5KeyBindings:
    """A class holding and applying keybindings based on application state."""

    def __init__(self, app):
        """Initialize the keybindings."""

        # Attach the application instance
        self.app = app

        # Attach the config instance
        self.config = app.config

        # Is vim mode enabled? This just a friendly pointer to the config
        self.vim_mode_enabled = self.config.vim_mode_enabled()

        # ========== Define attributes to hold all the keys ==========

        # Normal mode keys
        self.dataset_leader_key = self.config.get_keymap(
            "dataset_mode",
            "leader",
        )
        self.goto_leader_key = self.config.get_keymap(
            "jump_mode",
            "leader",
        )
        self.hist_leader_key = self.config.get_keymap(
            "hist_mode",
            "leader",
        )
        self.plot_leader_key = self.config.get_keymap(
            "plot_mode",
            "leader",
        )
        self.window_leader_key = self.config.get_keymap(
            "window_mode",
            "leader",
        )
        self.search_leader_key = self.config.get_keymap(
            "search_mode",
            "leader",
        )
        self.restore_key = self.config.get_keymap(
            "normal_mode",
            "restore_tree",
        )
        self.copy_key_binding = self.config.get_keymap(
            "normal_mode",
            "copy_path",
        )
        self.quit_key = self.config.get_keymap(
            "normal_mode",
            "quit",
        )
        self.toggle_attrs_key = self.config.get_keymap(
            "normal_mode",
            "expand_attributes",
        )

        # Tree keys
        self.expand_collapse_key = self.config.get_keymap(
            "tree_navigation",
            "expand/collapse",
        )
        self.jump_up_key = self.config.get_keymap(
            "tree_navigation",
            "jump_up",
        )

        # Motion keys
        self.jump_down_key = self.config.get_keymap(
            "tree_navigation",
            "jump_down",
        )
        self.move_up_key = self.config.get_keymap(
            "tree_navigation",
            "move_up",
        )
        self.move_down_key = self.config.get_keymap(
            "tree_navigation",
            "move_down",
        )
        self.move_left_key = self.config.get_keymap(
            "tree_navigation",
            "move_left",
        )
        self.move_right_key = self.config.get_keymap(
            "tree_navigation",
            "move_right",
        )
        self.vim_move_up_key = "k"  # Fixed vim key
        self.vim_move_down_key = "j"  # Fixed vim key
        self.vim_move_left_key = "h"  # Fixed vim key
        self.vim_move_right_key = "l"  # Fixed vim key

        # Dataset mode keys
        self.view_values_key = self.config.get_keymap(
            "dataset_mode",
            "view_values",
        )
        self.view_range_key = self.config.get_keymap(
            "dataset_mode",
            "view_values_range",
        )
        self.close_values_key = self.config.get_keymap(
            "dataset_mode",
            "close_values",
        )
        self.min_max_key = self.config.get_keymap(
            "dataset_mode",
            "min_max",
        )
        self.mean_key = self.config.get_keymap(
            "dataset_mode",
            "mean",
        )
        self.std_key = self.config.get_keymap(
            "dataset_mode",
            "std_dev",
        )

        # Search mode keys
        self.accept_search_key = self.config.get_keymap(
            "search_mode",
            "accept_search",
        )
        self.cancel_search_key = self.config.get_keymap(
            "search_mode",
            "cancel_search",
        )
        self.exit_search_key = self.config.get_keymap(
            "search_mode",
            "exit_search",
        )

        # ====== Define attributes to hold all the different labels ======

        # Normal mode labels
        self.dataset_mode_label = Label(
            f"{translate_key_label(self.dataset_leader_key)} → Dataset Mode"
        )
        self.goto_mode_label = Label(
            f"{translate_key_label(self.goto_leader_key)} → Goto Mode"
        )
        self.hist_mode_label = Label(
            f"{translate_key_label(self.hist_leader_key)} → Histogram Mode"
        )
        self.plotting_mode_label = Label(
            f"{translate_key_label(self.plot_leader_key)} → Plotting Mode"
        )
        self.window_mode_label = Label(
            f"{translate_key_label(self.window_leader_key)} → Window Mode"
        )
        self.search_label = Label(
            f"{translate_key_label(self.search_leader_key)} → Search"
        )
        self.restore_tree_label = Label(
            f"{translate_key_label(self.restore_key)} → Restore Tree"
        )
        self.copy_key_label = Label(
            f"{translate_key_label(self.copy_key_binding)} → Copy Key"
        )
        self.exit_label = Label(f"{translate_key_label(self.quit_key)} → Exit")
        self.exit_mode_label = Label(
            f"{translate_key_label(self.quit_key)} → Exit Mode"
        )
        self.expand_attrs_label = Label(
            f"{translate_key_label(self.toggle_attrs_key)} → Expand Attributes"
        )
        self.shrink_attrs_label = Label(
            f"{translate_key_label(self.toggle_attrs_key)} → Shrink Attributes"
        )

        # Tree labels
        self.expand_collapse_label = Label(
            f"{translate_key_label(self.expand_collapse_key)} → "
            "Open/Close Group"
        )
        self.move_ten_label = Label(
            f"{translate_key_label(self.jump_up_key)}/"
            f"{translate_key_label(self.jump_down_key)} → Up/Down 10"
        )

        # Dataset mode labels
        self.view_values_label = Label(
            f"{translate_key_label(self.view_values_key)} → Show Values"
        )
        self.view_range_label = Label(
            f"{translate_key_label(self.view_range_key)} "
            "→ Show Values In Range"
        )
        self.close_values_label = Label(
            f"{translate_key_label(self.close_values_key)} → Close Value View"
        )
        self.min_max_label = Label(
            f"{translate_key_label(self.min_max_key)} → Get Minima and Maxima"
        )
        self.mean_label = Label(
            f"{translate_key_label(self.mean_key)} → Get Mean"
        )
        self.std_label = Label(
            f"{translate_key_label(self.std_key)} → Get Standard Deviation"
        )

        # Search mode labels
        self.accept_search_label = Label(
            f"{translate_key_label(self.accept_search_key)} → Accept"
        )
        self.cancel_search_label = Label(
            f"{translate_key_label(self.exit_search_key)}/"
            f"{translate_key_label(self.cancel_search_key)} → Cancel"
        )

        # ========== Define all the filters we will need ==========

        # Normal mode filters
        self.filter_normal_mode = lambda: app.flag_normal_mode
        self.filter_not_normal_mode = lambda: not app.flag_normal_mode
        self.filter_not_searching = lambda: not app.flag_search_mode
        self.filter_tree_focus = lambda: app.tree_has_focus
        self.filter_expanded_attrs = lambda: app.flag_expanded_attrs
        self.filter_not_expanded_attrs = lambda: not app.flag_expanded_attrs
        self.filter_dataset_mode = lambda: app.flag_dataset_mode
        self.filter_dataset_values_shown = (
            lambda: app.flag_dataset_mode and app.dataset_values_has_content
        )
        self.filter_search_mode = lambda: app.flag_search_mode

    def bind_function(self, key, function, filter_lambda):
        """Bind a function to a key with a filter condition.

        Args:
            key (str): The key to bind the function to.
            function (callable): The function to bind.
            filter_lambda (callable): A lambda function that returns a boolean
                indicating whether the binding should be active.
        """
        self.app.kb.add(key, filter=Condition(filter_lambda))(function)

    def _init_normal_mode_bindings(self):
        """Initialise normal mode keybindings."""
        # Bind mode leader keys
        self.bind_function(
            self.goto_leader_key,
            goto_leader_mode,
            self.filter_normal_mode,
        )
        self.bind_function(
            self.dataset_leader_key,
            dataset_leader_mode,
            self.filter_normal_mode,
        )
        self.bind_function(
            self.window_leader_key,
            window_leader_mode,
            self.filter_normal_mode,
        )
        self.bind_function(
            self.hist_leader_key,
            hist_leader_mode,
            self.filter_normal_mode,
        )
        self.bind_function(
            self.plot_leader_key,
            plotting_leader_mode,
            self.filter_normal_mode,
        )

        # Bind the search leader key but only if tree has focus
        self.bind_function(
            self.search_leader_key,
            search_leader_mode,
            self.filter_normal_mode,
        )

        # Bind the tree restoration key
        self.bind_function(
            self.restore_key,
            restore_tree_to_initial,
            self.filter_normal_mode,
        )

        # Bind the copy key
        self.bind_function(
            self.copy_key_binding,
            copy_key,
            self.filter_normal_mode,
        )

        # Binding the quitting machinery
        self.bind_function(
            self.quit_key,
            exit_app,
            self.filter_normal_mode,
        )

        # Bind exiting a leader mode
        self.bind_function(
            self.quit_key,
            exit_leader_mode,
            self.filter_not_normal_mode,
        )

    def _init_motion_bindings(self):
        """Initialise motion keybindings."""
        # Bind vim motions if vim mode is enabled (these work everywhere
        # regardless of focus but need to ignore when typing is done in search)
        if self.vim_mode_enabled:
            self.bind_function(
                self.vim_move_left_key,
                move_left,
                self.filter_not_searching,
            )
            self.bind_function(
                self.vim_move_down_key,
                move_down,
                self.filter_not_searching,
            )
            self.bind_function(
                self.vim_move_up_key,
                move_up,
                self.filter_not_searching,
            )
            self.bind_function(
                self.vim_move_right_key,
                move_right,
                self.filter_not_searching,
            )

        # The user can also add their own movement keys via the config but
        # we only need to bind these if they are not up/down/left/right or
        # the vim keys (assuming vim mode is enabled)
        if self.move_up_key != "up" and not (
            self.vim_mode_enabled and self.move_up_key == self.vim_move_up_key
        ):
            self.bind_function(
                self.move_up_key,
                move_up,
                self.filter_not_searching,
            )
        if self.move_down_key != "down" and not (
            self.vim_mode_enabled
            and self.move_down_key == self.vim_move_down_key
        ):
            self.bind_function(
                self.move_down_key,
                move_down,
                self.filter_not_searching,
            )
        if self.move_left_key != "left" and not (
            self.vim_mode_enabled
            and self.move_left_key == self.vim_move_left_key
        ):
            self.bind_function(
                self.move_left_key,
                move_left,
                self.filter_not_searching,
            )
        if self.move_right_key != "right" and not (
            self.vim_mode_enabled
            and self.move_right_key == self.vim_move_right_key
        ):
            self.bind_function(
                self.move_right_key,
                move_right,
                self.filter_not_searching,
            )

    def _init_tree_bindings(self):
        """Initialise tree navigation keybindings."""
        # Bind expand/collapse attributes key
        self.bind_function(
            self.expand_collapse_key,
            expand_collapse_node,
            self.filter_tree_focus,
        )

        # Bind jump keys
        self.bind_function(
            self.jump_up_key,
            move_up_ten,
            self.filter_tree_focus,
        )
        self.bind_function(
            self.jump_down_key,
            move_down_ten,
            self.filter_tree_focus,
        )

        # Binding the expand/collapse attributes keys
        self.bind_function(
            self.toggle_attrs_key,
            expand_attributes,
            self.filter_not_expanded_attrs,
        )
        self.bind_function(
            self.toggle_attrs_key,
            collapse_attributes,
            self.filter_expanded_attrs,
        )

    def _init_dataset_bindings(self):
        """Initialize dataset mode keybindings."""
        # Bind dataset mode keys
        self.bind_function(
            self.view_values_key,
            show_values,
            self.filter_dataset_mode,
        )
        self.bind_function(
            self.view_range_key,
            show_values_in_range,
            self.filter_dataset_mode,
        )
        self.bind_function(
            self.close_values_key,
            close_values,
            self.filter_dataset_values_shown,
        )
        self.bind_function(
            self.min_max_key,
            minimum_maximum,
            self.filter_dataset_mode,
        )
        self.bind_function(
            self.mean_key,
            mean,
            self.filter_dataset_mode,
        )
        self.bind_function(
            self.std_key,
            std,
            self.filter_dataset_mode,
        )

    def _init_search_bindings(self):
        """Initialize search mode keybindings."""
        # Bind search mode keys
        self.bind_function(
            self.accept_search_key,
            accept_search_results,
            self.filter_search_mode,
        )
        self.bind_function(
            self.cancel_search_key,
            exit_search_mode,
            self.filter_search_mode,
        )
        self.bind_function(
            self.exit_search_key,
            exit_search_mode,
            self.filter_search_mode,
        )

    def _init_bindings(self):
        """Initialize all keybindings."""
        self._init_normal_mode_bindings()
        self._init_motion_bindings()
        self._init_tree_bindings()
        self._init_dataset_bindings()
        self._init_search_bindings()

    def get_current_hotkeys(self):
        """Get the current hotkeys based on application state."""
        # Initialise a list in which we will store the hotkey labels to show
        # Note that order matters here as it defines the order in which the
        # hotkeys are shown in the UI
        hotkeys = []

        # Opening and closing nodes if tree has focus
        if self.filter_tree_focus():
            hotkeys.append(self.expand_collapse_label)

        # Show mode leaders in normal mode
        if self.filter_normal_mode():
            hotkeys.append(self.goto_mode_label)
            hotkeys.append(self.dataset_mode_label)
            hotkeys.append(self.window_mode_label)
            hotkeys.append(self.hist_mode_label)
            hotkeys.append(self.plotting_mode_label)

        # If tree has focus, show jump 10 keys
        if self.filter_tree_focus():
            hotkeys.append(self.move_ten_label)

        # Show the search key if in normal mode
        if self.filter_normal_mode():
            hotkeys.append(self.search_label)

        # Show the tree restoration key if in normal mode
        if self.filter_normal_mode():
            hotkeys.append(self.restore_tree_label)

        # Show the copy key if in normal mode
        if self.filter_normal_mode():
            hotkeys.append(self.copy_key_label)

        # Show the expand/shrink attributes key if in normal mode and tree
        # has focus
        if self.filter_normal_mode():
            if self.filter_not_expanded_attrs():
                hotkeys.append(self.expand_attrs_label)
            else:
                hotkeys.append(self.shrink_attrs_label)

        # Show the dataset mode keys if in dataset mode
        if self.filter_dataset_mode():
            hotkeys.append(self.view_values_label)
            hotkeys.append(self.view_range_label)
            if self.filter_dataset_values_shown():
                hotkeys.append(self.close_values_label)
            hotkeys.append(self.min_max_label)
            hotkeys.append(self.mean_label)
            hotkeys.append(self.std_label)

        # Show the search mode keys if in search mode
        if self.filter_search_mode():
            hotkeys.append(self.accept_search_label)

        # Show the quit key in normal mode
        if self.filter_normal_mode():
            hotkeys.append(self.exit_label)

        # We have special text for cancelling/exiting search mode
        elif self.filter_search_mode():
            hotkeys.append(self.cancel_search_label)

        # If not in normal mode, show the exit leader mode key
        else:
            hotkeys.append(self.exit_mode_label)

    def get_mode_title(self):
        """Get the current mode title based on application state."""
        # Get the application instance for clarity
        app = self.app

        # Determine the current mode and return the appropriate title
        if app.flag_normal_mode:
            return "Normal Mode"
        elif app.flag_jump_mode:
            return "Goto Mode"
        elif app.flag_dataset_mode:
            return "Dataset Mode"
        elif app.flag_window_mode:
            return "Window Mode"
        elif app.flag_plotting_mode:
            return "Plotting Mode"
        elif app.flag_hist_mode:
            return "Histogram Mode"
        elif app.flag_search_mode:
            return "Search Mode"
        else:
            return "Unknown Mode"
