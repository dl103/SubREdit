import sublime, sublime_plugin
import paramiko
import tempfile
import time
import os
import stat

class RemoteOpenCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window.show_input_panel("Remote File Path:", "", self.on_done, None, None)
        pass

    def on_done(self, text):
        self.s = sublime.load_settings("REditPreferences.sublime-settings")
    	host = self.s.get("ssh_host")
    	username = self.s.get("ssh_username")
    	pw = self.s.get("ssh_pass")
        w_dir = self.s.get("workspace_dir")
        self.curr_dir = os.path.join(str(w_dir),str(username)+"@"+str(host))
        client = paramiko.SSHClient()
    	client.load_system_host_keys()
    	client.connect(host, username = username, password = pw)
        self.sftp = client.open_sftp()
        self.read_file(text)
        client.close()
        pass

    def read_file(self, filepath):
        local_path = os.path.normpath(self.curr_dir + filepath)
        print os.path.normpath(os.path.join(local_path, ".."))
        if not os.path.exists(os.path.normpath(os.path.join(local_path, ".."))):
            os.makedirs(os.path.normpath(os.path.join(local_path, "..")))
        try:
            self.sftp.get(filepath, local_path)
        except IOError as e:
            sublime.error_message("Could not find file %s" % filepath)
            print e
            return
        except OSError as e:
           sublime.error_message("Failed to create a temporary directory! Error: %s" % e)
           return
        self.window.open_file(local_path)

class RemoteSaveAsCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        self.view.window().show_input_panel("Remote File Path:", "", self.on_done, None, None)
        pass

    def on_done(self, text):
        s = sublime.load_settings("REditPreferences.sublime-settings")
        host = s.get("ssh_host")
        username = s.get("ssh_username")
        pw = s.get("ssh_pass")
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(host, username = username, password = pw)
        self.sftp = client.open_sftp()
        self.save_file(text)
        client.close()

    def save_file(self, filepath):
        if (os.path.isdir(filepath)):
            filepath += self.view.file_name().split('/')[-1] 
        self.sftp.put(self.view.file_name(), filepath)

class RemoteSaveCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        self.s = sublime.load_settings("REditPreferences.sublime-settings")
        w_dir = self.s.get("workspace_dir")
        host = self.s.get("ssh_host")
        username = self.s.get("ssh_username")
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(host, username = username, password = pw)
        self.sftp = client.open_sftp()
        self.curr_dir = os.path.join(str(w_dir),str(username)+"@"+str(host))
        remote_path = os.path.abspath(os.path.relpath(self.view.file_name(), self.curr_dir))
        self.save_file(remote_path)
        client.close()

    def save_file(self, filepath):
        self.sftp.put(self.view.file_name(), filepath)
