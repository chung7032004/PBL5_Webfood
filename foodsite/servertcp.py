# server_socket_receive.py
import socket
import struct

def recvall(sock, n):
    """Nhận đủ n byte từ socket"""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 5001))
server.listen(1)

print("Server đang chờ kết nối...")
conn, addr = server.accept()
print(f"Đã kết nối từ {addr}")

# Nhận 4 byte đầu tiên để biết kích thước ảnh
lengthbuf = recvall(conn, 4)
if not lengthbuf:
    print("Không nhận được kích thước ảnh")
    conn.close()

length, = struct.unpack('>I', lengthbuf)
print(f"Kích thước ảnh nhận: {length} byte")

# Nhận phần còn lại của ảnh
image_data = recvall(conn, length)

# Lưu ảnh
save_path = "E:/KI6/PBL5/testsavesocket/received.jpg"

with open(save_path, "wb") as f:
    f.write(image_data)

print("Đã lưu ảnh thành công")
conn.close()
