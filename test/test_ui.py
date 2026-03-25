#!/usr/bin/env python3
from textual.app import App, ComposeResult
from textual.widgets import Label

class TestApp(App):
    def compose(self) -> ComposeResult:
        yield Label('Test UI')

if __name__ == '__main__':
    TestApp().run()