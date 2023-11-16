from textual.app import App, ComposeResult
from textual.widgets import Static, Label, ListItem, ListView, TextArea, Input
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.binding import Binding
from board import Board


class TaskList(ListView):
    """
        Inherited widget from Listview to use as the kanban board columns
    """
    # Keybinds
    BINDINGS = [
        Binding("k", "cursor_up", "Cursor Up", show=False, priority=True),
        Binding("j", "cursor_down", "Cursor Down", show=False, priority=True),
    ]

class EditScreen(Screen):
    """
        This is a screen used to edit the name of a task
    """
    CSS="""
        Label{
            width:50%;
        }
        Input{
            width:50%;
        }
    """
    BINDINGS = [
        Binding('enter', 'save', 'Save Changes', priority=True)
    ]
    def __init__(self,text):
        """
        Initialize the screen
        """
        super().__init__()
        self.text = text

    def compose(self):
        """
        Compose the widgets on the screen, this screen doesn't need dynamic layout changes
        """
        yield Label('Task Name:')
        yield Input(value=self.text)


    def action_save(self):
        query = self.query(selector=Input)
        self.dismiss(query.nodes[0].value)


class KanbanForm(App):
    CSS_PATH = 'layout.tcss'
    BINDINGS = [
        Binding("l", "fnext", "Focus Next", show=False, ),
        Binding("a", "new_task", "Add New Task", show=False, ),
        Binding("h", "fprev", "Focus Prev", show=False, ),
        Binding("L", "move_up", "Focus Next", show=False),
        Binding("H", "move_down", "Focus Prev", show=False),
        Binding("e", "edit_task", "Edit Task", show=False,),
        Binding('q', 'exit', "Exit")
        ]

    def compose(self):
        """
        Initialization function for form
        """
        # Initialize our board class
        self.board = Board(file = '.board.md')
        self.cols = list()

        self.col_widgets = list()
        
         
        with Horizontal():
            for i,col in enumerate(self.board.get_columns()):
                if i < len(self.board.get_columns())-1:
                    col_class = 'column'
                else:
                    col_class = 'last-column'
                with Vertical(classes=col_class):
                    yield Static(col, classes='header')
                    yield TaskList(
                        *[ListItem(Label(task)) for task in self.board.get_tasks()[i]])

        # Now make all TaskLists except the first have no highlights
    def action_fnext(self):
        """ Focus next column"""
        self.children[0].focus_next()

    def action_move_up(self):
        icol, itask = self.get_col_task()
        text = self.board.get_task(icol, itask)
        moved = self.board.move_task(icol, itask, 1)
        if moved:
            query = self.query(selector=TaskList)
            self.focused.highlighted_child.remove()
            query.nodes[icol+1].append(ListItem(Label(text)))
            self.focused.action_cursor_down()
            self.action_fnext()
            self.focused.action_cursor_down()

        
    def action_fprev(self):
        """ Focus previous column """
        self.children[0].focus_previous()

    def action_move_down(self):
        icol, itask = self.get_col_task()
        text = self.board.get_task(icol, itask)
        moved = self.board.move_task(icol, itask, -1)
        if moved:
            query = self.query(selector=TaskList)
            self.focused.highlighted_child.remove()
            query.nodes[icol-1].append(ListItem(Label(text)))
            self.focused.action_cursor_down()
            self.action_fprev()
            self.focused.action_cursor_down()

    def action_edit_task(self):
        icol, itask = self.get_col_task()
        task = self.board.get_task(icol, itask)
        self.push_screen(EditScreen(task), self.update_task)
    
    def action_new_task(self):
        self.push_screen(EditScreen(""), self.new_task)

    def action_exit(self):
        """ Exit the application """
        self.board.write_md()
        self.exit()

    def get_col_task(self):
        """ 
        This function gets the relevant column and task from the Board object for the current
        selected item in the tui.
        """
        focused_col = self.focused
        query = self.query(selector=TaskList)

        # First get the column index
        for i, child in enumerate(query.nodes):
            if focused_col == child:
                col_index = i

        # Now get the indext of the item in the list
        to_move = focused_col.highlighted_child
        for i, child in enumerate(focused_col.children):
            if to_move == child: 
                task_index = i

        return col_index, task_index
    
    def update_task(self, text):
        """ This function gets the text inputted in the edit screen and updates the underlying 
            task and the board class
            
        """
        icol, itask = self.get_col_task()
        self.focused.highlighted_child.children[0].update(text)
        self.board.update_task(icol, itask, text)

    def new_task(self, text):
        """ This function adds a new task to our board
        """
        icol,_ = self.get_col_task()
        self.focused.mount(ListItem(Label(text)))
        self.board.add_task(icol, text)
        self.focused.highlighted_child
    
#    def on_key(self):
#        with open('log','a') as f:
#            f.write("{}".format(self.children[0].focus_next))

if __name__ == "__main__":
    kb = KanbanForm()
    kb.run()


