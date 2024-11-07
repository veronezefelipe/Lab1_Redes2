import socket
import ssl
import base64

# Configurações do servidor SMTP do Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587
username = "veronezetest@gmail.com"  
password = "idgj blxe whuc golq"      

# Configuração do destinatário
from_address = "veronezetest@gmail.com"
to_address = "veronezett@gmail.com"
subject = "Envio SMTP"
body = "Olá, essa é uma mensagem de teste do Vero."

arqvanexo = "SMTP.jpeg"  

# Função para enviar um comando e verificar a resposta
def send_command(sock, command, expected_code):
    sock.send((command + "\r\n").encode())
    recv = sock.recv(1024).decode()
    if not recv.startswith(expected_code):
        raise Exception(f"Erro no comando '{command}': {recv}")

try:
    # Conectar ao servidor SMTP e iniciar TLS
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((smtp_server, smtp_port))
    recv = client_socket.recv(1024).decode()
    if not recv.startswith("220"):
        raise Exception("220 resposta não recebida do servidor.")

    # Enviar EHLO e iniciar TLS
    send_command(client_socket, "EHLO cliente", "250")
    send_command(client_socket, "STARTTLS", "220")

    # Envolver o socket com SSL para criptografia
    client_socket = ssl.wrap_socket(client_socket)

    # Enviar EHLO novamente após iniciar TLS
    send_command(client_socket, "EHLO cliente", "250")

    # Autenticação LOGIN
    send_command(client_socket, "AUTH LOGIN", "334")
    send_command(client_socket, base64.b64encode(username.encode()).decode(), "334")
    send_command(client_socket, base64.b64encode(password.encode()).decode(), "235")

    # Comando MAIL FROM
    send_command(client_socket, f"MAIL FROM:<{from_address}>", "250")

    # Comando RCPT TO
    send_command(client_socket, f"RCPT TO:<{to_address}>", "250")

    # Comando DATA para iniciar o corpo da mensagem
    send_command(client_socket, "DATA", "354")

    # Montar o cabeçalho da mensagem com anexo
    message = f"From: {from_address}\r\n"
    message += f"To: {to_address}\r\n"
    message += f"Subject: {subject}\r\n"
    message += "MIME-Version: 1.0\r\n"
    message += "Content-Type: multipart/mixed; boundary=boundary42\r\n\r\n"
    message += "--boundary42\r\n"
    message += "Content-Type: text/plain\r\n\r\n"
    message += body + "\r\n\r\n"

    # Adicionar a imagem como anexo
    message += "--boundary42\r\n"
    message += "Content-Type: application/octet-stream\r\n"
    message += f"Content-Disposition: attachment; filename={arqvanexo}\r\n"
    message += "Content-Transfer-Encoding: base64\r\n\r\n"

    # Ler a imagem e codificar em base64
    with open(arqvanexo, "rb") as attachment:
        image_data = attachment.read()
        encoded_image = base64.b64encode(image_data).decode()
        message += encoded_image + "\r\n"

    # Finalizar o corpo da mensagem
    message += "--boundary42--\r\n.\r\n"

    # Enviar a mensagem completa
    client_socket.send(message.encode())
    recv = client_socket.recv(1024).decode()
    if not recv.startswith("250"):
        raise Exception("Erro ao enviar mensagem.")

    # Comando QUIT para encerrar a sessão SMTP
    send_command(client_socket, "QUIT", "221")

    print("E-mail enviado com sucesso!")

except Exception as e:
    print(f"Erro ao enviar e-mail: {e}")

finally:
    client_socket.close()
