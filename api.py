# -*- coding: utf-8 -*-
import json
import requests
import sys
import random
import time
import datetime

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class API(object):
	def __init__(self):
		self.s=requests.session()
		self.s.verify=False
		self.s.headers.update({'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 10_2 like Mac OS X) AppleWebKit/602.3.12 (KHTML, like Gecko) Mobile/14C92','Content-Type':'application/json; charset=utf-8'})
		self.base='https://app.alcww.gumi.sg/'
		self.app_ver=1721
		self.ticket=1
		self.udid='00000000-0000-0000-0000-000000000000'
		self.idfa='00000000-0000-0000-0000-000000000000'
		self.idfv=None
		self.secret_key=self.genRandomDeviceID().lower()

	def setudid(self,id):
		self.udid=id
		
	def setidfa(self,id):
		self.idfa=id
		
	def setidfv(self,id):
		self.idfv=id
		
	def setdeviceid(self,id):
		self.device_id=id

	def setsecretkey(self,id):
		self.secret_key=id
		
	def genRandomHex(self,n):
		return ''.join([random.choice('0123456789ABCDEF') for x in range(n)])
		
	def genRandomDeviceID(self):
		return '%s-%s-%s-%s-%s'%(self.genRandomHex(8),self.genRandomHex(4),self.genRandomHex(4),self.genRandomHex(4),self.genRandomHex(12))
		
	def makeHeader(self):
		if hasattr(self, 'config'):
			if hasattr(self, 'access_token'):
				self.s.headers.update({'x-app-ver':str(self.app_ver),'X-GUMI-TRANSACTION':self.genRandomDeviceID().lower(),'x-asset-ver':self.config['body']['assets'],'Authorization':'gumi %s'%(self.access_token)})
			else:
				self.s.headers.update({'x-app-ver':str(self.app_ver),'X-GUMI-TRANSACTION':self.genRandomDeviceID().lower(),'x-asset-ver':self.config['body']['assets']})
		else:
			self.s.headers.update({'x-app-ver':str(self.app_ver),'X-GUMI-TRANSACTION':self.genRandomDeviceID().lower()})
		
	def log(self,msg):
		print '[%s] %s'%(time.strftime('%H:%M:%S'),msg)
			
	def callAPI(self,path,data=None,type=1):
		self.makeHeader()
		if type == 1:
			r=self.s.post(self.base+path,data=json.dumps(data))
		else:
			r=self.s.get(self.base+path)
		self.ticket+=1
		if 'body' in r.content and 'player' in r.content and 'player' in json.loads(r.content)['body'] and 'id' in json.loads(r.content)['body']['player']:
			self.userlog(json.loads(r.content))
			if 'btlid' in r.content and json.loads(r.content)['body']['player']['btlid']>=1:
				self.resumemission(json.loads(r.content)['body']['player']['btlid'])
		if 'stat_msg' in r.content and len(json.loads(r.content)['stat_msg'])>=1:
			self.log((json.loads(r.content)['stat_msg'].encode('utf8','ignore')))
			return None
		return json.loads(r.content)
			
	def userlog(self,inp):
		self.log('id:%s name:%s friendid:%s exp:%s lvl:%s stamina:%s/%s'%(inp['body']['player']['id'],inp['body']['player']['name'],inp['body']['player']['fuid'],inp['body']['player']['exp'],inp['body']['player']['lv'],inp['body']['player']['stamina']['pt'],inp['body']['player']['stamina']['max']))
			
	def chkver(self):
		res= self.callAPI('chkver',{"ticket":self.ticket,"param":{"ver":self.app_ver,"os":"ios"}})
		self.config=res
		return res
		
	def register(self):
		res= self.callAPI('gauth/register',{"ticket":self.ticket,"access_token":"","param":{"secret_key":self.secret_key,"udid":self.udid,"idfa":self.idfa,"idfv":self.idfv}})
		self.device_id=res['body']['device_id']
		return res

	def accesstoken(self):
		res= self.callAPI('gauth/accesstoken',{"ticket":self.ticket,"access_token":"","param":{"secret_key":self.secret_key,"device_id":self.device_id,"idfa":self.idfa,"idfv":self.idfv}})
		self.access_token=res['body']['access_token']
		return res

	def master_log(self):
		return self.callAPI('master/log',{"ticket":self.ticket})
		
	def bundle(self):
		return self.callAPI('bundle',{"ticket":self.ticket})
	
	def product(self):
		return self.callAPI('product',{"ticket":self.ticket})
	
	def login_param(self):
		return self.callAPI('login/param',{"ticket":self.ticket})
	
	def award(self):
		return self.callAPI('award',{"ticket":self.ticket})
	
	def gacha(self):
		return self.callAPI('gacha',{"ticket":self.ticket})
	
	def gacha_exec(self,gachaid,free,ticketnum=None):
		if ticketnum:
			return self.callAPI('gacha/exec',{"ticket":self.ticket,"param":{"gachaid":gachaid,"free":free,"ticketnum":ticketnum}})
		else:
			return self.callAPI('gacha/exec',{"ticket":self.ticket,"param":{"gachaid":gachaid,"free":free}})

	def chat_message(self):
		return self.callAPI('award',{"ticket":26,"param":{"start_id":0,"channel":1,"limit":30,"exclude_id":0}})

	def trophy_exec(self,work,force=False):
		done=[]
		for w in work:
			if force:
				done.append({'iname':w[0],'pts':w[1],'ymd':self.getymd(),'rewarded_at':self.getymd()})
			else:
				done.append({'iname':w[0],'pts':w[1],'ymd':self.getymd()})
		data={'ticket':self.ticket,'param':{'trophyprogs':done}}
		return self.callAPI('trophy/exec',data)
		
	def raid2(self,iname,ticket):
		return self.callAPI('btl/com/raid2',{"ticket":self.ticket,"param":{"iname":iname,"partyid":0,"ticket":ticket}})

	def btl_req(self,data):
		return self.callAPI('btl/com/req',data)

	def btl_end(self,data):
		return self.callAPI('btl/com/end',data)
		
	def getymd(self):
		return datetime.datetime.fromtimestamp(int(time.time())).strftime("%y%m%d")
		
	def bingo_exec(self,work,force=False):
		done=[]
		for w in work:
			parent=w[0].split('_')
			if force:
				if len(parent)==2:
					done.append({'iname':w[0],'parent':'','pts':w[1],'ymd':self.getymd(),'rewarded_at':self.getymd()})
				else:
					done.append({'iname':w[0],'parent':'%s_%s'%(parent[0],parent[1]),'pts':w[1],'ymd':self.getymd(),'rewarded_at':self.getymd()})
			else:
				if len(parent)==2:
					done.append({'iname':w[0],'parent':'%s_%s'%(parent[0],parent[1]),'pts':w[1],'ymd':self.getymd()})
				else:
					done.append({'iname':w[0],'parent':'%s_%s'%(parent[0],parent[1]),'pts':w[1],'ymd':self.getymd()})
		data={'ticket':self.ticket,'param':{'bingoprogs':done}}
		return self.callAPI('bingo/exec',data)
				
	def tut_update(self,tut):
		return self.callAPI('bingo/exec',{"ticket":self.ticket,"param":{"tut":tut}})

	def auth(self):
		return self.callAPI('achieve/auth',None,2)
		
	def login(self):
		return self.callAPI('login',{"ticket":self.ticket,"param":{"device":"iPhone6SPlus"}})

	def playnew(self):
		return self.callAPI('playnew',{"ticket":self.ticket,"param":{"permanent_id":self.idfa}})
	
	def setlanguage(self,lang):
		return self.callAPI('setlanguage',{"ticket":self.ticket,"param":{"lang":lang}})
	
	def getmail(self,isPeriod):
		mails=self.mail(1,isPeriod,0)
		mailids=[]
		for m in mails['body']['mails']['list']:
			mailids.append(m['mid'])
		return self.mailread(mailids,1,1)

	def mail(self,page,isPeriod,isRead):
		return self.callAPI('mail',{"ticket":self.ticket,"param":{"page":page,"isPeriod":isPeriod,"isRead":isRead}})

	def mailread(self,mailids,page,period):
		return self.callAPI('mail/read',{"ticket":self.ticket,"param":{"mailids":mailids,"page":page,"period":period}})
	
	def parseReward(self,input):
		fin=[]
		reward=input['body']['btlinfo']
		drops=reward['drops']
		for d in drops:
			if 'iname' in d:
				fin.append('%s x%s'%(d['iname'],d['num']))
		rewards=reward['rewards']
		for idx, r in enumerate(rewards):
			for i in r:
				fin.append('%s x%s'%(i,rewards[idx][i]))
		return ','.join(fin)
	
	def preparebltend(self,inp,btlid):
		mobs=[]
		beats=[]
		for i in inp['body']['btlinfo']['drops']:
			#if 'num' in i and i['num']==1:
			beats.append(1)
			#elif 'num' not in i:
			mobs.append(0)
		res={"ticket":self.ticket,"param":{"btlid":btlid,"btlendparam":{"time":0,"result":"win","beats":beats,"steals":{"items":mobs,"golds":mobs},"missions":[1,1,1],"inputs":[]},"hpleveldamage":[102,10,19]}}
		return res
	
	def resumemission(self,btlid):
		self.log('found active quest')
		res=self.callAPI('btl/com/resume',{"ticket":self.ticket,"param":{"btlid":btlid}})
		if not res:
			return
		self.log('doing %s mission'%(res['body']['btlinfo']['qid']))
		self.log('reward:\n%s'%self.parseReward(res))
		return self.btl_end(self.preparebltend(res,btlid))
	
	def doMission(self,data):
		data={"ticket":self.ticket,"param":{"iname":data,"partyid":0,"btlparam":{"help":{"fuid":""}}}}
		self.log('doing %s mission'%(data['param']['iname']))
		res=self.btl_req(data)
		if not res:
			return
		self.log('reward:\n%s'%self.parseReward(res))
		btlid=res['body']['btlid']
		return self.btl_end(self.preparebltend(res,btlid))

	def doLogin(self):
		self.chkver()
		self.accesstoken()
		self.auth()
		self.login()
		
	def doTut(self):
		self.chkver()
		self.setidfv(self.genRandomDeviceID())
		self.register()
		self.accesstoken()
		self.master_log()
		self.auth()
		self.login()
		self.playnew()
		self.setlanguage('en')
		self.bundle()
		self.product()
		self.login_param()
		self.trophy_exec([('GL_GEARTUT_01',[1]),('LOGIN_GLTUTOTIAL_01',[1])])
		self.doMission('QE_OP_0002')
		self.doMission('QE_OP_0003')
		self.doMission('QE_OP_0004')
		self.doMission('QE_OP_0006')
		self.trophy_exec([('GL_BF_DAILY_01',[1])])
		self.trophy_exec([('AWARD_RECORD_00001_00002',[1]),('AWARD_RECORD_00003_00004',[1])])
		self.tut_update(8192)
		self.award()
		self.trophy_exec([('DAILY_GLAPVIDEO_01',[1]),('DAILY_GLAPVIDEO_02',[1]),('DAILY_GLAPVIDEO_03',[1]),('DAILY_GLAPVIDEO_04',[1]),('DAILY_GLAPVIDEO_05',[1])],True)
		self.tut_update(2)
		self.tut_update(8194)
		self.trophy_exec([('LOGIN_GLTUTOTIAL_01',[1])])
		self.gacha()
		self.log(self.gacha_exec('Rare_Gacha_ii',1))
		self.trophy_exec([('DAILY_GL2017OCT_2_12',[1])])
		self.bingo_exec([('CHALLENGE_01_01',[1])],True)
		self.gacha()
		self.tut_update(258)
		self.tut_update(322)
		self.tut_update(450)
		self.tut_update(482)
		self.tut_update(2530)
		self.tut_update(2538)
		self.doMission('QE_ST_NO_010001')
		self.tut_update(2539)
		self.award()
		self.getmail(1)
		self.tut_update(8195)
		self.award()
		self.log('tut done')
		
if __name__ == "__main__":
	a=API()
	a.doTut()