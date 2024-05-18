import logging
import os
import hashlib
import shutil
import sched
import time


class FolderSynchronizer:
    def __init__(self, source_folder: str, replica_folder: str, logger: logging.Logger):
        """
        Initialize the FolderSynchronizer with source and replica folder paths and a logger.

        Args:
            source_folder (str): Path to the source folder.
            replica_folder (str): Path to the replica folder.
            logger: Logger object for logging synchronization activities.
        """
        self.source_hash, self.replica_hash = {}, {}  # Dictionary to store hashes of files
        self.source_folder = source_folder
        self.replica_folder = replica_folder
        self.scheduler = sched.scheduler(time.time, time.sleep)  # Scheduler for periodic tasks

        self.logger = logger  # Logger for logging activities

    def _calculate_file_hash(self, file_path, hash_function=hashlib.md5, chunk_size=1000000) -> str:
        """
        Calculate and return the hash of the file using the specified hash function.

        Args:
            file_path (str): Path to the file for which the hash is to be calculated.
            hash_function: Hash function to use (default is hashlib.md5).
            chunk_size (int): Size of the chunks to read from the file (default is 1,000,000 bytes).

        Returns:
            str: The calculated hash of the file.
        """
        hasher = hash_function()
        with open(file_path, 'rb') as file:
            while chunk := file.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()

    def compare_hashes(self):
        """
        Compare the hashes of the source and replica directories and synchronize the replica
        directory with the source directory. Log the changes made.
        """
        source_files = set(self.source_hash.keys())
        replica_files = set(self.replica_hash.keys())

        added_files = source_files - replica_files  # Files that are in source but not in replica
        removed_files = replica_files - source_files  # Files that are in replica but not in source
        modified_files = {file for file in source_files & replica_files if
                          self.source_hash[file] != self.replica_hash[file]}  # Files that are modified

        if added_files:
            message = 'Added files:'
            for file in added_files:
                source_file_path = os.path.join(self.source_folder, file)
                replica_file_path = os.path.join(self.replica_folder, file)
                if os.path.isdir(source_file_path):  # Check if the source path is a directory
                    os.makedirs(replica_file_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(replica_file_path), exist_ok=True)
                    self.copy_file(source_file_path, replica_file_path)
                message += f' {file};'
            self.logger.info(message)

        if removed_files:
            message = 'Removed files:'
            for file in removed_files:
                replica_file_path = os.path.join(self.replica_folder, file)
                if os.path.exists(replica_file_path):  # Check if the replica path exists
                    if os.path.isdir(replica_file_path):  # Check if the replica path is a directory
                        shutil.rmtree(replica_file_path)  # Remove the directory
                    else:
                        os.remove(replica_file_path)  # Remove the file
                message += f' {file};'
            self.logger.info(message)

        if modified_files:
            message = 'Modified files:'
            for file in modified_files:
                source_file_path = os.path.join(self.source_folder, file)
                replica_file_path = os.path.join(self.replica_folder, file)
                self.copy_file(source_file_path, replica_file_path)  # Copy the modified file to replica
                message += f' {file};'
            self.logger.info(message)

    def process_directory(self, source_path: str) -> dict:
        """
        Process a directory, including its subdirectories, and calculate hashes for all files.

        Args:
            source_path (str): Path to the directory to process.

        Returns:
            dict: A dictionary with relative file paths as keys and their hashes as values.
        """
        hash_dict = {}
        for root, dirs, files in os.walk(source_path):  # Walk through the directory
            for dir_ in dirs:
                dir_path = os.path.join(root, dir_)
                relative_path = os.path.relpath(dir_path, source_path)
                hash_dict[relative_path] = None
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_hash = self._calculate_file_hash(file_path)

                    # Store the hash in the dictionary with relative path as key
                    relative_path = os.path.relpath(file_path, source_path)
                    hash_dict[relative_path] = file_hash
                except Exception as e:
                    self.logger.exception(f'Error processing file {file_path}: {e}')
        return hash_dict

    def copy_file(self, source_file: str, destination_file: str):
        """
        Copy a file from the source to the destination path.

        Args:
            source_file (str): Path to the source file.
            destination_file (str): Path to the destination file.
        """
        shutil.copy2(source_file, destination_file)  # Copy the file preserving metadata

    def sync_folders(self):
        """
        Synchronize the source folder with the replica folder by processing directories and
        comparing hashes.
        """
        self.source_hash = self.process_directory(self.source_folder)  # Process the source directory
        self.replica_hash = self.process_directory(self.replica_folder)  # Process the replica directory
        self.compare_hashes()

    def periodic_sync(self, sync_interval: int = 10):
        """
        Continuously synchronize folders at a specified interval.

        Args:
            sync_interval (int): Time interval (in seconds) between synchronization attempts (default is 10 seconds).
        """
        self.logger.info(f'Synchronizer started ...')
        while True:
            self.sync_folders()
            time.sleep(sync_interval)
