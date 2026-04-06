from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import Layout, HSplit, VSplit
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.containers import Window, Frame, ConditionalContainer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.filters import Condition
import os

# -----------------------------
# Define Java Keywords & Symbols
# -----------------------------
java_keywords = [
    "abstract","assert","boolean","break","byte","case","catch","char","class",
    "const","continue","default","do","double","else","enum","extends","final",
    "finally","float","for","goto","if","implements","import","instanceof","int",
    "interface","long","native","new","package","private","protected","public",
    "return","short","static","strictfp","super","switch","synchronized","this",
    "throw","throws","transient","try","void","volatile","while","true","false","null"
]

symbols = {
    '>': '#ffffff','<': '#00ffff','=': '#ffcc00','+': '#ff0000','-': '#00ffcc',
    '*': '#ff00ff','/': '#00ffff', '.':'#ffff00',';':'#ffaa00','{':'#00ffcc',
    '}':'#00ffcc','(':'#ff00ff',')':'#ff00ff',',':'#ff00ff'
}

# -----------------------------
# Style
# -----------------------------
style = Style.from_dict({
    'keyword': '#ff0066 bold',
    'number': '#ffaa00',
    'text': '#00ff00',
    'symbol': '#00ffff bold',
    'status': 'bg:#444444 #ffffff',
    'frame.border': 'fg:#00ff00',
    'frame.label': 'fg:#ff0066 bold',
    'background': 'bg:#000000',
    **{f'symbol_{ord(k)}': v for k,v in symbols.items()}
})

# -----------------------------
# Lexer
# -----------------------------
class JavaLexer(Lexer):
    def lex_document(self, document):
        def get_line(lineno):
            line = document.lines[lineno]
            tokens = []
            word = ""
            for ch in line:
                if ch.isspace():
                    if word:
                        tokens.extend(self.process_word(word))
                        word = ""
                    tokens.append(('class:text',' '))
                elif ch in symbols:
                    if word:
                        tokens.extend(self.process_word(word))
                        word = ""
                    tokens.append((f'class:symbol_{ord(ch)}', ch))
                else:
                    word += ch
            if word:
                tokens.extend(self.process_word(word))
            return tokens
        return get_line
    
    def process_word(self, word):
        if word in java_keywords:
            return [('class:keyword', word)]
        elif word.isdigit():
            return [('class:number', word)]
        else:
            return [('class:text', word)]

# -----------------------------
# Bottom status bar (shortcuts)
# -----------------------------
def bottom_bar():
    text = [
        ('class:status', ' Ctrl-S: Save | Ctrl-Q: Quit | Ctrl-Z: Undo | Ctrl-Y: Redo | '),
        ('class:status', ' Vim-style keys active ')
    ]
    return text

# -----------------------------
# Editor Function
# -----------------------------
def editor(filename):
    # Load file
    if os.path.exists(filename):
        with open(filename, "r") as f:
            content = f.read()
    else:
        content = ""
    
    buffer = Buffer()
    buffer.text = content
    
    # Keybindings
    kb = KeyBindings()
    
    @kb.add('c-s')
    def save(event):
        with open(filename, "w") as f:
            f.write(buffer.text)
    
    @kb.add('c-q')
    def exit_(event):
        event.app.exit()
    
    # Undo/Redo
    @kb.add('c-z')
    def undo(event):
        buffer.undo()
    
    @kb.add('c-y')
    def redo(event):
        buffer.redo()
    
    # -----------------------------
    # Vim-style navigation (hjkl)
    # -----------------------------
    @kb.add('h')
    def left(event):
        event.app.current_buffer.cursor_left(count=1)
    
    @kb.add('l')
    def right(event):
        event.app.current_buffer.cursor_right(count=1)
    
    @kb.add('j')
    def down(event):
        event.app.current_buffer.cursor_down(count=1)
    
    @kb.add('k')
    def up(event):
        event.app.current_buffer.cursor_up(count=1)
    
    # -----------------------------
    # Layout
    # -----------------------------
    editor_window = Frame(
        Window(
            BufferControl(buffer=buffer, lexer=JavaLexer(), focus_on_click=True),
            wrap_lines=False
        ),
        title=f" Java Editor - {filename} ",
    )
    
    bottom_window = Window(
        content=FormattedTextControl(bottom_bar),
        height=1,
        style="class:status"
    )
    
    root_container = HSplit([
        editor_window,
        bottom_window
    ])
    
    app = Application(
        layout=Layout(root_container),
        key_bindings=kb,
        mouse_support=True,
        full_screen=True,
        style=style
    )
    
    app.run()

# -----------------------------
# Run Editor
# -----------------------------
if __name__ == "__main__":
    editor("Test.java")
