# -*- coding: utf-8 -*-

# POC of video encryption using Python, OpenSSL & FFMPeg

"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>. 1
"""

# Imports
import random
import os

VIDEO_FILE = "bars_100.avi"
FRAMES_DIRECTORY = "frames/"
OUTPUT_DIRECTORY = "bin/"
CRYPTD_DIRECTORY = "crypt/"

# Creating the directories
os.system("mkdir " + FRAMES_DIRECTORY)
os.system("mkdir " + OUTPUT_DIRECTORY)
os.system("mkdir " + CRYPTD_DIRECTORY)

# ffmpeg -y -i bars_100.avi  -an -vcodec bmp -s 1024x768 pic%d.bmp
FFMPEG_CMD = "ffmpeg -y -i " + VIDEO_FILE +" -an -vcodec bmp -s 1024x768 "+ FRAMES_DIRECTORY +"pic%d.bmp >> /dev/null"

# Convert video to frames, save them in the plain frames directory
os.system(FFMPEG_CMD)
print "[+] DEBUG : Converted the file to frames"

# Get number of frames outputed
bmp_count = int(os.popen('ls ./frames | wc -l').read())

print "[+] DEBUG : Number of frames outputed : " + str(bmp_count)

# Read all the bmp files and cut the 54 first bytes of it (the headers)
for i in range(1, bmp_count+1):
    i_file = FRAMES_DIRECTORY + "pic" + str(i) + ".bmp"
    o_file = OUTPUT_DIRECTORY + "pic" + str(i) + ".bin"

    fi_open = open(i_file, 'rb')
    fi_open.read(54)

    fo_open = open(o_file, 'wb')
    fo_open.write(fi_open.read())

    fo_open.close()
    fi_open.close()

print "[+] DEBUG : Done cutting of the headers"

# Generate n random key for the encryption, where n = bmp_count
iv = "0123456789ABCDEF" # 64 bits
key = "0123456789ABCDEF0123456789ABCDEF" # 128 bits

key_list = []
iv_list = []

for i in range(0, bmp_count):
    key_list.append(''.join(random.sample(key,len(key))))
    iv_list.append(''.join(random.sample(iv,len(iv))))

print "[+] DEBUG : Key and IV lists generated"

print "[+] DEBUG : Starting encryption"

# Take each file, DES/AES it and store it back; we will eventually
# give him back his BMP headers
for i in range(0, bmp_count):
    i_file = OUTPUT_DIRECTORY + "pic" + str(i+1) + ".bin"
    c_file = OUTPUT_DIRECTORY + "Cpic" + str(i+1) + ".bin"
    o_file = CRYPTD_DIRECTORY + "pic" + str(i+1) + ".bmp"

    # I choose ECB mode to see the "problem" with it
    # Any other encryption scheme will work
    # You must take care of the size of the keys and the IVs

    command = "openssl enc -aes-128-ecb -in " + i_file + " -out " + c_file
    #command += " -iv " + iv_list[i]
    command += " -K " + key_list[i]
    os.system(command)

    fi_open = open(c_file, 'rb')
    i_bytes = fi_open.read()
    fi_open.close()

    fo_open = open(o_file, 'wb')

    # All the frames have the same header, so ...
    headers = open("frames/pic1.bmp", "rb").read(54)
    fo_open.write(headers)
    fo_open.write(i_bytes)
    fo_open.close()

print "[+] DEBUG : Done encrypting the frames"

print "[+] DEBUG : Creating the assembled video"

# Reunite the frames into one video
os.system("ffmpeg -i crypt/pic%d.bmp -y -f avi -b 1150 -s 1024x768 -r 29.97 -g 12 -qmin 3 -qmax 13 -ab 224 -ar 44100 -ac 2 ./test.avi")

print "[+] DEBUG : DONE !"