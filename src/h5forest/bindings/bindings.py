"""A module containing the keybindings for the basic UI.

This module contains the keybindings for the basic UI. These keybindings are
always active and are not dependent on any leader key. The functions in this
module should not be called directly, but are intended to be used by the main
application.
"""

from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Label

from h5forest.bindings.normal_funcs import (
    copy_key,
    dataset_leader_mode,
    exit_app,
    exit_leader_mode,
    goto_leader_mode,
    hist_leader_mode,
    plotting_leader_mode,
    restore_tree_to_initial,
    search_leader_mode,
    window_leader_mode,
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
        # For clarity extract the app instance
        app = self.app

        # Bind mode leader keys
        self.bind_function(
            self.goto_leader_key,
            goto_leader_mode,
            lambda: app.flag_normal_mode,
        )
        self.bind_function(
            self.dataset_leader_key,
            dataset_leader_mode,
            lambda: app.flag_normal_mode,
        )
        self.bind_function(
            self.window_leader_key,
            window_leader_mode,
            lambda: app.flag_normal_mode,
        )
        self.bind_function(
            self.hist_leader_key,
            hist_leader_mode,
            lambda: app.flag_normal_mode,
        )
        self.bind_function(
            self.plot_leader_key,
            plotting_leader_mode,
            lambda: app.flag_normal_mode,
        )

        # Bind the search leader key but only if tree has focus
        self.bind_function(
            self.search_leader_key,
            search_leader_mode,
            lambda: app.flag_normal_mode
            and app.app.layout.has_focus(app.tree_content.content),
        )

        # Bind the tree restoration key
        self.bind_function(
            self.restore_key,
            restore_tree_to_initial,
            lambda: app.flag_normal_mode,
        )

        # Bind the copy key
        self.bind_function(
            self.copy_key_binding,
            copy_key,
            lambda: app.flag_normal_mode,
        )

        # Binding the quitting machinery
        self.bind_function(
            self.quit_key,
            exit_app,
            lambda: app.flag_normal_mode,
        )

        # Bind exiting a leader mode
        self.bind_function(
            self.quit_key,
            exit_leader_mode,
            lambda: not app.flag_normal_mode,
        )

    def _init_motion_bindings(self):
        """Initialise motion keybindings."""
        # For clarity extract the app instance
        app = self.app

        # Bind vim motions if vim mode is enabled (these work everywhere
        # regardless of focus but need to ignore when typing is done in search)
        if self.vim_mode_enabled:
            self.bind_function(
                self.vim_move_left_key,
                move_left,
                lambda: not app.flag_search_mode,
            )
            self.bind_function(
                self.vim_move_down_key,
                move_down,
                lambda: not app.flag_search_mode,
            )
            self.bind_function(
                self.vim_move_up_key,
                move_up,
                lambda: not app.flag_search_mode,
            )
            self.bind_function(
                self.vim_move_right_key,
                move_right,
                lambda: not app.flag_search_mode,
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
                lambda: not app.flag_search_mode,
            )
        if self.move_down_key != "down" and not (
            self.vim_mode_enabled
            and self.move_down_key == self.vim_move_down_key
        ):
            self.bind_function(
                self.move_down_key,
                move_down,
                lambda: not app.flag_search_mode,
            )
        if self.move_left_key != "left" and not (
            self.vim_mode_enabled
            and self.move_left_key == self.vim_move_left_key
        ):
            self.bind_function(
                self.move_left_key,
                move_left,
                lambda: not app.flag_search_mode,
            )
        if self.move_right_key != "right" and not (
            self.vim_mode_enabled
            and self.move_right_key == self.vim_move_right_key
        ):
            self.bind_function(
                self.move_right_key,
                move_right,
                lambda: not app.flag_search_mode,
            )

    def _init_tree_bindings(self):
        """Initialise tree navigation keybindings."""
        # For clarity extract the app instance
        app = self.app

        # Bind expand/collapse attributes key
        self.bind_function(
            self.expand_collapse_key,
            expand_collapse_node,
            lambda: app.tree_has_focus,
        )

        # Bind jump keys
        self.bind_function(
            self.jump_up_key,
            move_up_ten,
            lambda: app.tree_has_focus,
        )
        self.bind_function(
            self.jump_down_key,
            move_down_ten,
            lambda: app.tree_has_focus,
        )

        # Binding the expand/collapse attributes keys
        self.bind_function(
            self.toggle_attrs_key,
            expand_attributes,
            lambda: app.flag_normal_mode and not app.flag_expanded_attrs,
        )
        self.bind_function(
            self.toggle_attrs_key,
            collapse_attributes,
            lambda: app.flag_normal_mode and app.flag_expanded_attrs,
        )

    def _init_bindings(self):
        """Initialize all keybindings."""
        self._init_normal_mode_bindings()
        self._init_motion_bindings()
        self._init_tree_bindings()

    def _get_normal_tree_labels(self):
        """Get the normal mode labels when the tree has focus."""
        # Show expand/collapse attributes key based on current state
        if self.app.flag_expanded_attrs:
            toggle_attr_label = self.shrink_attrs_label
        else:
            toggle_attr_label = self.expand_attrs_label

        labels = [
            self.expand_collapse_label,
            self.goto_mode_label,
            self.dataset_mode_label,
            self.window_mode_label,
            self.hist_mode_label,
            self.plotting_mode_label,
            self.move_ten_label,
            self.search_label,
            self.copy_key_label,
            toggle_attr_label,
            self.restore_tree_label,
            self.exit_label,
        ]

        return labels

    def _get_normal_labels_no_tree_focus(self):
        """Get the normal mode labels when the tree does not have focus."""
        return [
            self.goto_mode_label,
            self.dataset_mode_label,
            self.window_mode_label,
            self.hist_mode_label,
            self.plotting_mode_label,
            self.search_label,
            self.restore_tree_label,
            self.exit_label,
        ]

    def get_current_hotkeys(self):
        """Get the current hotkeys based on application state."""
        # Get the application instance for clarity
        app = self.app

        # Initialise a list in which we will store the hotkey labels to show
        # Note that order matters here as it defines the order in which the
        # hotkeys are shown in the UI
        hotkeys = []

        # Are we in normal mode with tree focus?
        if app.flag_normal_mode and app.tree_has_focus:
            hotkeys.extend(self._get_normal_tree_labels())

        # Are we in normal mode without tree focus?
        elif app.flag_normal_mode and not app.tree_has_focus:
            hotkeys.extend(self._get_normal_labels_no_tree_focus())
