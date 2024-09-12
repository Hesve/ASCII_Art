'''
@author Henry Svedberg
'''

from PIL import Image, ImageEnhance
import numpy as np
import os
import json


class ASCII_art:
    ''' The class ASCII_art contains various methods to convert an image into ascii
    art. This class is meant to be a stand alone class in the sense that it 
    contains all the necessary methods to handle individual images and 
    render them to ASCII art. But its not intended to handle any user interaction.
   
    It is to some degree an extension of the Image class from the Pillow module
    as it incorporates some of that modules methods to load and adjust the images.
    It also uses some methods from numpy in order to handle arrays
    
    Overall, this class contains methods to load an image, rezise it, change the
    brightness or contrast and then render it to ascii either directly in the
    console or to a new file.
    '''
    
    def _load_image(self, image_path):
        '''Method to load an image from a file on the computer and convert it 
      into grayscale'''
  
        with Image.open(image_path) as img:
            img.load()
            return img.convert(mode="L")

                                                  
    def __init__(self, image_path):
        '''instanciating object from image with attributes corresponding to the
        image properties as well as a gray scale attribute'''
        
        self._image = self._load_image(image_path)
        self._file_name = os.path.basename(image_path)
        self._height = self._image.height
        self._width = self._image.width
        self._aspect_ratio = self._height / self._width
        self._contrast = 1
        self._brightness = 1
        self.gscale= "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
       
      # gray scale level values from: 
      # http://paulbourke.net/dataformats/asciiart/ 
      # 70 levels of gray 
    
    def resize(self, new_height=None, new_width= None):
        ''' Method to rezise an image with the arguments new_height and new_width.
        Both values can be set manually but its not the primary intent as it is 
        meant to handle user input specifying either width or height. 
        
        If only one attribute is set, then the other attribute is calculated as 
        to  maintain the original aspect ratio while also adjusting for  that 
        letters are rougly twice as tall as they are wide. 

        If neither new height or new width are specified , then the default 
        new width is 50 with the height calcualted accordingly. '''
        

        if not new_height and not new_width:
            new_width = 50
            new_height = int(round((self._aspect_ratio * new_width / 2),0))
        elif not new_height:
            new_height = int(round((self._aspect_ratio * new_width / 2),0))
        elif not new_width:
            new_width = int(round((new_height / self._aspect_ratio * 2),0)) 
       
        
        sizes = (new_width, new_height)
        self._image = self._image.resize(sizes)
        self._target_width = new_width
        self._target_height = new_height
        
    def image_enhance(self, attribute, parameter):
        '''
    Method to enhance the brightness or contrast of an image. Valid arguments
    for attribute are "brightness" or "contrast". The parameter is the factor 
    with which to increase or decrease the attribute.
    
    The parameter value is always in relation to the original value of 1.0 and 
    not multiplicative of the current value. For example, if you use this method 
    to change brightness by 1.5, and then again by 1.8, then it is an increase 
    by 80% in relation to the original value.
    
    '''
        #using the methods for PIl image objects
        if attribute == "brightness":
            enhancer = ImageEnhance.Brightness(self._image)
            self._image = enhancer.enhance(parameter / self._brightness)
            #user input for the program is limited to prevent parameter = 0
            self._brightness = parameter
        elif attribute == "contrast":
            enhancer = ImageEnhance.Contrast(self._image)
            self._image = enhancer.enhance(parameter / self._contrast)
            self._contrast = parameter
        else:
            raise NameError("Invalid attribute name. Only 'brightness' and \
                            'contrast' are defined")
    


    #note: the following two methods are meant to be used on a np.array which
    # is defined in the render function further below. 
    
    def __normalize(self, x, min_support=0, max_support=None, 
                    x_min=0, x_max=255):
        '''
        method to normalize the values for the grey scale [0-255] into the 
        range of [0, y]  where y represents length of the gscale attribute
        used. This function is intended to be used on a np.array so that 
        the normalized values of the np.array can be used as indexes for gscale''
        '''
        if not max_support:
            max_support = len(self.gscale)-1 
   #Note. since len(self.gscale)-1  cannot be set as the defualt argument value,
   #I instead opted to set the default to None and then change it like this.
   
        x_norm = (max_support - min_support) * ((x- x_min)/ x_max - x_min) + min_support
        return x_norm
    #formula is from here: 
    #https://stats.stackexchange.com/questions/281162/scale-a-number-between-a-range
        
   
  
    __vectorize_index = np.vectorize(lambda self, i: self.gscale[i])
    #lambda function combined with np.vectorize that takes an np.array as 
    #argument and returns the indexed the elements in gscale based on the value 
   # of each element  in the array. For example, if the value  is 0, then it 
   #returns gscale[0]
    
     
   
    def render(self, out = False):
        '''Method to render an image to ASCII art based on the attributes 
        it currently has. If an argument for out is provided, the rendered art
        will be saved to a new file with the same name as the one provided for 
        the argument. Default is .txt if user does not specify format.
       
        The method works by converting the pixels to an array, normalizing their 
        values to fit the gscale length and then using the values  as indeces 
        for the corresponding element in gscale.
        '''
        greyscale_array= self.__normalize(np.asarray(self._image))
        #creating an np.array and normalizing values
      
        int_array = (np.rint(greyscale_array).astype(int)) 
        # rounding to nearest integer and converting to int
        
        ascii_array = self.__vectorize_index(self, int_array)
        #this is an array where each value is the corresponding gscale letter
        
        strings = ascii_array.view('U' + str(ascii_array.shape[1])).flatten()
        #the strings object is an array with one column and where each row contains
        #all the letters for the corresponding row in ascii_array
        if out:
            if "." not in out:
                out += ".txt"
            with open(out, "w") as out_file:
                print("\n".join(strings), file=out_file)
        else:
            print("\n".join(strings))
                  
    # the piece of code for printing the array is credited to stackoverflow:
    #https://stackoverflow.com/questions/9632995/how-to-easily-print-ascii-art-text
     #(its the last answer)   
 
class SessionManager :
    '''This class is responsible for managing the session given that some user
    input is already provided. The class provides the methods necessary
    to handle multiple ASCII_art objects. It has some session specific methods 
    such as for handling current images or displaying session info, or loading 
    and saving the session.
    
    It also contaings methods to load, save. modify or render images by 
    making use of the ASCII_art class methods while providing some 
    additional utility in order to make it work from user input, such as finding
    the correct image. Hence the purpose of this class is to serve as an 
    interface between the actual user interface, and the individual Ascii_art
    objects.'''
 
    def __init__(self):
        self.members=[]
        self._current = None

        
    def _check_target_size(self, member):
        '''method to check whether or not an object has a target size or not,
        which will be used in the info method'''

        if hasattr(member, "_target_width") and hasattr(member, "_target_height"):
            target_size_info = (
            f"(width, height): "
            f"{member._target_width}, {member._target_height}")
    
        else:
            target_size_info = "no target size set"
        return target_size_info
    

    def _find_img(self, img):
        '''Method ment to be used in whenever an user uses any command with 
        "set img".  Given the arugment "img"  as in the user provided "set img" 
        or "render img"  commands, this method checks the members if their file 
        name or alias is equal to img while also checking for duplicates. 
        If img  is "current", it returns the current image. '''
        
        if img == "current":
            return self._current
        
        matches = 0
        for member in self.members:
            if (hasattr(member, "alias") and member.alias==img) or \
            member._file_name == img:
                matches +=1
                matched_member = member
            
        if matches == 0:
            raise NameError(f"No image was found with the name '{img}' ")
         
        elif matches > 1: 
            raise NameError(f"More Than one image was found with the name"
                            f" or alias '{img}'")
        else:
            return matched_member
            
    def _info(self):
        '''Method to display an overview of the session such as what images are 
        loaded and their attributes, as well as the current image.'''
        print("=== Current session ===\n"
              "Images: \n")
       
        for member in self.members:
            target_size_info = self._check_target_size(member) 
            
            if hasattr(member, "alias"):
                print(member.alias)
            else:
                print("no alias:")
            print(
                f"    filename: {member._file_name}\n"
                f"    size (width, height): ({member._width}, {member._height})\n"
                f"    target size: {target_size_info}\n"
                f"    brightness: {member._brightness}\n"
                f"    contrast: {member._contrast}\n") 
        
        if hasattr(self._current, "alias"):
            print("Current image: ", self._current.alias, "\n")
        else:
            print("Current image:", self._current._file_name, "\n")
            
        #had some help from ChatGpt by asking:
        #"how to print object attributes in a for loop and check if they have 
        #specific attributes in python"
        
    def _load_image(self, file, alias = False, set_width = True):
        '''Method to load an image as an ASCII_art object to the session while
        also automatically sets the new width to 50 as default'''
        try:
            ascii_object = ASCII_art(file)
            if alias:
                ascii_object.alias = alias
            if set_width:
                ascii_object.resize(new_width=50)
            self.members.append(ascii_object)
            self._current = ascii_object
        except (FileNotFoundError, OSError):
            print(f"No image was found with the filename: {file}. "
                  "Please try again")   
    
    def _load_json(self, filename):
        '''method to load and return a json file. This is used for the 
        next method: _load_sesison'''
        if not filename.endswith(".json"):
            filename += ".json"

        with open(filename, "r") as file:
            return(json.load(file))
              
    def _load_session(self, filename):
        '''Method to load a saved session in json format. This does not load
        any pixel data; instead it checks the saved data for the file names and 
        converts them into new ASCII-art objects while also reapplying any 
        saved changes and keeps track of current image'''
    
        session_data = self._load_json(filename)
        self.members = []
        self._current = None

        for member_data in session_data["members"]:
            ascii_object = ASCII_art(member_data["file_name"])
            if member_data["alias"]:
                ascii_object.alias = member_data["alias"]
            if member_data["target_width"] is not None and member_data[
                    "target_height"] is not None:
                ascii_object.resize(
                    new_width=member_data["target_width"],
                    new_height=member_data["target_height"]
                )
            ascii_object.image_enhance("brightness", member_data["brightness"])
            ascii_object.image_enhance("contrast", member_data["contrast"])
            self.members.append(ascii_object)

        if session_data["current"]:
            for member in self.members:
                if member._file_name == session_data["current"]:
                    self._current = member
                    break
            else:
                print("Could not find the specified current image.")  
#Note: this load session and save session method further below
#were done with help from ChatGpt
                
    def _render_img(self, img=False, filename= False):
        '''method to render an image based on the render method from the 
        ASCII_art class. img is the image to be rendered; if not specified
        it will be current image. Filename is the name of the out file to render
        to; if not specified the image will only be printed to console.'''
        
        try:
            if not img:
                img= self._current
            else: img = self._find_img(img)
                
            if filename:
                img.render(out=filename)
            else:
                img.render()
            if self._current != img:
                self._current = img
                
        except NameError as err_message:
            print(err_message) 
            

    def _save_session(self, filename):
        '''method to save the session such as the ascii_art objects and their
        attributes, as well as the session specific current. The data is saved
        as a json file'''
        
        if not filename.endswith(".json"):
            filename += ".json"
            
        session_data = {
        "members": [],
        "current": self._current._file_name if self._current else None,
    }
        for member in self.members:
            member_data = {
                "file_name": member._file_name,
                "alias": member.alias if hasattr(member, "alias") else None,
                "target_width": getattr(member, "_target_width", None),
                "target_height": getattr(member, "_target_height", None),
                "brightness": member._brightness,
                "contrast": member._contrast,
                }
            session_data["members"].append(member_data)
        with open(filename, "w") as f:
            json.dump(session_data, f, indent=4)
                        

       
    def _set_img_dim(self, img, attribute, value):
        '''Method to change the dimension of an image given the alias or filename as 
        the argument "img" based on the resize method for ASCII object.'''
        img_object = self._find_img(img)
        if attribute == "width":
            img_object.resize(new_width=value)
        elif attribute == "height":
            img_object.resize(new_height=value)
        else:
            raise NameError("Invalid attribute. Use 'width' or 'height'.")
            
        if self._current != img_object:
            self._current = img_object

            
    def _set_img_enhance(self, img, attribute, value):
        '''Method to enhance image contrast or brightness based on the 
        enhanct method for ASCII objects. '''
        img_object = self._find_img(img)
        if attribute ==  "brightness":
            img_object.image_enhance("brightness", value)
        elif attribute == "contrast":
            img_object.image_enhance("contrast", value)
        else:
            raise NameError("Invalid attribute. Use 'brightness' or 'contrast'") 
        if  self._current != img_object:
            self._current = img_object
                            


class ASCII_UserInterface:  
    '''This class is handling the user interface. It handles the user input
    by checking whether or not the user is giving a valid command such as 
    "load", "set", "render", "save", "info" or "quit".  Each  command has its 
    own method to handle that specific command to check that
    user input for the rest of the command is valid and then delegated to the 
    corresponding method in the Sessionhandler class. 
    
 '''    
    def __init__(self):
        self.session_manager = SessionManager()
        self._current_image = None
        self.run_program()
             
    #crating dictionary as class attribute  with all valid commands and their
    #corresponding method to handle said command    
    command_handlers = {
        "load": "_handle_load_cmd",
        "help": "user_help",
        "info": "_handle_info",
        "render": "_handle_render_cmd",
        "save": "_handle_save_cmd",
        "set": "_handle_set_cmd",
        "quit": "_handle_quit_cmd"
    }
            
    def run_program(self):
        '''This is the method for the user command prompt interface. When started
        this will always require an user input. if the user command is valid, then 
        it is passed on the the method to handle that specific command'''
        
        print("Welcome to ASCII Art Studio! If you need help to see all valid "
              "commands, type 'help'. To exit, type 'quit' ")
        self._run = True #so loop can break from within quit method
        while self._run:
            user_input = input("AAS: ").lower().split()

            if not user_input:
                print("No command given. Please try again")
                continue
            
            user_cmd = user_input[0]
            self._cmd = user_cmd
            self._input_len = len(user_input)
            
            if self._print_if_no_image(user_cmd): #this will print an error if
                continue  # an user tries some methods before image is loaded

            if user_cmd in self.command_handlers:
                handle_method_name = self.command_handlers[user_cmd]
                handle_method = getattr(self, handle_method_name)

                if user_cmd in ["quit", "info", "help"]: # The handler methods 
                #for these do not take any input argument.
                    handle_method()  # Call method without arguments
                else:
                    handle_method(user_input)  # Call method with arguments
            else:
                print("Invalid command given")
    
                                
    def _print_error(self, err_message="", invalid_args = False):
        '''This method will print a generic error message for each command
         Or a generic error with some extra message as provided by the 
         argument err_msg. If invalid_args is set to true, the err_message
         will be a generic error message for invalid number of arguments. 
        '''
        if invalid_args:
            err_message = "Invalid number of arguments provided"
            
        print(f"Invalid {self._cmd} command. {err_message} "\
              f"If you need additional help. Type 'help'")
            


    def _handle_load_cmd(self, user_input):
        '''method to check that the load command is valid and then delegate it
        to either load_img or load_session'''
        valid_len = [3,5]
        if self._input_len not in valid_len:
            self._print_error(invalid_args = True)
        else:
            load_keyword = user_input[1]
            if load_keyword == "image":
                self._handle_load_img_cmd(user_input)
            elif load_keyword == "session":
                self._handle_load_session(user_input)
            else:
                self._print_error()
            
    def _handle_load_img_cmd(self, user_input):
        
        '''Method to handle the load img command by checking which type of 
        load image command it as and then delegating to session_managers load
        method'''
        img_file = user_input[2]
                         
        if self._input_len == 3:
            self.session_manager._load_image(file=img_file)
            
        elif self._input_len == 5 and user_input[3] =="as":
             alias = user_input[4]
             self.session_manager._load_image(file=img_file, alias = alias)                      
        else: 
            self._print_error()
               
        
                
    def _handle_load_session(self, user_input):
        '''Method to handle the load session command similar to the previous 
        method but for load session'''
        if  self._input_len != 3:
            self._print_error(invalid_args=True)

        else:
            session_file = user_input[2]
            try:
                self.session_manager._load_session(session_file)
            except FileNotFoundError:
                print(f"Session file '{session_file}' not found. Please provide"
                      f" a valid filename.")
        
            except json.JSONDecodeError:
                print(f"Error decoding the session file '{session_file}'. "
                      f"The file might be corrupted.")
            except UnicodeDecodeError:
                print(f"The specified file, {session_file} is a  "
                      f"format not valid with Json")
            except MemoryError:
                print(f"Not enough memory to load the file {session_file}")
            except PermissionError:(f"No permission to read the file "
                                   f"'{session_file}'")
            except Exception as e:
                print(f"An error occurred while loading the session file "
                      f"'{session_file}': {e}")
        
             
    def _handle_info(self):
        '''Method to display an overview of the session such as what images are 
        loaded and their attributes, as well as the current image.'''
        print("=== Current session ===\n"
              "Images: \n")
       
        for member in self.session_manager.members:
            target_size_info = self.session_manager._check_target_size(member) 
            
            if hasattr(member, "alias"):
                print(member.alias)
            else:
                print("no alias:")
            print(
                f"    filename: {member._file_name}\n"
                f"    size (width, height): ({member._width}, {member._height})\n"
                f"    target size: {target_size_info}\n"
                f"    brightness: {member._brightness}\n"
                f"    contrast: {member._contrast}\n") 
        
        if hasattr(self.session_manager._current, "alias"):
            print("Current image: ", self.session_manager._current.alias, "\n")
        else:
            print("Current image:", self.session_manager._current._file_name, "\n")
            
        #had some help from ChatGpt by asking:
        #"how to print object attributes in a for loop and check if they have 
        #specific attributes in python"
    
    def _handle_quit_cmd(self):
        '''method to quit the program'''
        print("Ok bye!")
        self._run = False
        
    def _handle_render_cmd(self, user_input):
       '''Method to handle the render command from the user input. if the 
        command is valid then the user input is passed to to the render_img 
        method. If it is not valid the generic error message is printed'''
        
       if self._input_len == 1: # if the length is 1 then the input is simply "render"
           self.session_manager._current.render()
            
       elif self._input_len == 2:
              self.session_manager._render_img(img = user_input[1])
         
       elif self._input_len ==4  and user_input[2] == "to":
            self.session_manager._render_img(img= user_input[1], 
                                             filename = user_input[3])                     
       else:
           self._print_error()
            
    
    def _handle_save_cmd(self, user_input):
        '''Method to handle the save command'''
        if self._input_len != 4:
            self._print_error(invalid_args = True)
        elif user_input[1] != "session" or user_input[2] != "as":
            self._print_error()
        else:
            try:
                filename = user_input[3]
                self.session_manager._save_session(filename)
            except FileNotFoundError:
                print(f"Error: The file '{filename}' was not found.")
            except OSError as e:
                print(f"Error: An OS-related error occurred while saving the session: {e}")
            except Exception as e:
                print(f"An error occurred while saving the session: {e}")
        

 
        
    def _handle_set_cmd(self, user_input):
        '''method to handle the "set" command to make sure its valid so that 
        the input is only valid attributes or valid numbers. This also limits 
        the number for width or height to between 10-5000. Since it would not 
        be much art with only a few pixels, or would risk crashing with a
        large number. Then it  pass the input along to the methods 
        _set_img_dim or set_img_enhance'''
        
        if self._input_len !=4:
            self._print_error(invalid_args = True)
        elif user_input[2] not in ["width", "height","brightness", "contrast"]:
            self._print_error("Valid attributes are 'width', 'height'"
                              " 'brightness, 'contrast'.")
        else:
            try: # incase the number cant be converted to float or int
                img = user_input[1]
                number = float(user_input[3])
                option = user_input[2]
                
                if number <= 0:
                    self._print_error("Invalid number. Please enter a positive number.")
                    
                elif option in ["width", "height"]:
                    if number < 10:
                        self._print_error("Number too small. Minimum allowed number is 10")
                    elif number > 5000:
                        self._print_error("Number too large. Maximuxm allowed number is 5000")
                    else:
                      self.session_manager._set_img_dim(img, option, int(number))
                    
                elif option in ["brightness", "contrast"]:
                    self.session_manager._set_img_enhance(img, option, number)
                    
            except ValueError:
                print(user_input[3], "is not a valid number")
            except NameError as err_message:
                print(err_message)
                
                        
    def _print_if_no_image(self, user_cmd):
        '''method to print that no image has been loaded if user tries
        to use any method dependent on an image before loading an image'''
        
        if not self.session_manager.members and user_cmd in [
                "render", "set", "info"]:
            print("No images loaded. " 
                  "Use 'load image <filename>' to load an image"
                  " or 'load session <filename>' to load a session")
            return True
        #returning true as a way for other functions to check if it has been
        #printed or not
     
    def user_help(self):
        '''printing the user help from the other methods with help information'''
        print("Valid commands are\n")
        self.load_image_help()
        self.info_help()
        self.render_help()
        self.set_help()
        self.save_load_session_help()
        print("quit: to exit the session")
                
    #the following are just print functions for the different commands to be 
    #use in the user_help. Its mostly a refurbished description from the 
    # instruction file 
    def load_image_help(self):
        print("\nload image 'filename': Load the file in filename and save it "
              "in the session under its filename. The most recently loaded "
              "image is also set as the current image. Note that you must "
              "include the format of the image such as .jpg \n"
              "\nload image filename as alias: Same as the 'load image \"filename\"' "
              "but save the image under the name alias.\n")
        
    def info_help(self):
        print("Info: gives a list of loaded images and their attributes, " 
              "as well as which image is set as the current image.\n")
        
    def render_help(self):
        print("render: Create ASCII art for the current image. Default width for the "
             " rendered image is set to be 50 with the height adjusted as to "
             "correspond to half of the original aspect ratio to adjust for "
             "letters being taller than they are wide\n")
              
        print("render img: Like 'render,' but for the image saved with the "
              "name img. It can be the filename, its alias, or current.\n") 
        
        print("render img to filename: Same as above, but the output is saved "
              "to a file with the name as provided by filename.\n")
        
    def set_help(self):
        print("set img width num: Set the width of the image img "
              "(alias or filename) to num. The image's height is  " 
              "adjusted as explained in the render method." 
              "when rendering the image.\n")
        
        print("set img height num: Same as above, but for the image's height.\n")
        
        print("set img brightness num: Specify how the brightness of the image "
              "img should change compared to the original before rendering. "
              "If num is 1.1, the image will be 10% brighter, and if num is 0.8, " 
              "the image will be 20% darker.\n")
        print("set img contrast num: Same as above, but for contrast.\n")
        
    def save_load_session_help(self):    
        
        print("save session as filename: Save the loaded images with their "
              "filenames, size, brightness, and contrast. The pixel data of the" 
              " images is not saved. The current image, current, is also saved.\n")
        
        print("load session filename: Load the session saved in filename. The "
              "images whose filenames are saved are loaded, and the "
              "saved parameters are set. The current image will be the "
              "one specified in the saved session.\n")
        

        
        
        
        
        

    



def main():
    ASCII_UserInterface()            

if __name__ == "__main__":
    main()


       
          

