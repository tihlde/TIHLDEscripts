# coding: utf-8
__author__ = 'Harald Floor Wilhelmsen'


class LogSolution:
    log_files = {}

    def __init__(self, log_files, standard_file_name):
        """
        Initializes the log-object
        :param log_files: A list of *file*-names without extensions.
        Log-files with these names will be created in /var/log.
        """
        for file_name in log_files:
            self.log_files[file_name] = '/var/log/{}.log'.format(file_name)
        self.log_files['standard_log_file'] = '/var/log/{}.log'.format(standard_file_name)

    def log(self, entry, log_file_name, print_entry=True):
        if print_entry:
            print(entry)
        with open(self.log_files[log_file_name], 'a') as log_file:
            log_file.write(entry + '\n')
