import sublime, sublime_plugin
import paramiko
import tempfile
import time
import os

class RemoteOpenCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window.show_input_panel("Remote File Path:", "", self.on_done, None, None)
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
        self.read_file(text)
        client.close()
        pass

    def read_file(self, filepath):
        try:
            remotefile = self.sftp.open(filepath, mode='r')
            temp_dir = tempfile.mkdtemp(prefix='REdit-')
        except IOError as e:
            sublime.error_message("Could not find file %s" % filepath)
            return
        except OSError as e:
           sublime.error_message("Failed to create a temporary directory! Error: %s" % e)
           return
        file_name = filepath.split('/')[-1]
        local_path = os.path.join(temp_dir, file_name)
        local_file = open(local_path, "w+")
        file_contents = remotefile.read()
        local_file.write(file_contents)
        local_file.flush()
        local_file.seek(0)
        self.window.open_file(local_path)

class RemoteSaveCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        self.window.show_input_panel("Remote File Path:", "", self.on_done, None, None)
        #print(self.view.substr(sublime.Region(0, self.view.size())))

    def on_done(self, text):
        print("You wrote " + text)
        s = sublime.load_settings("REditPreferences.sublime-settings")
        host = s.get("ssh_host")
        username = s.get("ssh_username")
        pw = s.get("ssh_pass")
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(host, username = username, password = pw)
        sftp = client.open_sftp()
        remotefile = sftp.open(text, mode='r')
        self.read_file(remotefile)
        client.close()