import sublime, sublime_plugin
import paramiko
import tempfile
import time

class RemoteOpenCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window.show_input_panel("Remote File Path:", "", self.on_done, None, None)
        pass

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
        pass

    def read_file(self, file):
        try:
           temp_file = tempfile.NamedTemporaryFile(prefix='REdit-')
        except OSError as e:
        	sublime.error_message("Failed to create a temporary file! Error: %s" % e)
        file_contents = file.read()
        print("Remote file contents: " + file_contents)
        temp_file.write(file_contents)
        temp_file.seek(0)
        #temp_file.flush()
        print("Temporary file contents: " + temp_file.read())
        self.window.open_file(temp_file.name)
        