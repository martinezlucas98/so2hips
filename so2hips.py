import os
import subprocess

def is_program(name):
        """Ve si el archivo `name` existe"""
        from shutil import which
        print (which(name)) #is not None

#print(is_program("wget"))

def check_files_is_program(list):
        #nothing yet
        print('')

def check_mailq(command):
        p = subprocess.Popen("mailq", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        print(output)

if __name__=='__main__':
        #ciclo main
        check_mailq("mailq")
        is_program("wget")
        is_program("asdfgh")
