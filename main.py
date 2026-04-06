import sys
import os
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame
from prompt_toolkit.completion import Completer, Completion

keywords = [
    "abstract","assert","boolean","break","byte","case","catch","char","class","const",
    "continue","default","do","double","else","enum","extends","final","finally","float",
    "for","goto","if","implements","import","instanceof","int","interface","long","native",
    "new","package","private","protected","public","return","short","static","strictfp",
    "super","switch","synchronized","this","throw","throws","transient","try","void",
    "volatile","while","yield","record","sealed","non-sealed","var","module","open","opens",
    "requires","exports","provides","with","uses","permits"
]

symbols = {
    '>':'#ffffff','<':'#00ffff','=':'#ffcc00','+':'#ff0000','-':'#00ffcc',
    '*':'#ff00ff','/':'#00ffff',';':'#ffaa00','{':'#00aaff','}':'#00aaff',
    '(':'#00ffaa',')':'#00ffaa', '.':'#ffff00'
}

style = Style.from_dict({
    'keyword':'bold #ff79c6',
    'number':'bold #bd93f9',
    'text':'#f1fa8c',
    'line-number':'bg:#282a36 #6272a4',
    'bottom':'bg:#282a36 #f8f8f2',
    'border':'bg:#282a36 fg:#50fa7b',
    'frame.border':'fg:#0000ff bold',
    'cursor-line':'bg:#44475a',
    **{f"symbol_{ord(k)}": v for k,v in symbols.items()}
})

class JavaLexer(Lexer):
    def lex_document(self, document):
        def get_line(lineno):
            line = document.lines[lineno]
            tokens = []
            word = ""
            for ch in line:
                if ch == ' ':
                    if word:
                        tokens.extend(self.process_word(word))
                        word = ""
                    tokens.append(('class:text',' '))
                elif ch in symbols:
                    if word:
                        tokens.extend(self.process_word(word))
                        word = ""
                    tokens.append((f'class:symbol_{ord(ch)}',ch))
                else:
                    word += ch
            if word:
                tokens.extend(self.process_word(word))
            return tokens
        return get_line

    def process_word(self, word):
        if word in keywords:
            return [('class:keyword',word)]
        elif word.isdigit():
            return [('class:number',word)]
        else:
            return [('class:text',word)]

class JavaCompleter(Completer):
    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for kw in keywords:
            if kw.startswith(word):
                yield Completion(kw, start_position=-len(word))

def editor(filename):
    if not filename.endswith(".java"):
        print("Error: Filename must end with .java")
        sys.exit(1)

    if not os.path.exists(filename):
        open(filename,'w').close()

    with open(filename,'r') as f:
        text = f.read()

    buffer = Buffer(completer=JavaCompleter(), complete_while_typing=True)
    buffer.text = text

    bindings = KeyBindings()
    
    @bindings.add('c-s')
    def save(event):
        with open(filename,'w') as f:
            f.write(buffer.text)

    @bindings.add('c-q')
    def exit_app(event):
        event.app.exit()

    @bindings.add('c-z')
    def undo(event):
        buffer.undo()

    @bindings.add('c-y')
    def redo(event):
        buffer.redo()

    @bindings.add('c-f')
    def search(event):
        from prompt_toolkit.shortcuts import prompt
        term = prompt("Search: ")
        cursor = buffer.text.find(term)
        if cursor != -1:
            buffer.cursor_position = cursor

    # Automatic indentation
    @bindings.add('enter')
    def smart_enter(event):
        b = event.app.current_buffer
        current_line = b.document.current_line_before_cursor
        indent = ""
        for ch in current_line:
            if ch in [' ', '\t']:
                indent += ch
            else:
                break
        if current_line.strip().endswith("{"):
            indent += "    "  # 4 spaces extra for blocks
        b.insert_text('\n' + indent)

    def get_line_numbers():
        result = []
        for i, _ in enumerate(buffer.document.lines):
            result.append(('class:line-number', f'{i+1:3} '))
            result.append(('', '\n'))
        return result

    editor_window = Frame(
        VSplit([
            Window(width=4, content=FormattedTextControl(get_line_numbers)),
            Window(content=BufferControl(buffer=buffer, lexer=JavaLexer(), focus_on_click=True))
        ]),
        title='Write Java Code',
        style='class:border'
    )

    bottom_bar = Window(
        height=1,
        content=FormattedTextControl(
            text='Ctrl-S: Save | Ctrl-Q: Exit | Ctrl-Z: Undo | Ctrl-Y: Redo | Ctrl-F: Search | Enter: Auto-indent | Mouse Supported'
        ),
        style='class:bottom'
    )

    root_container = HSplit([
        editor_window,
        bottom_bar
    ])

    app = Application(
        layout=Layout(root_container),
        key_bindings=bindings,
        full_screen=True,
        mouse_support=True,
        style=style
    )

    app.run()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please enter a filename (must end with .java)")
        sys.exit(1)
    editor(sys.argv[1])
