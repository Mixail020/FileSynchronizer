from folder_synchronizer import FolderSynchronizer
from logger import setup_logging
import argparse
def main():
    parser = argparse.ArgumentParser(description='Synchronize two folders.')
    parser.add_argument('-s', '--source_folder', type=str, help='The source folder to synchronize from')
    parser.add_argument('-r', '--replica_folder', type=str, help='The replica folder to synchronize to')
    parser.add_argument('-l', '--log_file', type=str, help='The log file path')
    parser.add_argument('-i', '--interval', type=int, default=10, help='The synchronization interval in seconds (default: 10 seconds)')

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log_file)

    # Initialize the FolderSynchronizer
    fsync = FolderSynchronizer(args.source_folder, args.replica_folder, logger)

    # Start the periodic synchronization
    fsync.periodic_sync(args.interval)

if __name__ == "__main__":
    main()