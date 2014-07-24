#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
#
# This is test for skynet.config 
 
import unittest,os
import skynet

class Test_Config(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.curr_dir=( os.path.dirname ( os.path.join ( os.path.realpath(__file__) ) ) )
        self.default_target_conf_list=skynet.Config().target_configs()
        
    def test_default_json(self):
        self.assertGreater(len(self.default_target_conf_list), 0, "parser /skynet/skynet_config.json incorrectly")
       
    def test_run_Config_twice(self):
        obj=skynet.Config()
        self.return_list=obj.target_configs()
        self.assertGreater(len(self.return_list), 0, "parser /skynet/skynet_config.json incorrectly")
        self.return_list=obj.target_configs()
        self.assertGreater(len(self.return_list), 0, "parser /skynet/skynet_config.json incorrectly")
        
    def test_nonexist_json(self):
        self.assertRaises(FileNotFoundError,\
            lambda: skynet.Config("/a/b/c.json").target_configs())
        
    def test_invalid_json_No_IP_Element(self):
        self.invlid_IP_list=skynet.Config(os.path.join(self.curr_dir,"invalid_no_IP.json")).target_configs()
        self.assertEqual(len(self.invlid_IP_list), 0)

    def test_invalid_json_No_ID_Element(self):
        self.invlid_IP_list=skynet.Config(os.path.join(self.curr_dir,"invalid_no_ID.json")).target_configs()
        self.assertEqual(len(self.invlid_IP_list), 1)
                
    def test_invalid_json_format(self):
        self.assertRaises(skynet.config.config.InvalidConfigException,\
                          lambda: skynet.Config(os.path.join(self.curr_dir,"invalid_format_error.json")).target_configs())
        
    def test_invalid_IP(self):
        self.invlid_IP_list=skynet.Config(os.path.join(self.curr_dir,"invalid_IP.json")).target_configs()
        self.assertEqual(len(self.invlid_IP_list), 1, "stored invalid IP")
        
    def test_invalid_ID(self):
        self.invlid_ID_list=skynet.Config(os.path.join(self.curr_dir,"invalid_ID.json")).target_configs()
        self.assertEqual(len(self.invlid_ID_list), 1, "stored invalid IP")
        
if __name__ == '__main__':
    unittest.main()
    