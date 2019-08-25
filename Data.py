class Data:
    def __init__(self):
        self.photoDS = {}
        self.nameList = []
        self.inputing = False
        self.PoPoPositionDS = {}
        self.positionList = []
        self.clientList = {}

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
                self.positionList.append(position)
                self.clientList[str(chatId)]['position'] = position
                return True
        else:
            print("not in clientList")
            return False

    def addPoPoNumber(self, chatId, number):
        print("clientList: ", self.clientList)
        self.PoPoPositionDS[self.clientList[str(chatId)]['position']] = number
        self.clientList[str(chatId)]['status'][2] = True
