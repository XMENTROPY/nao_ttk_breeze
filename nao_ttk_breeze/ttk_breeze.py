
from tkinter import ttk
import tkinter
from util.config import config
from util.functions import get_parent_uuid, get_self_name, snake_to_title
from util.log import log

class Page(ttk.Frame):
    def __init__(self, page_canvas: ttk.Frame, uuid: str):
        # Style
        self.style = 'page.TFrame'

        # Name
        self.uuid = uuid
        name = get_self_name(uuid)

        # Initialize ttk.Frame
        super().__init__(page_canvas, name=name)
        
        # Display self
        self.grid(row=1, column=0, sticky="nsew")
        
        # Tree level
        self.tree_level = 0

        # Current Subpage Title Label
        self.subpage_title = ttk.Label(self)
        self.subpage_title.grid(row=0, column=0, sticky='nw')

        # Navigation for the subpages
        self.page_menu = ttk.Frame(self, name='page_menu', style='page_menu.TFrame', width=200, height=990)
        self.page_menu.grid(row=1, column=0, sticky='nsw')

        # Where Pages get rendered
        self.subpage_canvas = ttk.Frame(self, name='subpage_canvas', width=1720, height=990)
        self.subpage_canvas.grid(row=1, column=1, sticky='nsew')

    def show(self):
        # Dynamically locate the page_title label in the root window
        root = self.winfo_toplevel()
        page_title = root.nametowidget("page_title")  # Use the widget name to locate it
        page_title.configure(text=snake_to_title(self.uuid))
        self.tkraise()

    def add_subpage(self, button_text: str, command=None):
        if not command:
            raise ValueError('All menu items must have a "link" to a page.')
        button = ttk.Button(self.page_menu, text=button_text, command=command)
        button.grid(row=len(self.page_menu.children) + 1, column=0, sticky='ew', pady=2, padx=5)

class SubPage(ttk.Frame):
    def __init__(self, page: Page, uuid: str):
        self.style = 'subpage.TFrame'
        self.uuid = uuid
        name = get_self_name(uuid)
        super().__init__(page.subpage_canvas, name=name)
        self.grid(row=0, column=0, sticky="nsew")
        self.tree_level = 0
        self.parent_page = page

    def show(self):
        # Dynamically locate the subpage_title label in the parent page
        subpage_title = self.parent_page.subpage_title
        subpage_title.configure(text=snake_to_title(self.uuid))
        self.tkraise()

class Container(ttk.Frame):

    def __init__(self, parent:ttk.Frame, uuid:str, style:str=None, grid_coords:dict[str:int]=None, grid_padding:dict[str:int]=None, grid_settings:dict[str]=None, **kwargs):
        
        name = get_self_name(uuid)

        if parent.tree_level % 2 == 0:
            default_grid_coords = {'row': len(parent.children), 'column': 0}
            default_style='dark_container.TFrame'

        elif parent.tree_level % 2 != 0:
            default_grid_coords = {'row': 0, 'column': len(parent.children)}
            default_style='light_container.TFrame'

        if not grid_coords:
            grid_coords = default_grid_coords
        
        if not style:
            style = default_style

        super().__init__(parent, name=name, style=style, **kwargs)
        self.parent_uuid:str = get_parent_uuid(uuid)
        self.tree_level:int = parent.tree_level + 1
        self.grid(**{**grid_coords, **grid_padding, **grid_settings})

class Component(ttk.Frame):
    
    def __init__(self, parent:ttk.Frame, uuid:str, style:str='component.TFrame', grid_coords:dict[str:int]=None, grid_padding:dict[str:int]={}, grid_settings:dict[str]={}):
        name = get_self_name(uuid)
        super().__init__(parent, style=style, name=name)

        # Setting parent uuid
        self.parent_uuid:str = get_parent_uuid(uuid)

        # Initialize Tree Level
        self.tree_level:int = parent.tree_level + 1

        # Auto match background color
        if style == 'component.TFrame':
            parent_background_color = ttk.Style().lookup(parent.style, 'background')
            self.configure(background=parent_background_color)

        # Default Griding Pattern
        if parent.tree_level % 2 == 0:
            default_grid_coords = {'row': len(parent.children), 'column': 0}

        if parent.tree_level % 2 != 0:
            default_grid_coords = {'row': 0, 'column': len(parent.children)}

        if not grid_coords:
            grid_coords = default_grid_coords

        self.grid(**{**grid_coords, **grid_padding, **grid_settings})

class UI:

    def __init__(self):
        """
        Initializes the UI class with a root Tkinter window, a notebook widget,
        and a dictionary to store UI objects by their IDs.
        """
        def create_menu(root):
            menu_bar = tkinter.Menu(root)

            # Add a "File" menu
            file_menu = tkinter.Menu(menu_bar, tearoff=0)
            file_menu.add_command(label="Open", command=lambda: print('hello world'))
            file_menu.add_command(label="Save", command=lambda: print('hello world'))
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=root.quit)

            menu_bar.add_cascade(label="File", menu=file_menu)

            # Add an "Edit" menu
            edit_menu = tkinter.Menu(menu_bar, tearoff=0)
            edit_menu.add_command(label="Undo", command=lambda: print('hello world'))
            edit_menu.add_command(label="Redo", command=lambda: print('hello world'))

            menu_bar.add_cascade(label="Edit", menu=edit_menu)

            root.config(menu=menu_bar)

        self.root = tkinter.Tk()  # Main Tkinter window
        self.root.title(config['title']['value']) # Set window title
        self.root.option_add('*Font', config['app_font']['font'])
        self.root.option_add("*Button.Font", config['app_font']['font'])
        create_menu(self.root) # Windows Menu

        # Dictionary to store UI elements by their IDs
        self.object_directory: dict = {}

        # Global navigation for the application
        self.navbar = ttk.Frame(self.root, name='navbar', style='navbar.TFrame', width=1920, height=40)
        self.navbar.grid(row=0, column=0, sticky='nw')
        self.register_uuid('navbar', self.navbar)

        # Where Pages get rendered
        self.page_title = ttk.Label(self.root, name='page_title')
        self.page_title.grid(row=1, column=0, sticky='nw')

        self.page_canvas = ttk.Frame(self.root, name='page_canvas', width=1920, height=990)
        self.page_canvas.grid(row=2, column=0)

        self.register_uuid('page_canvas', self.page_canvas)

    def mainloop(self):
        """
        Starts the Tkinter event loop, keeping the GUI active.
        """
        self.root.mainloop()

    def register_uuid(self, uuid, object):
        self.check_uuid_exists(uuid)
        self.object_directory[uuid] = object

    def add_page(self, uuid: str):
            # Check that page is parent
            if get_parent_uuid(uuid):
                raise NameError('Page UUID cannot contain a parent.')
            
            # Check if the uuid is reserved
            self.check_uuid_exists(uuid)
            
            # Create page object
            page = Page(self.page_canvas, uuid)

            # Register page object
            self.register_uuid(uuid, page)
            
            # Create nav bar button
            nav_button = ttk.Button(self.navbar, name=get_self_name(uuid), text=snake_to_title(uuid), command=page.show)
            nav_button.grid(row=0, column=len(self.navbar.children) + 1, padx=30, pady=20)

    def add_subpage(self, uuid: str):
            # Get subpage name
            name = get_self_name(uuid)

            # Get the parent page UUID
            parent_page_uuid = self.get_parent_uuid(uuid)

            # Get parent Page Object
            parent_page_object = self.get_object(parent_page_uuid)

            # Check that parent object is a page
            if type(parent_page_object) != Page:
                raise NameError('Subpages can only be added to pages.')

            # Create sub page
            subpage = SubPage(parent_page_object, uuid)

            # Register page object
            self.register_uuid(uuid, subpage)

            # Add a button to navigate to the subpage
            parent_page_object.add_subpage(button_text=snake_to_title(name), command=subpage.show)

    def add_container(self, uuid:str, style:str=None, grid_coords:dict=None, grid_padding:dict=config['default_pad'], grid_settings:dict={}) -> None:

        if not self.object_directory.get(self.get_parent_uuid(uuid)):
            raise LookupError('Parent does not exists')

        # Get the containers parent_uuid
        parent_uuid = get_parent_uuid(uuid)

        # Get the containers parent
        parent:ttk.Widget = self.get_object(parent_uuid)
        
        # Create container
        container = Container(
            parent=parent, 
            uuid=uuid,
            style=style, 
            grid_coords=grid_coords, 
            grid_padding=grid_padding,
            grid_settings=grid_settings)
    
        # Register the container in the directory
        self.register_uuid(uuid, container)

    def add_component(self, 
                      uuid:str, 
                      component_type:Component, 
                      style:str=None, 
                      grid_coords:dict=None,
                      grid_padding:dict=config['default_pad'],
                      grid_settings:dict={},
                      **kwargs
                      ) -> None:

        self.check_uuid_exists(uuid)

        if not component_type:
            raise AttributeError('No component type provided. Component must have a specified type.')
        
        # Get the components parent_uuid
        parent_uuid = get_parent_uuid(uuid)

        # Get parent container
        parent = self.get_object(parent_uuid)
        
        # Create component
        component:Component = component_type(parent, uuid, style, grid_coords=grid_coords, grid_padding=grid_padding, grid_settings=grid_settings, **kwargs)

        # Register component
        self.register_uuid(uuid, component)

    def get_object(self, uuid:str):
        """
        Retrieves a UI object by its ID.

        Args:
            uuid (str): The ID of the UI object to retrieve.

        Returns:
            UiObject: The UI object.

        Raises:
            KeyError: If the specified UUID is not found in the UI objects.
        """

        if uuid not in self.object_directory:
            log.debug(uuid)
            raise KeyError(f"UI object with UUID {uuid} not found.")
        return self.object_directory[uuid]

    def get_state(self, uuid:str) -> dict:
        """
        Retrieves the state of a UI object and its children.
        Omits the topmost layer, directly returning the states of its children.
        """
        # Get the object in question
        ui_object = self.get_object(uuid)
 
        # If the object has children, directly return their states
        if not issubclass(type(ui_object), Component):
            child_states = {}
            for child_uuid in ui_object.children.keys():
                child_states.update(self.get_state(uuid+'.'+child_uuid))
            return child_states  # Exclude the top-level parent

        # For leaf nodes, return their state
        return ui_object.get()

    def get_parent_uuid(self, uuid:str) -> str:

        parent_uuid = get_parent_uuid(uuid)
        
        if '.' not in uuid:
            return None
        
        if parent_uuid not in self.object_directory:
            raise KeyError(f"UI object with UUID '{parent_uuid}' not found.")
        
        return parent_uuid

    def check_uuid_exists(self, uuid):
        """Checks the object directory to see if the specified UUID already exists."""
        if self.object_directory.get(uuid):
            raise NameError(f'UUID already exists - {uuid}')

    def check_uuid_does_not_exist(self, uuid):
        if not self.object_directory.get(uuid):
            raise NameError('UUID does not exist exists')
