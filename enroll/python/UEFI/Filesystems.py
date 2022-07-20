#
# Copyright 2019-2021 Canonical Ltd.
# Authors:
# - dann frazier <dann.frazier@canonical.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import shutil
import subprocess
import tempfile


class FatFsImage:
    def __init__(self, size_in_mb):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            self.path = f.name

        subprocess.check_call(
            [
                'dd', 'if=/dev/zero', 'of=%s' % (self.path),
                'count=0', 'bs=1M', 'seek=%d' % (size_in_mb), 'status=none'
            ]
        )
        new_env = os.environ.copy()
        new_env['PATH'] = f"{os.environ['PATH']}:/sbin"
        subprocess.check_call(['mkdosfs', '-F', '32', self.path], env=new_env)

    def __del__(self):
        os.unlink(self.path)

    def mkdir(self, dir):
        subprocess.run(['mmd', '-i', self.path, dir])

    def makedirs(self, dir):
        dirs = dir.split(os.path.sep)
        for dir_idx in range(1, len(dirs)+1):
            next_dir = os.path.sep.join(dirs[:dir_idx])
            self.mkdir(next_dir)

    def insert_file(self, src, dest):
        subprocess.check_call(
            [
                'mcopy', '-i', self.path, src, '::%s' % (dest)
            ]
        )


class EfiBootableIsoImage:
    def __init__(self, eltorito_img):
        with tempfile.TemporaryDirectory() as iso_root:
            eltorito_iso_root = 'boot'
            eltorito_iso_path = os.path.join(eltorito_iso_root, 'efi.img')
            eltorito_local_root = os.path.join(iso_root, eltorito_iso_root)
            eltorito_local_path = os.path.join(iso_root, eltorito_iso_path)

            os.makedirs(eltorito_local_root)
            shutil.copyfile(eltorito_img.path, eltorito_local_path)

            with tempfile.NamedTemporaryFile(delete=False) as f:
                self.path = f.name

            subprocess.check_call(
                [
                    'xorriso', '-as', 'mkisofs', '-J', '-l',
                    '-c', 'boot/boot.cat',
                    '-partition_offset', '16', '-append_partition', '2',
                    '0xef', eltorito_local_path,
                    '-e', '--interval:appended_partition_2:all::',
                    '-no-emul-boot', '-o', self.path, iso_root
                ]
            )

    def __del__(self):
        os.unlink(self.path)


class GrubShellBootableIsoImage(EfiBootableIsoImage):
    def __init__(self, efi_arch, use_signed):
        EfiArchToGrubArch = {
            'X64': "x86_64",
            'AA64': "arm64",
        }
        efi_img = FatFsImage(64)
        efi_img.makedirs(os.path.join('EFI', 'BOOT'))
        removable_media_path = os.path.join(
            'EFI', 'BOOT', 'BOOT%s.EFI' % (efi_arch.upper())
        )
        efi_ext = 'efi'
        grub_subdir = "%s-efi" % EfiArchToGrubArch[efi_arch.upper()]
        if use_signed:
            efi_ext = "%s.signed" % (efi_ext)
            grub_subdir = "%s-signed" % (grub_subdir)

        shim_src = os.path.join(
            os.path.sep, 'usr', 'lib', 'shim',
            'shim%s.%s' % (efi_arch.lower(), efi_ext)
        )
        grub_src = os.path.join(
            os.path.sep, 'usr', 'lib', 'grub',
            '%s' % (grub_subdir),
            "" if use_signed else "monolithic",
            'grub%s.%s' % (efi_arch.lower(), efi_ext)
        )
        grub_dest = os.path.join(
            'EFI', 'BOOT', 'GRUB%s.EFI' % (efi_arch.upper())
        )
        efi_img.insert_file(shim_src, removable_media_path)
        efi_img.insert_file(grub_src, grub_dest)
        super().__init__(efi_img)
