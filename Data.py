class Data:
    def __init__(self):
        self.photoDS = {}
        self.nameList = []
        self.inputing = False
        self.PoPoPositionDS = {}
        self.positionList = []
        self.clientList = {}
        self.memberList = {}
        self.admin = ""
        self.hackerList = {}

    def addPhoto(self, photo, name):
        if str(name) in self.photoDS:
            print(name in self.photoDS)
            self.photoDS[name].append(photo)
        else:
            self.photoDS[name].append(photo)

    def addTarget(self, name):
        if not (name in self.nameList):
            self.nameList.append(name)
            self.photoDS[name] = []

    def prepareForInput(self):
        if not self.inputing:
            self.clientList[chatId] = [False,True, True]

    def inputFinished(self, chatId):
        if self.inputing:
            self.clientList[chatId] = [False,False,True]

    def getName(self):
        if len(self.nameList) == 0:
            return "No current Target"
        else:
            return self.nameList[-1]

    def reportPopo(self, chatId):
        # x = {str(chatId) : {'status': (True,False,False), 'position': ""}}
        self.clientList[str(chatId)] = {'status': [True,False,True], 'position': ""}
        print("clientList: ",self.clientList)

    def addPoPoposition(self, chatId, position):
        if str(chatId) in self.clientList:
            if self.clientList[str(chatId)]['status'][0]:
                if not self.clientList[str(chatId)]['status'][2]:
                    return False
                self.clientList[str(chatId)]['status'][2] = False
                print("clientList: ",self.clientList)
                print("positionList", self.positionList)
                if not position in self.positionList:
                    self.positionList.append(position)
                self.clientList[str(chatId)]['position'] = position
                return True
        else:
            print("not in clientList")
            return False

    def addPoPoNumber(self, chatId, number):
        print("clientList: ", self.clientList)
        if (not self.clientList[str(chatId)]['position'] in self.PoPoPositionDS):
            self.PoPoPositionDS[self.clientList[str(chatId)]['position']] = int(number)
        else:
            if(self.PoPoPositionDS[self.clientList[str(chatId)]['position']] != 0):
                print(self.PoPoPositionDS[self.clientList[str(chatId)]['position']])
                self.PoPoPositionDS[self.clientList[str(chatId)]['position']] = int((int(self.PoPoPositionDS[self.clientList[str(chatId)]['position']]) + int(number))/2)
        self.clientList[str(chatId)]['status'][2] = True

    def haveMember(self, chatId):
        return chatId in self.memberList
    def addMember(self, chatId, name):
        print("add Member")
        if (not chatId in self.memberList):
            self.memberList[chatId] = {lastUpdateTime: "", name: name}

    def updateLastUpdateTime(self, chatId, time):
        if (chatId in self.memberList):
            self.memberList[chatId]["lastUpdateTime"] = time

    def updateName(self, chatId, name):
        for member in self.memberList:
            if name == member.name:
                self.memberList[chatId] = { lastUpdateTime: self.memberList[member], name: name}
                self.memberList.pop(member,None)

    def setAdmin(self, chatId):
        if self.admin == None:
            self.admin = chatId

    def updateAdmin(self, chatId, password, contact={}):
        if password == os.environ.get('admin_secret'):
            self.admin = chatId
            return True
        else:
            self.hackerList[chatId] = contact
            return False
