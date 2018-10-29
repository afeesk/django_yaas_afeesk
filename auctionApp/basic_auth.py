import base64
user = "afeesk"
password = "yaas3211"

hd_value = '%s:%s' % (user, password)
encoded_bytes = base64.b64encode(hd_value.encode())
encoded_str = encoded_bytes.decode()
print ("Authorization: Basic", encoded_str)
