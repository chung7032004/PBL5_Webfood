# client_socket_send.py
import socket
import struct

# Mở ảnh
filename = "E:/KI6/PBL5/Screenshot 2025-05-24 141507.png"
with open(filename, "rb") as f:
    image_data = f.read()

# Tạo socket TCP
print("Đang kết nối đến server...")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('10.10.59.201', 5001))  # thay IP của server

# Gửi độ dài ảnh (4 byte)
length = len(image_data)
client.sendall(struct.pack('>I', length))

# Gửi dữ liệu ảnh
client.sendall(image_data)

print("Đã gửi xong ảnh.")
client.close()
