from __future__ import print_function

import sys
import os


def parser(args):
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Convert all fake stereo audio files under current directory into mono channel files, with the option to delete empty audio files.')
    parser.add_argument('-a', '--auto',
                        action='store_true',
                        help='Backup to "RAW", \
                        delete empty audio files, \
                        and monolize fake stereos.')
    parser.add_argument('-b', '--backup',
                        nargs=1, default=['RAW'],
                        help='Name of the sub-folder to backup all files to. \
                        Default: "RAW"')
    parser.add_argument('-i', '--inc',
                        action='store_true',
                        help='Add a number to the backup folder name if the \
                        folder exists to avoid overwriting existing folder.')
    parser.add_argument('-f', '--file',
                        nargs=1, default='',
                        help='Select a single file to monolize.')
    parser.add_argument('-r', '--remove',
                        action='store_true',
                        help='Remove all empty/silent audio files')
    parser.add_argument('-m', '--monolize',
                        action='store_true',
                        help='Convert all fake stereo files into mono files.')
    parser.add_argument('-o', '--overwrite',
                        action='store_true',
                        help='Make permanent change to the original file \
                        without backing up.')
    # parser.add_argument('-s', '--subfolder',
    #                     action='store_true',
    #                     help='Include files in sub-folder during conversion.')
    args = parser.parse_args()
    return args


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    args = parser(args)

    if args.file:
        from monolizer import Monolizer
        with Monolizer(file=args.file[0]) as obj:
            print(obj)
    else:
        from monolizer import FileHandler

        folder = FileHandler(folder=os.getcwd())
        if len(folder.files) == 0:
            print('No audio files found in current directory.')
        else:
            if args.auto or args.delete or args.monolize:
                if args.auto or (not args.overwrite and args.backup):
                    folder.backup(folder=args.backup[0], newfolder=args.inc)
                    print('Backed up all original files to {} subfolder'.format(args.backup[0]))
                if args.auto or args.remove:
                    files = folder.remove_empty_files()
                    print('Deleted files: {}'.format(' '.join(files)))
                if args.auto or args.monolize:
                    files = folder.monolize_fake_stereo_files()
                    print('Monolized files: {}'.format(' '.join(files)))
            else:
                print(folder)

        del folder

if __name__ == "__main__":
    main()
