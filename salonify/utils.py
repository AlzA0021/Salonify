import os
from uuid import uuid4


# -------------------------------------------------------------------
# File Uploader
class File_Uploader:
    def __init__(self, dir, prefix):
        self.dir = dir
        self.prefix = prefix

    def upload_to(self, instance, filename):
        filename, ext = os.path.splitext(filename)
        return f"{self.dir}/{self.prefix}/{uuid4()}{ext}"


# -------------------------------------------------------------------
def create_random_code(count):
    import random

    count -= 1
    return random.randint(10**count, 10 ** (count + 1) - 1)


# -------------------------------------------------------------------
def send_sms(mobile_number, message):
    pass
    # try:
    #     api = KavenegarAPI('4E59314842514E49415669774637352B684B376D6435442B564C72346C36624E735058727664463438754D3D', )
    #     params = {
    #         'sender': '',#optional
    #         'receptor': 'mobile_number',#multiple mobile number, split by comma
    #         'message': 'message',
    #     }
    #     response = api.sms_send(params)
    #     print(response)
    # except APIException as e:
    #     print(e)
    # except HTTPException as e:
    #     print(e)


# ----------------------------------------------------------------------
