from api import API

a=API()
a.setidfv('55B7A4EC-4879-A4CA-194F-E3635EF68806')
a.setdeviceid('be0e33a6-a15c-4cf6-82d1-5139b6aebe1c')
a.setsecretkey('54cebb88-49fa-0375-bcb4-2c95d15eb792')
a.doLogin()
a.doMission('QE_OP_0002')