import os
import tkinter
from tkinter import PhotoImage, Canvas
import json
from cryptography.fernet import Fernet
import smtplib
from email.message import EmailMessage

"""  Kullanıcı adı: tuncay
     Şifre: 123456  """



# Kullanıcı verilerinin dosya yolu
USER_DATA_FILE = "users.json"

# Kullanıcı verilerini dosyadan okuma/oluşturma
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "w") as file:
        json.dump({}, file)  # Boş bir sözlük olarak başlat

with open(USER_DATA_FILE, "r") as file:
    kullanıcıListesi = json.load(file)

# Anahtar oluşturma ve kaydetme/okuma işlemleri
try:
    with open("key.key", "rb") as key_file:
        key = key_file.read()
except FileNotFoundError:
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

cipher_suite = Fernet(key)


def save_user_list():
    try:
        with open("user_list.json", "w") as file:
            json.dump(kullanıcıListesi, file)
    except Exception as e:
        print(f"Error saving user list: {e}")


def load_user_list():
    global kullanıcıListesi
    try:
        with open("user_list.json", "r") as file:
            kullanıcıListesi = json.load(file)
    except FileNotFoundError:
        kullanıcıListesi = {}  # Eğer dosya yoksa boş bir liste oluştur
    except Exception as e:
        print(f"Error loading user list: {e}")
        kullanıcıListesi = {}
kullanıcıListesi = {"tuncay": "123456"}
load_user_list()

# Şifreleme ve Deşifreleme fonksiyonları
def encrypt_and_save():
    title = entry1.get()
    notes = text1.get("1.0", tkinter.END)
    master_key = entry3.get()

    if not title or not notes or not master_key:
        message_label.config(text="Please fill all fields.", fg="red")
        return

    try:
        # Şifreleme işlemi
        encrypted_notes = cipher_suite.encrypt((notes + master_key).encode())
        with open(f"{title}.{username}.enc", "wb") as file:
            file.write(encrypted_notes)
        message_label.config(text="Notes encrypted and saved successfully!", fg="green")
    except Exception as e:
        message_label.config(text=f"Error: {e}", fg="red")
    finally:
        entry1.delete(0, tkinter.END)
        text1.delete("1.0", tkinter.END)
        entry3.delete(0, tkinter.END)


def decrypt_and_show():
    title = entry1.get()
    master_key = entry3.get()

    if not title or not master_key:
        message_label.config(text="Please provide a title and master key.", fg="red")
        return

    try:
        # Şifrelenmiş dosyayı okuma ve çözme
        with open(f"{title}.{username}.enc", "rb") as file:
            encrypted_notes = file.read()
        decrypted_notes = cipher_suite.decrypt(encrypted_notes).decode()

        # Şifre çözülmüş notları kontrol et
        if decrypted_notes.endswith(master_key):
            text1.delete("1.0", tkinter.END)
            text1.insert(tkinter.END, decrypted_notes[:-len(master_key)])
            message_label.config(text="Notes decrypted successfully!", fg="green")
        else:
            message_label.config(text="Invalid master key!", fg="red")
    except FileNotFoundError:
        message_label.config(text="Encrypted file not found.", fg="red")
    except Exception as e:
        message_label.config(text=f"Error: {e}", fg="red")

def showMyNotes():
    newWindow= tkinter.Toplevel(window)
    newWindow.title("All notes")
    newWindow.geometry("500x400")

    titleLabel= tkinter.Label(newWindow, text="saved notes",font=("Arial",14,"normal"))
    titleLabel.pack(pady=10)
    for file_name in os.listdir():
        if file_name.endswith(f"{username}.enc"):
            title= file_name[:-(len(username)+5)]
            with open(file_name, "rb") as file:
                encrypted_content= file.read()
            tkinter.Label(newWindow, text=f"Title: {title}", font=("Arial", 12, "bold"), fg="red").pack(anchor="w",padx=10)
            text_widget = tkinter.Text(newWindow, height=3, width=60, wrap="word")
            text_widget.insert("1.0", encrypted_content.decode())
            text_widget.config(state="disabled")  # Düzenlenmeyi önlemek için
            text_widget.pack(anchor="w", padx=10, pady=5)

def clearAll():
    entry1.delete(0, tkinter.END)
    text1.delete("1.0", tkinter.END)
    entry3.delete(0, tkinter.END)


def login():
    global window, entry1, entry3, text1, message_label, photo, photoLabel, username

    username = girisEntry.get()
    password = sifreEntry.get()
    if username in kullanıcıListesi and kullanıcıListesi[username] == password:
        giris.destroy()
        window = tkinter.Tk()
        window.title("Secret!!")
        window.minsize(width=400, height=500)
        window.config(padx=0, pady=20)

        photo= PhotoImage(file=r"C:\Users\yalci\OneDrive\Masaüstü\topSecret.png")
        #photoLabel= tkinter.Label(image=photo)
        #photoLabel.pack()

        canvas= tkinter.Canvas(height=150,width=150)
        canvas.create_image(100,100,image=photo)
        canvas.pack()

        label1 = tkinter.Label(window, text="Enter your title",fg="dark blue")
        label1.pack()
        entry1 = tkinter.Entry(window, width=35)
        entry1.pack()

        label2 = tkinter.Label(window, text="Enter your notes",fg="dark blue")
        label2.pack()
        text1 = tkinter.Text(window, width=40, height=15, font=("Arial", 12))
        text1.pack()

        label3 = tkinter.Label(window, text="Enter master key",fg="dark blue")
        label3.pack()
        entry3 = tkinter.Entry(window, width=40, show="*")
        entry3.pack()

        pushButton1 = tkinter.Button(window, text="Save & Encrypt", command=encrypt_and_save)
        pushButton1.pack()
        pushButton2 = tkinter.Button(window, text="Decrypt", command=decrypt_and_show)
        pushButton2.pack()
        pushButton3 = tkinter.Button(window, text="My Notes", command=showMyNotes)
        pushButton3.pack()
        pushButton4 = tkinter.Button(window, text="Clear all", command=clearAll)
        pushButton4.pack()

        message_label = tkinter.Label(window, text="", fg="green")
        message_label.pack()

    elif girisEntry.get() == "" or sifreEntry.get() == "":
        error_label.config(text="Please enter all values!", fg="red")

    elif girisEntry.get() != "tuncay" or sifreEntry.get() != 123456:
        error_label.config(text="Invalid username or password!", fg="red")

    else:
        error_label.config(text="Unknown error", fg="red")

'''def sendeMail(): ### HATALI ÇALIŞMIYOOOOR ###
    myePostaName= "secretnoteshello@yahoo.com"
    myePostaPassword= "D656F59307A686E72F21DECC42D9ABFFDF8D"
    userePosta= ePosta

    message = EmailMessage()
    message["Subject"] = "Welcome to Secret Notes!"
    message["From"] = myePostaName
    message["To"] = userePosta
    message.set_content("Welcome to Secret Notes family! \nWe are so happy to see you. \nEnjoy the Secret Notes and don't forget nobody see your notes!")

    try:
        # SMTP sunucusuna bağlanma ve e-posta gönderme
        with smtplib.SMTP_SSL("smtp.elasticemail.com", 465) as smtp:  # xxGmailxx için SMTP ayarları
            smtp.login(myePostaName, myePostaPassword)
            smtp.send_message(message)
        print("E-posta başarıyla gönderildi!")
    except Exception as e:
        print(f"E-posta gönderilirken hata oluştu: {e}")

    try:
        # Yahoo SMTP ayarları (TLS kullanımı)
        with smtplib.SMTP("smtp.mail.yahoo.com", 587) as smtp:
            smtp.starttls()  # TLS şifrelemesini başlat
            smtp.login(myePostaName, myePostaPassword)
            smtp.send_message(message)
        print("E-posta başarıyla gönderildi!")
    except Exception as e:
        print(f"E-posta gönderilirken hata oluştu: {e}")'''


def accountAdd():
    global kullanıcıListesi, ePosta
    ePosta = ePostaEntry.get()
    username = kayıtOlEntry.get()
    password = kayıtSifreEntry.get()
    if not ePosta.endswith("@gmail.com"):
        kayıtErrorLabel.config(text="Please use @gmail e-Posta name!!!", fg="red")
        return

    if not ePosta or not username or not password:
        kayıtErrorLabel.config(text="Please fill all fields!", fg="red")
        return

    if username in kullanıcıListesi:
        kayıtErrorLabel.config(text="Username already exists!", fg="red")
        return

    kullanıcıListesi[username] = password
    save_user_list()  # Kullanıcı listesini kaydetmek için
    kayıtErrorLabel.config(text="Account created successfully!", fg="green")
    ###sendeMail()


def signUpPage():
    global ePostaEntry, kayıtOlEntry, kayıtSifreEntry, kayıtErrorLabel
    giris.destroy()

    kayıtOl= tkinter.Tk()
    kayıtOl.title("Sign Up Page")
    kayıtOl.minsize(width=350,height=200)

    ePostalLabel= tkinter.Label(kayıtOl, text="E-Posta")
    ePostalLabel.pack()
    ePostaEntry= tkinter.Entry(kayıtOl, width=35)
    ePostaEntry.pack()

    kayıtOlLabel= tkinter.Label(kayıtOl, text="Username")
    kayıtOlLabel.pack()
    kayıtOlEntry= tkinter.Entry(kayıtOl, width=30)
    kayıtOlEntry.pack()

    kayıtSifreLabel= tkinter.Label(kayıtOl, text="Password")
    kayıtSifreLabel.pack()
    kayıtSifreEntry= tkinter.Entry(kayıtOl, width=30)
    kayıtSifreEntry.pack()

    kayıtOlusturButton= tkinter.Button(kayıtOl, text="Create Account", command=accountAdd, background="green")
    kayıtOlusturButton.pack()

    kayıtErrorLabel = tkinter.Label(kayıtOl, text="", fg="red")
    kayıtErrorLabel.pack()




giris= tkinter.Tk()
giris.title("Login Page")
giris.minsize(width=300,height=200)

infoPhoto= PhotoImage(file=r"C:\Users\yalci\OneDrive\Masaüstü\loginPhoto.png")
canvas= tkinter.Canvas(height=150,width=150)
canvas.create_image(80,80,image=infoPhoto)
canvas.pack()

girisLabel= tkinter.Label(giris, text="Username")
girisLabel.pack()
girisEntry= tkinter.Entry(giris, width=25)
girisEntry.pack()

girisSifre= tkinter.Label(giris, text="Password")
girisSifre.pack()
sifreEntry= tkinter.Entry(giris, width=25, show="*")
sifreEntry.pack()

error_label = tkinter.Label(giris, text="", fg="red")
error_label.pack()

girisButton= tkinter.Button(giris, text="Login",command=login, background="light blue", relief="flat", bd=4)
girisButton.pack()

kayıtOlButton= tkinter.Button(giris, text="Sign Up", command=signUpPage, background="light blue", relief="flat", bd=4)
kayıtOlButton.pack()

giris.mainloop()