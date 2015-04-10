import os
import shutil
from core.generictask import GenericTask
from core.tasksmanager import TasksManager
from lib.images import Images
from lib import util


__author__ = 'cbedetti'

class QA(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(self, subject)
        self.setCleanupBeforeImplement(False)
        self.__subject = subject


    def implement(self):
        if not os.path.exists('img'):
            os.makedirs('img')

        shutil.copyfile(os.path.join(self.toadDir, 'templates/files/logo.png'), 'img/logo.png')

        menuHtml = ""
        qaTasksList = []
        taskManager = TasksManager(self.__subject)
        for task in taskManager.getQaTasks():
            name = task.getName()
            qaTasksList.append(name)
            menuHtml +="\n<li><a id=\"{0}\" href=\"{0}.html\">{0}</a></li>".format(name)

	message = "Task is running on the server. Refresh to check if QA is over"
	for name in qaTasksList:
            htmlTaskFileName = "{}.html".format(name)
            if not os.path.exists(htmlTaskFileName):
                htmlCode = self.parseTemplate({'parseHtmlTables':message, 'menuHtml':menuHtml}, os.path.join(self.toadDir, 'templates/files/qa.main.tpl'))
                util.createScript(htmlTaskFileName, htmlCode)
        
        htmlCode = self.parseTemplate({'menuHtml':menuHtml}, os.path.join(self.toadDir, 'templates/files/qa.main.tpl'))
        util.createScript('qa.main.tpl', htmlCode)

        htmlCode = self.parseTemplate({'parseHtmlTables':'', 'menuHtml':menuHtml}, os.path.join(self.toadDir, 'templates/files/qa.main.tpl'))
        util.createScript('index.html', htmlCode)


    def meetRequirement(self, result=True):
        """
        
        """
        return result


    def isDirty(self):
        """Validate if this tasks need to be submit for implementation

        """
        return Images((os.path.join(self.workingDir, 'index.html'), 'QA index.html')).isSomeImagesMissing()