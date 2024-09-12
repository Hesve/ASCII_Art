# -*- coding: utf-8 -*-
"""

@author: Henry Svedberg
"""

import unittest
from PIL import Image, ImageEnhance
import numpy as np
import os
import json
from ASCII_Art_Studio import ASCII_art, SessionManager, ASCII_UserInterface
from unittest.mock import patch

#Note: this requires that the user has an image with the name grayscale and slalom
#in the same working directory

class TestAscii_art(unittest.TestCase):
 
    def test_load_image(self):
        '''assert that an instance is created with correct attributes so that the
        #image loading function is working as expected.'''
        img= "grayscale.jpg"
        ascii_object = ASCII_art(img)
        self.assertEqual(ascii_object._file_name, "grayscale.jpg", \
                          "filename should be grayscale.jpg")
        self.assertIsNotNone(ascii_object._image,
                             "No image object exists") 
        
        self.assertEqual(ascii_object._height, ascii_object._image.height, 
                         "Object height and image height are not the same")
        self.assertEqual(ascii_object._width, ascii_object._image.width,
                         "object width and image width are not the same")
        self.assertAlmostEqual(ascii_object._aspect_ratio, #almostequal due to rounding
                               ascii_object._height / ascii_object._width,
                         "Object and image aspect ratios are not the same")
        self.assertEqual(ascii_object._contrast, 1, "object contrast is not 1")
        self.assertEqual(ascii_object._brightness, 1, "object brightness is not 1")    

    def test_resize_custom_arguments(self):
        '''asserting resize method works with custom arguments'''
        img= "grayscale.jpg"
        ascii_object = ASCII_art(img)
        ascii_object.resize(new_width = 50, new_height = 50)
        self.assertEqual(ascii_object._target_height, 50, 
                         "target_height should be 50")
        self.assertEqual(ascii_object._target_width, 50, 
                         "target_width should be 50")
            
    def test_resize_default_arguments(self):
        '''asserting resize works with defaults'''
        img= "grayscale.jpg"
        ascii_object = ASCII_art(img)
        expected_width = 50
        expected_height = int(round((ascii_object._aspect_ratio * 
                                    expected_width/ 2),0))
        ascii_object.resize()
        self.assertEqual(ascii_object._target_height, expected_height, 
                         f"target_height should be {expected_height}")
        
        self.assertEqual(ascii_object._target_width, expected_width,
                         f"target_width should be {expected_width}")
        
    def test_enhance(self):
        '''asserting the enhance_method works'''
        img= "grayscale.jpg"
        ascii_object = ASCII_art(img)
        
        ascii_object.image_enhance("brightness", 1.3)
        ascii_object.image_enhance("contrast", 0.2)
        
        self.assertEqual(ascii_object._brightness, 1.3, "brightness is not set to 1.3")
        self.assertEqual(ascii_object._contrast, 0.2, "contrast is not set to 0.2")
        
        #testing nameerror:
        with self.assertRaises(NameError):
            ascii_object.image_enhance("brightne", 0.2)
            
    def test_normalize(self):
        ''' testing normalize so that it normalizes gray scale values into to fit into
        different ranges of values'''
        
        img= "grayscale.jpg"
        ascii_object = ASCII_art(img)
        
        #generating random integers from an discrete uniform [0,255] distribution
        #to represent some random pixels converted to grayscale
        number_observations = 1337
        simulated_data = np.random.randint(0,256, number_observations)
        
        #choosing a random number to represent the length of the gscale attribute
        gscale_len = np.random.randint(1,101)
             
        output = ascii_object._ASCII_art__normalize(x = simulated_data,
                                                    max_support = gscale_len)

        #checking that all values are within defined range:
        within_range = np.logical_and(0 <= output, output <= gscale_len)
        self.assertTrue(np.all(within_range), 
        f"the simulated values were expected to only be withing the range "
        f"0:{gscale_len} but were found outside that range")
        
    @patch("builtins.print")  # Patch the print function
    def test_render_print(self, mock_print):
        '''testing that the render function can print to console. However, this 
        does not check the actual characters printed in some meaningsful way'''
        img = "grayscale.jpg"
        ascii_object = ASCII_art(img)
        ascii_object.resize()
        
        # Call the render function
        ascii_object.render()
        
        # Check if the print function was called
        self.assertTrue(mock_print.called, "print function was not called")
        
        # Check if the printed content is not empty
        printed_content = "\n".join(call_args[0][0] for call_args in mock_print.call_args_list)
        self.assertTrue(printed_content.strip(), "printed content is empty")
        
#note: i asked chatgpt for help on this on how to assert that print has been used


class TestSessionManager(unittest.TestCase):
#note: the first two methods here are just to help structure the code and
#as to not repeat the same code so much

   def setUp(self):
       #this gets called every time before each test to start a new session
       self.session_manager = SessionManager()

   def _load_images(self):
       self.session_manager._load_image("grayscale.jpg")
       self.session_manager._load_image("slalom.jpg", alias="skidor")

    

       
   def test_load_image(self):
       #checking that it can load two images with and without alias, thatthe
       #second image will be set to current and that target width = 50
       self._load_images()
       grayscale_obj = self.session_manager.members[0]
       slalom_obj = self.session_manager.members[1]
       
        # Check the loaded images 
       self.assertIsNotNone(grayscale_obj, "Could not load the image grayscale")
       self.assertIsNotNone(slalom_obj, "Could not load the image slalom")
       
       self.assertTrue(hasattr(slalom_obj, "alias"), 
                       "could not find any alias for the slalom image")
       self.assertEqual(slalom_obj.alias, "skidor", 
                        "The alias for slalom should be 'skidor'")
       self.assertEqual(self.session_manager._current, slalom_obj,
                     "'skidor' should be the current image")
       self.assertEqual(grayscale_obj._target_width, 50, 
                        "Target_width should be set to 50")
       
    
   def test_change_attribute(self):
       '''testing that the attributes can be sucesfully changed from within a 
       session given that the user has provided either the filename or alias'''
    #testing so that it can find an image provided user input and 
    #can change it attributes and then save/load the session. 
       self._load_images()
       grayscale_obj = self.session_manager.members[0]
       slalom_obj = self.session_manager.members[1]
            
        
       self.session_manager._set_img_dim("grayscale.jpg", "height", 70)
       self.session_manager._set_img_enhance("skidor", "contrast", 1.3)
            
       self.assertEqual(grayscale_obj._target_height, 70,
                        "Target height should be set to 70")
       self.assertEqual(slalom_obj._contrast, 1.3,
                        "contrast should be set to 13")
       #saving
       
   def compare_attributes(self, obj1, obj2):
       '''Helper function to compare attributes for two sessions by checking that
       the attributes are the same'''
       
       attributes_to_compare = [ "_target_height",
                                "target_width", "_file_name",
                                "_aspect_ratio",  "_contrast", "_brightness", 
                                "gscale", "alias,"]
       for attribute in attributes_to_compare:
           if hasattr(obj1, attribute) and hasattr(obj2, attribute):
               #using hasattr since alias may not exist
               value1 = getattr(obj1, attribute)
               value2 = getattr(obj2, attribute)
               self.assertEqual(value1, value2, 
                 f"Attribute {attribute} is different: {value1} != {value2}")
           elif hasattr(obj1,attribute) and not hasattr(obj2, attribute):
               self.fail(f"Attribute {attribute} does not exist in obj2")
    

   def save_and_load(self):
       '''helper function to load image, change attribute,  save and load 
       session'''
       self._load_images()
       self.session_manager._set_img_dim("grayscale.jpg", "height", 70)
       self.session_manager._set_img_enhance("skidor", "contrast", 1.3)
       self.session_manager._set_img_enhance("skidor", "brightness", 0.2)
       # Save session and load session
       self.session_manager._save_session("test_session.json")
       self.new_session_manager = SessionManager()
       self.new_session_manager._load_session("test_session.json")

   def test_save_and_load_session(self):
       '''testing save and load by  checking if its the same after'''
       self.save_and_load()
       
       grayscale_obj = self.session_manager.members[0]
       slalom_obj = self.session_manager.members[1]
       new_grayscale_obj = self.new_session_manager.members[0]
       new_slalom_obj = self.new_session_manager.members[1]
       
       session1_members = len(self.session_manager.members)
       session2_members = len(self.new_session_manager.members)

       self.assertEqual(session1_members, session2_members,
                   "the number of members in the two sessions are not the same")

       
       self.compare_attributes(grayscale_obj, new_grayscale_obj)
       self.compare_attributes(slalom_obj, new_slalom_obj)
       #chcking current attribute:
       self.assertEqual(self.session_manager._current.alias, 
                        self.new_session_manager._current.alias,
                     "The current image for the two sessions are not the same")
       
   def test_current_change(self):
       '''test that the current image changes everytime an user uses a method 
       to adjust the image attributes'''
       self._load_images()
       grayscale_obj = self.session_manager.members[0]
       slalom_obj = self.session_manager.members[1]
       self.assertEqual(self.session_manager._current, slalom_obj,
                     "'skidor' should be the current image")
       
       self.session_manager._set_img_dim("grayscale.jpg", "width", 13)
       self.assertEqual(self.session_manager._current, grayscale_obj,
                     "changing width did not change the current image")
       self.session_manager._set_img_dim("slalom.jpg", "height", 37)
       self.assertEqual(self.session_manager._current, slalom_obj,
                        "Changing height did not change the current image ")
       self.session_manager._set_img_enhance("skidor", "contrast", 0.4)
       self.assertEqual(self.session_manager._current, slalom_obj, 
                        "Changing contrast did not change the current image")
       self.session_manager._set_img_enhance("grayscale.jpg", "brightness", 2.0)
       self.assertEqual(self.session_manager._current, grayscale_obj,
                        "Changing brightness did not change the current image")
      
       
       
       


if __name__ == '__main__':
    unittest.main()       

