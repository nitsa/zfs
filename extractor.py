# ------------------- >> Script code starts here <<-----------------------

# Ported for Python 3

import struct
import lz4.frame
import datetime

# Input image - can change this
image_path = 'ada0.backup'

# Chunk size of data read from image - can change this
chunk_size = 1024

# Approx. distance of signature from LZ4_data_size DWORD - can change this
sig_offset = 20

# Number of signature bytes - can change this
sig_len = 7
# Signature bytes - can change those
sig_byte_0 = 0x7B
sig_byte_1 = 0x5C
sig_byte_2 = 0x72
sig_byte_3 = 0x74
sig_byte_4 = 0x66
sig_byte_5 = 0x31
sig_byte_6 = 0x5C

current_pos = 1

def current_datetime():
 now = datetime.datetime.now()
 return now.strftime("%Y-%m-%d %H:%M:%S")

with open(image_path, 'rb') as f:
 print ('[*] ' + current_datetime() + ' Started')

 while True:
  buf = f.read(chunk_size)

  if buf:
   i = 0
   # Find data
   while (i < len(buf) - sig_len):
    if buf[i] == sig_byte_0:
     if buf[i + 1] == sig_byte_1:
      if buf[i + 2] == sig_byte_2:
       if buf[i + 3] == sig_byte_3:
        if buf[i + 4] == sig_byte_4:
         if buf[i + 5] == sig_byte_5:
          if buf[i + 6] == sig_byte_6:
           sig_pos = f.tell() - (chunk_size - i)
           save_pos = f.tell()
           print ('[*] ' + current_datetime() + \
                  ' Sig found at offset ' + str(sig_pos))
           f.seek(sig_pos - sig_offset, 0)
           buf = f.read(sig_offset)
           j = sig_offset - 1

           # Find data size
           while (j > 0) :
			# ZFS max block size starts from 65KB
            if buf[j] <= 0x01:
             if buf[j - 1] == 0x00:
              data_size = struct.unpack('>I',buf[j - 1:j - 1 + 4])[0] + 4
              
              print ('[*] ' + current_datetime() + \
                     ' Compressed data size found')

              # Extract compressed data
              f.seek(sig_pos - (sig_offset - j + 1) + 4, 0)
              payload = f.read(data_size)

              # LZ4 header (hard-coded)
              # 0x04 0x22 0x4D 0x18 0x40 0x40 0xC0
              
              header = bytearray()
              header.append(0x04)
              header.append(0x22)
              header.append(0x4D)
              header.append(0x18)
              header.append(0x40)
              header.append(0x40)
              header.append(0xC0)
              header.append(buf[j + 2])
              header.append(buf[j + 1])
              header.append(buf[j])
              header.append(buf[j - 1])
              
              #header = chr(0x04) + chr(0x22) + chr(0x4D) + chr(0x18) + \
              #         chr(0x40) + chr(0x40) + \
              #         chr(0xC0) + \
              #         buf[j + 2] + buf[j + 1] + buf[j] + buf[j - 1]
              data = header + payload
              
              cf = 'compressed_' + str(sig_pos)
              n = open(cf, 'wb')
              n.write(data)
              n.close()
              
              print ('[*] ' + current_datetime() + \
                     ' Dumped compressed file ' + cf)

              df = 'decompressed_' + str(sig_pos) + '.rtf'

              #try:
              decompressed = lz4.frame.decompress(data)
              n = open(df, 'wb')
              n.write(decompressed)
              n.close()
              print ('[*] ' + current_datetime() + \
                      ' Decompressed in file ' + df)
              # This will catch error in case of incomplete compressed buff
              #except:
               #print ('[*] ' + current_datetime() + \
               #       ' Error during decompressing file ' + df)
               #pass

              break

            j = j - 1

           # Restore position and keep searching for files
           f.seek(save_pos, 0)
    i = i + 1

   if len(buf) == chunk_size:
    f.seek(-sig_len, current_pos)

  else:
   print ('[*] ' + current_datetime() + ' Finished')
   break

# -------------------- >> Script code ends here <<------------------------
